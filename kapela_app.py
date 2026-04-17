import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, date
from pushbullet import Pushbullet

# --- KONFIGURÁCIA ---
DB_FILE = "kalendar_kapely.json"
PB_API_KEY = "o.Ir4LWAKm78pwEhpKkAf6WZY9uZPNCkSm"
LOGIN_MENO = "ovcanskeparobci"
LOGIN_HESLO = "OvcanskeParobci123"

# HLAVNÁ FOTKA
KAPELA_FOTO_URL = "https://i.postimg.cc/T1Pkgjnw/1000027016.jpg" 

# --- DIZAJN ---
def apply_style():
    st.markdown(f"""
        <style>
        .stApp {{
            background: linear-gradient(rgba(0, 0, 0, 0.7), rgba(0, 0, 0, 0.7)), 
                        url("{KAPELA_FOTO_URL}");
            background-size: cover;
            background-position: left center;
            background-attachment: fixed;
            color: #ffffff;
        }}
        [data-testid="stSidebar"] {{ background-color: rgba(20, 20, 20, 0.85) !important; backdrop-filter: blur(12px); border-right: 1px solid #d4af37; }}
        h1, h2, h3, h4 {{ color: #d4af37 !important; font-family: 'Playfair Display', serif; text-shadow: 4px 4px 8px #000000; text-align: center; }}
        .stForm {{ background-color: rgba(0, 0, 0, 0.8) !important; border: 2px solid #d4af37 !important; border-radius: 20px; padding: 30px; }}
        .stButton>button {{ background-color: #d4af37 !important; color: black !important; border-radius: 12px !important; font-weight: bold !important; width: 100%; transition: 0.3s; }}
        .stButton>button:hover {{ transform: scale(1.02); box-shadow: 0px 0px 20px #d4af37; }}
        
        /* Box pre odpočítavanie */
        .countdown-box {{
            background: rgba(212, 175, 55, 0.2);
            border: 1px solid #d4af37;
            padding: 15px;
            border-radius: 15px;
            text-align: center;
            margin-bottom: 25px;
        }}
        </style>
    """, unsafe_allow_html=True)

# --- FUNKCIE ---
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
        pb.push_note("🎸 NOVÝ DOPYT", text)
        return True
    except: return False

# --- ŠTART APP ---
st.set_page_config(page_title="Ovčanske Parobci", page_icon="🎻", layout="centered")
apply_style()

st.sidebar.markdown("## PAROBCI")
menu = st.sidebar.radio("NAVIGÁCIA", ["🎸 Rezervácia", "📸 Galéria", "🔐 Administrácia"])

db = nacti_data()

# --- ODPOČÍTAVANIE DO NAJBLIŽŠIEHO HRANIA ---
def render_countdown():
    buduce = [a for a in db if (a.get("stav") == "schvalene" or "stav" not in a) and datetime.strptime(a['datum'], '%Y-%m-%d').date() >= date.today()]
    if buduce:
        buduce.sort(key=lambda x: x['datum'])
        najblizsia = buduce[0]
        d_format = datetime.strptime(najblizsia['datum'], '%Y-%m-%d').date()
        dni = (d_format - date.today()).days
        
        if dni == 0:
            msg = "DNES HRÁME! 🎻🔥"
        elif dni == 1:
            msg = "Zajtra hráme: " + najblizsia['poznamka']
        else:
            msg = f"Najbližšie hráme o {dni} dní ({najblizsia['poznamka']})"
        
        st.markdown(f'<div class="countdown-box"><h3 style="margin:0; font-size:1.2rem;">{msg}</h3></div>', unsafe_allow_html=True)

# --- 1. REZERVÁCIA ---
if menu == "🎸 Rezervácia":
    render_countdown()
    st.title("🎻 Ovčanske Parobci")
    st.markdown("#### Poriadna ľudová muzika na vašu akciu")
    
    with st.form("main_booking"):
        st.subheader("📩 Rezervačný dopyt")
        col1, col2 = st.columns(2)
        with col1: datum = st.date_input("Dátum akcie", min_value=datetime.now())
        with col2: cas = st.time_input("Čas začiatku")
        meno = st.text_input("Meno a telefón")
        detaily = st.text_area("Detaily (miesto, typ akcie...)")
        
        if st.form_submit_button("ODOSLAŤ REZERVÁCIU"):
            nova = {"id": str(datetime.now().timestamp()), "datum": str(datum), "cas": str(cas), "poznamka": f"{meno} | {detaily}", "stav": "cakajuce"}
            db.append(nova); uloz_data(db)
            posli_upozornenie(f"Dopyt: {datum} od {meno}")
            st.balloons(); st.success("Odoslané! Ozveme sa vám. ✅")

# --- 2. GALÉRIA ---
elif menu == "📸 Galéria":
    st.title("📸 Naša Zábava")
    st.write("Pozrite si, ako to vyzerá, keď to Ovčanske Parobci rozbalia!")
    
    # Tu môžeš pridať linky na ďalšie fotky z akcií
    fotky = [
        KAPELA_FOTO_URL, # Tu daj iné linky ak máš
        "https://i.postimg.cc/T1Pkgjnw/1000027016.jpg" 
    ]
    
    col1, col2 = st.columns(2)
    for i, foto in enumerate(fotky):
        if i % 2 == 0: col1.image(foto, use_container_width=True)
        else: col2.image(foto, use_container_width=True)

# --- 3. ADMIN ---
else:
    st.title("🔐 Administrácia")
    if 'auth' not in st.session_state: st.session_state['auth'] = False
    if not st.session_state['auth']:
        with st.form("login"):
            u = st.text_input("Užívateľ"); h = st.text_input("Heslo", type="password")
            if st.form_submit_button("Vstúpiť"):
                if u == LOGIN_MENO and h == LOGIN_HESLO: st.session_state['auth'] = True; st.rerun()
                else: st.error("Nesprávne údaje!")
    else:
        if st.sidebar.button("Odhlásiť sa"): st.session_state['auth'] = False; st.rerun()
        t1, t2, t3 = st.tabs(["📩 Nové dopyty", "📅 Kalendár", "➕ Pridať"])
        
        with t1:
            cakajuce = [a for a in db if a.get("stav") == "cakajuce"]
            for i, a in enumerate(cakajuce):
                with st.expander(f"{a['datum']} - {a['poznamka'][:20]}..."):
                    st.write(f"Info: {a['poznamka']}")
                    c1, c2 = st.columns(2)
                    if c1.button("✅ Schváliť", key=f"ok{i}"):
                        for item in db:
                            if item['id'] == a['id']: item['stav'] = "schvalene"
                        uloz_data(db); st.rerun()
                    if c2.button("🗑️ Zmazať", key=f"no{i}"):
                        db = [item for item in db if item['id'] != a['id']]
                        uloz_data(db); st.rerun()

        with t2:
            schvalene = [a for a in db if a.get("stav") == "schvalene" or "stav" not in a]
            schvalene.sort(key=lambda x: x['datum'])
            for i, a in enumerate(schvalene):
                with st.expander(f"📅 {a['datum']} - {a['poznamka'][:30]}"):
                    e_d = st.date_input("Dátum", value=datetime.strptime(a['datum'], '%Y-%m-%d'), key=f"d{i}")
                    e_n = st.text_area("Poznámka", value=a['poznamka'], key=f"n{i}")
                    if st.button("Uložiť", key=f"s{i}"):
                        for item in db:
                            if item['id'] == a['id']: item['datum'] = str(e_d); item['poznamka'] = e_n
                        uloz_data(db); st.rerun()
                    if st.button("Zmazať", key=f"del{i}"):
                        db = [item for item in db if item['id'] != a['id']]
                        uloz_data(db); st.rerun()

        with t3:
            with st.form("add"):
                d = st.date_input("Dátum"); n = st.text_input("Miesto")
                if st.form_submit_button("Uložiť"):
                    db.append({"id": str(datetime.now().timestamp()), "datum": str(d), "cas": "---", "poznamka": n, "stav": "schvalene"})
                    uloz_data(db); st.success("Pridané!"); st.rerun()

st.markdown(f'<div style="text-align:center; margin-top:50px; color:#ccc;"><b>Podpora:</b> 0944 757 122</div>', unsafe_allow_html=True)
