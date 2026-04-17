import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
from pushbullet import Pushbullet

# --- KONFIGURÁCIA ---
DB_FILE = "kalendar_kapely.json"
PB_API_KEY = "o.Ir4LWAKm78pwEhpKkAf6WZY9uZPNCkSm"
LOGIN_MENO = "ovcanskeparobci"
LOGIN_HESLO = "OvcanskeParobci123"

# Priamy link na fotku (použijeme ten, čo si poslal, ale cez pozadie)
KAPELA_FOTO_URL = "https://i.ibb.co/KzBTbwLR/image-2ec9e6.jpg" 

# --- BRUTÁLNY DIZAJN (CSS NA POZADIE) ---
def apply_style():
    st.markdown(f"""
        <style>
        /* Nastavenie celoobrazovkového pozadia */
        .stApp {{
            background: linear-gradient(rgba(0, 0, 0, 0.7), rgba(0, 0, 0, 0.7)), 
                        url("{KAPELA_FOTO_URL}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
            color: #ffffff;
        }}
        
        /* Transparentný bočný panel */
        [data-testid="stSidebar"] {{
            background-color: rgba(22, 27, 34, 0.8) !important;
            backdrop-filter: blur(10px);
            border-right: 1px solid #d4af37;
        }}
        
        /* Nadpisy so zlatým nádychom */
        h1, h2, h3 {{ 
            color: #d4af37 !important; 
            font-family: 'Playfair Display', serif; 
            text-shadow: 2px 2px 4px #000000;
        }}

        /* Biele karty pre formuláre aby boli čitateľné */
        .stForm {{
            background-color: rgba(0, 0, 0, 0.6) !important;
            border: 1px solid #d4af37 !important;
            border-radius: 15px;
            padding: 30px;
            backdrop-filter: blur(5px);
        }}

        /* Tlačidlá */
        .stButton>button {{ 
            background-color: #d4af37 !important; 
            color: black !important; 
            border-radius: 10px !important; 
            font-weight: bold !important;
            height: 3em;
            border: none !important;
        }}
        
        /* Päta */
        .footer-text {{ 
            text-align: center; 
            color: #ccc; 
            font-size: 0.9rem; 
            margin-top: 50px; 
            padding: 20px; 
            background: rgba(0,0,0,0.5);
            border-radius: 10px;
        }}
        </style>
    """, unsafe_allow_html=True)

# --- FUNKCIE PRE DÁTA ---
def nacti_data():
    if not os.path.exists(DB_FILE): return []
    try:
        with open(DB_FILE, "r") as f: return json.load(f)
    except: return []

def uloz_data(data):
    with open(DB_FILE, "w") as f: json.dump(data, f, indent=4)

def posli_upozornenie(text):
    try:
        pb = Pushbullet(PB_API_KEY)
        pb.push_note("🎸 OVČANSKE PAROBCI", text)
        return True
    except: return False

def footer():
    st.markdown(f"""
        <div class="footer-text">
            <b>Technická podpora:</b> 📞 0944 757 122 | ✉️ kollarstevo55@gmail.com
        </div>
    """, unsafe_allow_html=True)

# --- KONFIGURÁCIA STRÁNKY ---
st.set_page_config(page_title="Ovčanske Parobci", page_icon="🎻", layout="centered")
apply_style()

# --- SIDEBAR ---
st.sidebar.markdown("<h2 style='text-align: center;'>OVČANSKE PAROBCI</h2>", unsafe_allow_html=True)
menu_moznost = st.sidebar.radio("NAVIGÁCIA", ["🎸 Rezervácia vystúpenia", "🔐 Administrácia"])

# --- 1. VEREJNÁ ČASŤ ---
if menu_moznost == "🎸 Rezervácia vystúpenia":
    st.title("🎻 Ovčanske Parobci")
    st.markdown("<h4 style='text-align: center;'>Tradičná hudba pre vašu nezabudnuteľnú udalosť</h4>", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    with st.form("form_rezervacia"):
        st.subheader("📩 Rezervačný dopyt")
        col1, col2 = st.columns(2)
        with col1:
            d = st.date_input("Dátum akcie", min_value=datetime.now())
        with col2:
            c = st.time_input("Čas začiatku")
        
        m = st.text_input("Vaše meno a telefónne číslo")
        p = st.text_area("Detaily akcie (miesto, typ oslavy...)")
        
        submit = st.form_submit_button("ODOSLAŤ REZERVÁCIU")
        
        if submit:
            data = nacti_data()
            if any(a['datum'] == str(d) for a in data):
                st.error("Tento termín už máme bohužiaľ obsadený.")
            elif not m:
                st.warning("Prosím, uveďte kontakt.")
            else:
                if posli_upozornenie(f"DOPYT!\nDátum: {d}\nKontakt: {m}\nInfo: {p}"):
                    st.balloons()
                    st.success("Vaša správa bola odoslaná! Ozveme sa vám. ✅")

# --- 2. ADMIN ČASŤ ---
else:
    st.title("🔐 Správa systému")
    if 'auth' not in st.session_state: st.session_state['auth'] = False

    if not st.session_state['auth']:
        with st.form("login"):
            st.write("Vstup pre kapelu")
            u = st.text_input("Meno")
            h = st.text_input("Heslo", type="password")
            if st.form_submit_button("PRIHLÁSIŤ SA"):
                if u == LOGIN_MENO and h == LOGIN_HESLO:
                    st.session_state['auth'] = True
                    st.rerun()
                else: st.error("Chyba!")
    else:
        if st.sidebar.button("ODHLÁSIŤ SA"):
            st.session_state['auth'] = False
            st.rerun()

        t1, t2 = st.tabs(["➕ Pridať termín", "📅 Zoznam akcií"])
        
        with t1:
            with st.form("add"):
                d_in = st.date_input("Dátum")
                c_in = st.time_input("Čas")
                p_in = st.text_input("Miesto/Názov")
                if st.form_submit_button("ULOŽIŤ"):
                    data = nacti_data()
                    data.append({"id": str(datetime.now().timestamp()), "datum": str(d_in), "cas": str(c_in), "poznamka": p_in})
                    uloz_data(data)
                    st.success("Zapísané!")

        with t2:
            data = nacti_data()
            if data:
                data.sort(key=lambda x: x['datum'])
                for idx, a in enumerate(data):
                    with st.expander(f"📅 {a['datum']} - {a['poznamka']}"):
                        # Tu sú tie úpravy
                        nd = st.date_input("Dátum", value=datetime.strptime(a['datum'], '%Y-%m-%d'), key=f"d{idx}")
                        nc = st.text_input("Čas", value=a['cas'], key=f"c{idx}")
                        np = st.text_input("Miesto", value=a['poznamka'], key=f"p{idx}")
                        
                        c1, c2 = st.columns(2)
                        with c1:
                            if st.button("Uložiť", key=f"s{idx}"):
                                data[idx] = {"id": a['id'], "datum": str(nd), "cas": nc, "poznamka": np}
                                uloz_data(data); st.rerun()
                        with c2:
                            if st.button("Zmazať", key=f"r{idx}"):
                                data.pop(idx); uloz_data(data); st.rerun()
            else:
                st.write("Prázdno.")

footer()
