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

KAPELA_FOTO_URL = "https://i.postimg.cc/T1Pkgjnw/1000027016.jpg"

# --- DIZAJN ---
def apply_style():
    st.markdown(f"""
        <style>
        .stApp {{
            background: linear-gradient(rgba(0, 0, 0, 0.65), rgba(0, 0, 0, 0.65)), 
                        url("{KAPELA_FOTO_URL}");
            background-size: cover;
            background-position: left center;
            background-attachment: fixed;
            color: #ffffff;
        }}
        [data-testid="stSidebar"] {{ background-color: rgba(20, 20, 20, 0.8) !important; backdrop-filter: blur(12px); border-right: 1px solid #d4af37; }}
        h1, h2, h3, h4 {{ color: #d4af37 !important; font-family: 'Playfair Display', serif; text-shadow: 4px 4px 8px #000000; text-align: center; }}
        .stForm {{ background-color: rgba(0, 0, 0, 0.7) !important; border: 2px solid #d4af37 !important; border-radius: 20px; padding: 30px; }}
        .stButton>button {{ background-color: #d4af37 !important; color: black !important; border-radius: 12px !important; font-weight: bold !important; width: 100%; transition: 0.3s; }}
        .stButton>button:hover {{ transform: scale(1.02); box-shadow: 0px 0px 15px #d4af37; }}
        </style>
    """, unsafe_allow_html=True)

# --- PRÁCA S DÁTAMI ---
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

def footer():
    st.markdown(f"""
        <div style="text-align: center; color: #ccc; font-size: 0.9rem; margin-top: 50px; padding: 20px; background: rgba(0,0,0,0.7); border-radius: 10px; border-top: 1px solid #d4af37;">
            <b>Technická podpora:</b> 📞 0944 757 122 | ✉️ kollarstevo55@gmail.com
        </div>
    """, unsafe_allow_html=True)

# --- ŠTART APP ---
st.set_page_config(page_title="Ovčanske Parobci", page_icon="🎻", layout="centered")
apply_style()

st.sidebar.markdown("## PAROBCI")
menu = st.sidebar.radio("NAVIGÁCIA", ["🎸 Rezervácia", "🔐 Administrácia"])

# --- 1. REZERVÁCIA (HOST) ---
if menu == "🎸 Rezervácia":
    st.title("🎻 Ovčanske Parobci")
    st.markdown("#### Poriadna ľudová muzika na vašu akciu")
    
    with st.form("main_booking"):
        st.subheader("📩 Rezervačný dopyt")
        col1, col2 = st.columns(2)
        with col1: datum = st.date_input("Dátum akcie", min_value=datetime.now())
        with col2: cas = st.time_input("Približný čas")
        
        meno = st.text_input("Meno a telefón")
        detaily = st.text_area("Detaily (miesto, typ akcie...)")
        
        if st.form_submit_button("ODOSLAŤ REZERVÁCIU"):
            db = nacti_data()
            nova_akcia = {
                "id": str(datetime.now().timestamp()),
                "datum": str(datum),
                "cas": str(cas),
                "poznamka": f"{meno} | {detaily}",
                "stav": "cakajuce" 
            }
            db.append(nova_akcia)
            uloz_data(db)
            
            posli_upozornenie(f"Nový dopyt na {datum} od {meno}")
            st.balloons()
            st.success("Vaša požiadavka bola prijatá! Počkajte na potvrdenie kapelou. ✅")

# --- 2. ADMIN ---
else:
    st.title("🔐 Správa akcií")
    if 'auth' not in st.session_state: st.session_state['auth'] = False

    if not st.session_state['auth']:
        with st.form("login"):
            st.write("Vstup pre kapelu")
            u = st.text_input("Užívateľ")
            h = st.text_input("Heslo", type="password")
            if st.form_submit_button("Vstúpiť"):
                if u == LOGIN_MENO and h == LOGIN_HESLO:
                    st.session_state['auth'] = True
                    st.rerun()
                else: st.error("Nesprávne údaje!")
    else:
        if st.sidebar.button("Odhlásiť sa"):
            st.session_state['auth'] = False
            st.rerun()

        tab1, tab2, tab3 = st.tabs(["📩 Nové dopyty", "📅 Schválený kalendár", "➕ Pridať manuálne"])
        db = nacti_data()

        # TAB 1: ČAKAJÚCE NA POTVRDENIE
        with tab1:
            cakajuce = [a for a in db if a.get("stav") == "cakajuce"]
            if not cakajuce:
                st.write("Žiadne nové dopyty.")
            else:
                for i, a in enumerate(cakajuce):
                    with st.expander(f"Dopyt: {a['datum']} - {a['poznamka'][:30]}..."):
                        st.write(f"**Dátum:** {a['datum']} | **Čas:** {a['cas']}")
                        st.write(f"**Info:** {a['poznamka']}")
                        c1, col2 = st.columns(2)
                        if c1.button("✅ SCHVÁLIŤ", key=f"ok{i}"):
                            for item in db:
                                if item['id'] == a['id']: item['stav'] = "schvalene"
                            uloz_data(db)
                            st.rerun()
                        if col2.button("🗑️ ZAMIETNUŤ", key=f"no{i}"):
                            db = [item for item in db if item['id'] != a['id']]
                            uloz_data(db)
                            st.rerun()

        # TAB 2: SCHVÁLENÉ AKCIE
        with tab2:
            schvalene = [a for a in db if a.get("stav") == "schvalene" or "stav" not in a]
            if not schvalene:
                st.write("Kalendár je prázdny.")
            else:
                schvalene.sort(key=lambda x: x['datum'])
                for i, a in enumerate(schvalene):
                    with st.expander(f"📅 {a['datum']} - {a['poznamka'][:30]}..."):
                        st.write(f"**Čas:** {a['cas']}")
                        st.write(f"**Detaily:** {a['poznamka']}")
                        if st.button("Vymazať z kalendára", key=f"del{i}"):
                            db = [item for item in db if item['id'] != a['id']]
                            uloz_data(db)
                            st.rerun()

        # TAB 3: MANUÁLNE PRIDANIE
        with tab3:
            with st.form("manual_add"):
                d_in = st.date_input("Dátum")
                c_in = st.time_input("Čas")
                p_in = st.text_input("Poznámka")
                if st.form_submit_button("Uložiť priamo do kalendára"):
                    db.append({
                        "id": str(datetime.now().timestamp()), 
                        "datum": str(d_in), 
                        "cas": str(c_in), 
                        "poznamka": p_in, 
                        "stav": "schvalene"
                    })
                    uloz_data(db)
                    st.success("Akcia bola pridaná priamo do kalendára!")
                    st.rerun()

footer()
