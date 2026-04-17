import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, timedelta
from pushbullet import Pushbullet

# --- NASTAVENIA ---
DB_FILE = "kalendar_kapely.json"
PB_API_KEY = "o.Ir4LWAKm78pwEhpKkAf6WZY9uZPNCkSm"

def posli_upozornenie(text):
    try:
        pb = Pushbullet(PB_API_KEY)
        pb.push_note("🎸 OVČANSKE PAROBCI: Nový dopyt!", text)
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
st.set_page_config(page_title="Ovčanske Parobci", page_icon="🎸")

# --- SIDEBAR MENU ---
st.sidebar.title("Ovčanske Parobci")
menu = ["🎸 Rezervácia (pre verejnosť)", "🔐 Správa kapely"]
choice = st.sidebar.selectbox("Kam chcete ísť?", menu)

# --- 1. VEREJNÁ ČASŤ: REZERVÁCIA ---
if choice == "🎸 Rezervácia (pre verejnosť)":
    st.header("Chcete, aby sme vám zahrali?")
    st.write("Vyberte si termín vašej oslavy alebo svadby a my sa vám ozveme!")
    
    data = nacti_data()
    obsadene_datumy = [akcia['datum'] for akcia in data]

    with st.form("verejna_rezervacia"):
        datum = st.date_input("Dátum vašej akcie", min_value=datetime.now())
        cas = st.time_input("Približný čas začiatku")
        meno = st.text_input("Vaše meno a telefónne číslo")
        poznamka = st.text_area("O akú akciu ide? (napr. 50-tka v Krompachoch)")
        
        submitted = st.form_submit_button("Odoslať nezáväzný dopyt")
        
        if submitted:
            datum_str = str(datum)
            if datum_str in obsadene_datumy:
                st.error(f"Prepáčte, ale termín {datum_str} už máme obsadený inou akciou. 😔")
            elif not meno or not poznamka:
                st.warning("Prosím, vyplňte meno a detaily akcie.")
            else:
                # Odošle notifikáciu členom kapely
                msg = f"Nová žiadosť! \nKedy: {datum_str} o {cas}\nKto: {meno}\nČo: {poznamka}"
                if posli_upozornenie(msg):
                    st.success("Vaša požiadavka bola odoslaná! Kapela vás bude čoskoro kontaktovať. ✅")
                    # Voliteľne: Môžeš to automaticky pridať do JSONu ako "ČAKAJÚCE"
                    # Ak to chceš, stačí tu dopísať kód na uloženie do databázy.

# --- 2. ADMIN ČASŤ: SPRÁVA KAPELY ---
elif choice == "🔐 Správa kapely":
    # Tu môžeš pridať jednoduché heslo, ak chceš
    st.title("Administrácia")
    
    st.sidebar.header("Diagnostika")
    if st.sidebar.button("🚀 OTESTOVAŤ SPOJENIE"):
        if posli_upozornenie("Testovacia správa! Spojenie funguje. ✅"):
            st.sidebar.success("Píplo to!")

    sub_menu = ["Pridať akciu", "Zoznam akcií"]
    sub_choice = st.selectbox("Vyberte akciu", sub_menu)

    if sub_choice == "Pridať akciu":
        st.subheader("Zapíš nový termín (Potvrdený)")
        with st.form("nova_akcia_form"):
            datum = st.date_input("Dátum akcie", min_value=datetime.now())
            cas = st.time_input("Čas")
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
                    st.success(f"Akcia uložená!")

    elif sub_choice == "Zoznam akcií":
        st.subheader("Plánované akcie")
        data = nacti_data()
        if data:
            for idx, akcia in enumerate(data):
                with st.expander(f"📅 {akcia['datum']} - {akcia['poznamka']}"):
                    st.write(f"**Čas:** {akcia['cas']}")
                    if st.button(f"🔔 Poslať pripomienku hneď", key=f"send_{idx}"):
                        posli_upozornenie(f"PRIPOMIENKA: {akcia['poznamka']} dňa {akcia['datum']}!")
        else:
            st.info("Žiadne plánované akcie.")

# --- AUTOMATICKÁ KONTROLA TERMÍNOV (beží na pozadí) ---
# ... (tvoj pôvodný kód pre automatiku) ...
data = nacti_data()
dnes = datetime.now().date()
zmena = False
terminy = {"notif_mesiac": 30, "notif_2tyzdne": 14, "notif_1tyzden": 7}

for akcia in data:
    try:
        termin_akcie = datetime.strptime(akcia["datum"], "%Y-%m-%d").date()
        rozdiel = (termin_akcie - dnes).days
        for kluc, dni in terminy.items():
            if rozdiel == dni and not akcia.get(kluc, False):
                if posli_upozornenie(f"AUTOMATIKA: {akcia['poznamka']} o {dni} dní!"):
                    akcia[kluc] = True
                    zmena = True
    except:
        continue
if zmena:
    uloz_data(data)
