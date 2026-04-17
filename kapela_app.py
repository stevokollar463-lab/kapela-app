import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
from pushbullet import Pushbullet

# --- KONFIGURÁCIA ---
DB_FILE = "kalendar_kapely.json"
PB_API_KEY = "o.Ir4LWAKm78pwEhpKkAf6WZY9uZPNCkSm"

# Prihlasovacie údaje, ktoré si chcel
LOGIN_MENO = "ovcanskeparobci"
LOGIN_HESLO = "OvcanskeParobci123"

def posli_upozornenie(text):
    try:
        pb = Pushbullet(PB_API_KEY)
        pb.push_note("🎸 KAPELA NOTIFIKÁCIA", text)
        return True
    except:
        return False

if not os.path.exists(DB_FILE):
    with open(DB_FILE, "w") as f:
        json.dump([], f)

def nacti_data():
    try:
        with open(DB_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def uloz_data(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

# --- UI NASTAVENIA ---
st.set_page_config(page_title="Ovčanske Parobci", page_icon="🎸")

# Menu vľavo
st.sidebar.title("MENU")
menu_moznost = st.sidebar.radio("Vyberte si:", ["🎸 Rezervácia pre verejnosť", "🔐 Správa kapely"])

# --- 1. VEREJNÁ ČASŤ ---
if menu_moznost == "🎸 Rezervácia pre verejnosť":
    st.title("🎸 Rezervujte si Ovčanských Parobkov!")
    st.write("Vyplňte formulár a my sa vám ozveme, či máme voľno.")
    
    st.divider()
    
    with st.form("form_rezervacia"):
        datum = st.date_input("Dátum akcie", min_value=datetime.now())
        cas = st.time_input("Približný čas (odkedy hráme)")
        meno = st.text_input("Vaše meno a kontakt (mobil/email)")
        poznamka = st.text_area("O akú akciu ide? (napr. Svadba, 50-tka, Krstiny...)")
        
        odoslat = st.form_submit_button("ODOSLAŤ DOPYT")
        
        if odoslat:
            data = nacti_data()
            obsadene = [a['datum'] for a in data]
            
            if str(datum) in obsadene:
                st.error(f"Prepáčte, termín {datum} už máme obsadený.")
            elif not meno:
                st.warning("Zadajte prosím svoje meno a kontakt.")
            else:
                msg = f"NOVÁ REZERVÁCIA!\nKedy: {datum} o {cas}\nKto: {meno}\nČo: {poznamka}"
                if posli_upozornenie(msg):
                    st.success("Dopyt bol odoslaný! Ozveme sa vám. ✅")
                else:
                    st.error("Chyba pri odosielaní správy kapele.")

# --- 2. ADMIN ČASŤ (LOGIN) ---
else:
    st.title("🔐 Sekcia pre členov")

    # Kontrola prihlásenia v pamäti prehliadača
    if 'auth' not in st.session_state:
        st.session_state['auth'] = False

    if not st.session_state['auth']:
        # TU SÚ TIE POLÍČKA, KTORÉ HĽADÁŠ
        st.info("Pre vstup do správy sa musíte prihlásiť.")
        vstup_meno = st.text_input("Užívateľské meno")
        vstup_heslo = st.text_input("Heslo", type="password")
        
        if st.button("Prihlásiť sa"):
            if vstup_meno == LOGIN_MENO and vstup_heslo == LOGIN_HESLO:
                st.session_state['auth'] = True
                st.rerun()
            else:
                st.error("Nesprávne meno alebo heslo!")
    else:
        # TOTO UVIDÍŠ AŽ KEĎ SA PRIHLÁSIŠ
        st.sidebar.success("Ste prihlásený")
        if st.sidebar.button("Odhlásiť sa"):
            st.session_state['auth'] = False
            st.rerun()

        st.subheader("Administrácia akcií")
        
        tab1, tab2 = st.tabs(["Pridať novú akciu", "Zoznam všetkých akcií"])
        
        with tab1:
            with st.form("admin_add"):
                d = st.date_input("Dátum")
                c = st.time_input("Čas")
                p = st.text_input("Miesto / Názov")
                submit = st.form_submit_button("ULOŽIŤ AKCIU")
                
                if submit:
                    data = nacti_data()
                    nova = {"datum": str(d), "cas": str(c), "poznamka": p}
                    data.append(nova)
                    uloz_data(data)
                    st.success("Akcia uložená do kalendára!")

        with tab2:
            data = nacti_data()
            if data:
                for idx, akcia in enumerate(data):
                    st.write(f"📅 **{akcia['datum']}** - {akcia['poznamka']} ({akcia['cas']})")
                
                st.divider()
                if st.button("🗑️ VYMAZAŤ VŠETKO"):
                    uloz_data([])
                    st.rerun()
            else:
                st.write("Zatiaľ nemáte žiadne akcie.")
