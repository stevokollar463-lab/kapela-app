import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, timedelta
from pushbullet import Pushbullet

# --- NASTAVENIA ---
DB_FILE = "kalendar_kapely.json"
# Tvoj kapelový token
PB_API_KEY = "o.Ir4LWAKm78pwEhpKkAf6WZY9uZPNCkSm"

def posli_upozornenie(text):
    try:
        pb = Pushbullet(PB_API_KEY)
        pb.push_note("🎸 KAPELA: Pripomienka", text)
        return True
    except Exception as e:
        st.error(f"Chyba pri odosielaní: {e}")
        return False

# Inicializácia databázy
if not os.path.exists(DB_FILE):
    with open(DB_FILE, "w") as f:
        json.dump([], f)

def nacti_data():
    with open(DB_FILE, "r") as f:
        return json.load(f)

def uloz_data(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

# --- GRAFICKÉ ROZHRANIE (UI) ---
st.set_page_config(page_title="Manažér Kapely", page_icon="🎸")
st.title("🎸 Kapelný Kalendár")

# --- DIAGNOSTIKA V SIDEBARE ---
st.sidebar.header("Diagnostika")
if st.sidebar.button("🚀 OTESTOVAŤ SPOJENIE"):
    if posli_upozornenie("Testovacia správa! Spojenie funguje. ✅"):
        st.sidebar.success("Píplo to!")

menu = ["Pridať akciu", "Zoznam akcií"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "Pridať akciu":
    st.subheader("Zapíš nový termín")
    with st.form("nova_akcia_form"):
        datum = st.date_input("Dátum akcie", min_value=datetime.now())
        cas = st.time_input("Čas (voliteľné)")
        poznamka = st.text_input("Názov akcie / Miesto")
        submitted = st.form_submit_button("Uložiť do kalendára")
        
        if submitted:
            if not poznamka:
                st.error("Doplň názov akcie.")
            else:
                data = nacti_data()
                nova_akcia = {
                    "id": str(datetime.now().timestamp()),
                    "datum": str(datum),
                    "cas": str(cas),
                    "poznamka": poznamka,
                    "notif_mesiac": False,
                    "notif_2tyzdne": False,
                    "notif_1tyzden": False
                }
                data.append(nova_akcia)
                uloz_data(data)
                st.success(f"Uložené! Automatika nastavená (30, 14 a 7 dní pred).")

elif choice == "Zoznam akcií":
    st.subheader("Plánované akcie a manuálne odosielanie")
    data = nacti_data()
    
    if data:
        for idx, akcia in enumerate(data):
            with st.expander(f"📅 {akcia['datum']} - {akcia['poznamka']}"):
                col1, col2 = st.columns([3, 2])
                with col1:
                    st.write(f"**Čas:** {akcia['cas']}")
                    st.write(f"**Status:** M:{akcia['notif_mesiac']} | 2T:{akcia['notif_2tyzdne']} | 1T:{akcia['notif_1tyzden']}")
                
                with col2:
                    # TLAČIDLO POSLAŤ TERAZ
                    if st.button(f"🔔 Poslať teraz", key=f"send_{idx}"):
                        text_spravy = f"MANUÁLNA PRIPOMIENKA: {akcia['poznamka']} dňa {akcia['datum']} o {akcia['cas']}!"
                        if posli_upozornenie(text_spravy):
                            st.success("Odoslané!")

        if st.button("🗑️ Vymazať celú databázu"):
            uloz_data([])
            st.rerun()
    else:
        st.info("Zatiaľ žiadne akcie.")

# --- AUTOMATICKÁ KONTROLA TERMÍNOV ---
data = nacti_data()
dnes = datetime.now().date()
zmena = False

terminy = {
    "notif_mesiac": 30,
    "notif_2tyzdne": 14,
    "notif_1tyzden": 7
}

for akcia in data:
    try:
        termin_akcie = datetime.strptime(akcia["datum"], "%Y-%m-%d").date()
        rozdiel = (termin_akcie - dnes).days
        
        for kluc, dni in terminy.items():
            if rozdiel == dni and not akcia.get(kluc, False):
                cas_popis = "o mesiac" if dni == 30 else (f"o {dni} dní")
                msg = f"AUTOMATIKA: {akcia['poznamka']} už {cas_popis}! ({akcia['datum']})"
                
                if posli_upozornenie(msg):
                    akcia[kluc] = True
                    zmena = True
                    st.toast(f"Odoslané auto-upozornenie ({dni} dní)")
    except:
        continue

if zmena:
    uloz_data(data)