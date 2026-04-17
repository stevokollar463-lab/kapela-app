import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
from pushbullet import Pushbullet

# --- KONFIGURÁCIA ---
DB_FILE = "kalendar_kapely.json"
PB_API_KEY = "o.Ir4LW4Km78pwEhpKkAf6WZY9uZPNCkSm"
LOGIN_MENO = "ovcanskeparobci"
LOGIN_HESLO = "OvcanskeParobci123"

# Odkaz na vašu fotku (vymeň URL za link na vašu reálnu fotku, ak máš)
HEADER_IMAGE = "https://images.unsplash.com/photo-1514525253361-bee8718a74a2?q=80&w=1000&auto=format&fit=crop"

# --- BRUTÁLNY DIZAJN (CSS) ---
def apply_style():
    st.markdown(f"""
        <style>
        /* Hlavné pozadie */
        .stApp {{
            background-color: #0e1117;
            color: #ffffff;
        }}
        
        /* Úprava bočného panelu */
        [data-testid="stSidebar"] {{
            background-color: #161b22;
            border-right: 2px solid #d4af37;
        }}
        
        /* Nadpisy */
        h1, h2, h3 {{
            color: #d4af37 !important;
            font-family: 'Playfair Display', serif;
            text-transform: uppercase;
            letter-spacing: 2px;
        }}
        
        /* Tlačidlá */
        .stButton>button {{
            background-color: #d4af37 !important;
            color: black !important;
            border-radius: 20px !important;
            border: none !important;
            font-weight: bold !important;
            width: 100%;
            transition: 0.3s;
        }}
        
        .stButton>button:hover {{
            transform: scale(1.02);
            box-shadow: 0px 0px 15px #d4af37;
        }}
        
        /* Formuláre */
        .stForm {{
            border: 1px solid #d4af37 !important;
            padding: 20px;
            border-radius: 15px;
            background-color: #1c2128;
        }}
        
        /* Skrytie Streamlit menu */
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        </style>
    """, unsafe_allow_html=True)

# --- FUNKCIE ---
def posli_upozornenie(text):
    try:
        pb = Pushbullet(PB_API_KEY)
        pb.push_note("🎸 OVČANSKE PAROBCI", text)
        return True
    except: return False

def nacti_data():
    if not os.path.exists(DB_FILE): return []
    try:
        with open(DB_FILE, "r") as f: return json.load(f)
    except: return []

def uloz_data(data):
    with open(DB_FILE, "w") as f: json.dump(data, f, indent=4)

# --- SPRIESTORNENIE ---
st.set_page_config(page_title="Ovčanske Parobci | Rezervácie", page_icon="🎸", layout="centered")
apply_style()

# --- SIDEBAR ---
st.sidebar.image(HEADER_IMAGE, use_container_width=True)
st.sidebar.markdown("<h2 style='text-align: center;'>MENU</h2>", unsafe_allow_html=True)
menu_moznost = st.sidebar.radio("", ["🎸 Chceme vás na akciu", "🔐 Vstup pre kapelu"])

# --- 1. VEREJNÁ ČASŤ (DIZAJNOVÁ) ---
if menu_moznost == "🎸 Chceme vás na akciu":
    # Veľký nadpis s fotkou
    st.image(HEADER_IMAGE, caption="Ovčanske Parobci v akcii", use_container_width=True)
    st.title("🎻 Ovčanske Parobci")
    st.markdown("### Rezervujte si najlepšiu zábavu pre vašu oslavu!")
    st.write("Sme pripravení rozprúdiť krv v žilách na vašej svadbe, 50-tke či firemnej párty.")
    
    st.divider()
    
    col1, col2 = st.columns([1, 1])
    with col1:
        st.info("✅ Profesionálny prístup")
        st.info("✅ Široký repertoár")
    with col2:
        st.info("✅ Vlastná aparatúra")
        st.info("✅ Zábava do rána")

    st.markdown("---")
    st.subheader("📩 Napíšte nám termín")
    
    with st.form("form_rezervacia"):
        d = st.date_input("Kedy sa bude žúrovať?", min_value=datetime.now())
        c = st.time_input("Odkedy máme začať?")
        m = st.text_input("Vaše meno a telefón")
        p = st.text_area("Povedzte nám o akcii viac (miesto, počet ľudí...)")
        
        submit = st.form_submit_button("ODOSLAŤ REZERVÁCIU")
        
        if submit:
            data = nacti_data()
            if any(a['datum'] == str(d) for a in data):
                st.error(f"Tento termín ({d}) je už bohužiaľ obsadený. Skúste iný!")
            elif not m:
                st.warning("Napíšte nám aspoň vaše meno a číslo.")
            else:
                msg = f"Nová rezervácia!\nDátum: {d}\nČas: {c}\nKontakt: {m}\nInfo: {p}"
                if posli_upozornenie(msg):
                    st.balloons()
                    st.success("Hotovo! Správa nám práve prišla do mobilu. Ozveme sa vám! ✅")

# --- 2. ADMIN ČASŤ ---
else:
    st.title("🔐 Administrácia")
    
    if 'auth' not in st.session_state: st.session_state['auth'] = False

    if not st.session_state['auth']:
        v_meno = st.text_input("Užívateľ")
        v_heslo = st.text_input("Heslo", type="password")
        if st.button("VSTÚPIŤ"):
            if v_meno == LOGIN_MENO and v_heslo == LOGIN_HESLO:
                st.session_state['auth'] = True
                st.rerun()
            else: st.error("Prístup zamietnutý!")
    else:
        st.success("Vitajte, Parobci!")
        if st.sidebar.button("ODHLÁSIŤ SA"):
            st.session_state['auth'] = False
            st.rerun()

        t1, t2 = st.tabs(["➕ Pridať akciu", "📅 Plán akcií"])
        
        with t1:
            with st.form("add"):
                d = st.date_input("Dátum")
                c = st.time_input("Čas")
                p = st.text_input("Názov/Miesto")
                if st.form_submit_button("ULOŽIŤ"):
                    data = nacti_data()
                    data.append({"datum": str(d), "cas": str(c), "poznamka": p})
                    uloz_data(data)
                    st.success("Uložené!")

        with t2:
            data = nacti_data()
            for a in data:
                st.write(f"🟡 **{a['datum']}** - {a['poznamka']}")
            if st.button("VYMAZAŤ VŠETKO"):
                uloz_data([])
                st.rerun()
