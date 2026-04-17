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

# NOVÝ KVALITNÝ LINK Z POSTIMAGES
KAPELA_FOTO_URL = "https://i.postimg.cc/k4GMHzmG/1000027016.jpg" 

# --- DIZAJN (CSS) ---
def apply_style():
    st.markdown(f"""
        <style>
        /* Celoobrazovkové pozadie v top kvalite */
        .stApp {{
            background: linear-gradient(rgba(0, 0, 0, 0.65), rgba(0, 0, 0, 0.65)), 
                        url("{KAPELA_FOTO_URL}");
            background-size: cover;
            background-position: top center;
            background-attachment: fixed;
            color: #ffffff;
        }}
        
        /* Transparentný bočný panel */
        [data-testid="stSidebar"] {{
            background-color: rgba(20, 20, 20, 0.8) !important;
            backdrop-filter: blur(12px);
            border-right: 1px solid #d4af37;
        }}
        
        /* Zlaté nadpisy */
        h1, h2, h3, h4 {{ 
            color: #d4af37 !important; 
            font-family: 'Playfair Display', serif; 
            text-shadow: 4px 4px 8px #000000;
            text-align: center;
        }}

        /* Formulár v elegantnom boxe */
        .stForm {{
            background-color: rgba(0, 0, 0, 0.7) !important;
            border: 2px solid #d4af37 !important;
            border-radius: 20px;
            padding: 30px;
            backdrop-filter: blur(10px);
            box-shadow: 0px 15px 35px rgba(0,0,0,0.9);
        }}

        /* Brutálne zlaté tlačidlá */
        .stButton>button {{ 
            background-color: #d4af37 !important; 
            color: black !important; 
            border-radius: 12px !important; 
            font-weight: bold !important;
            font-size: 1.1rem !important;
            height: 3.5em;
            border: none !important;
            transition: all 0.4s ease;
        }}
        .stButton>button:hover {{
            transform: translateY(-3px);
            box-shadow: 0px 8px 25px #d4af37;
        }}
        
        /* Päta stránky */
        .footer-text {{ 
            text-align: center; 
            color: #eee; 
            font-size: 0.95rem; 
            margin-top: 60px; 
            padding: 25px; 
            background: rgba(0,0,0,0.8);
            border-radius: 15px;
            border-top: 2px solid #d4af37;
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
        pb.push_note("🎸 OVČANSKE PAROBCI", text)
        return True
    except: return False

def footer():
    st.markdown(f"""
        <div class="footer-text">
            <b>Máte technický problém? Kontaktujte správcu:</b><br>
            📞 <b>0944 757 122</b> | ✉️ <b>kollarstevo55@gmail.com</b>
        </div>
    """, unsafe_allow_html=True)

# --- ŠTART APP ---
st.set_page_config(page_title="Ovčanske Parobci", page_icon="🎻", layout="centered")
apply_style()

# --- SIDEBAR ---
st.sidebar.markdown("<h2 style='text-align: center;'>PAROBCI</h2>", unsafe_allow_html=True)
menu = st.sidebar.radio("NAVIGÁCIA", ["🎸 Rezervácia", "🔐 Administrácia"])

if menu == "🎸 Rezervácia":
    st.title("🎻 Ovčanske Parobci")
    st.markdown("<h4 style='text-align: center;'>Poriadna ľudová muzika na vašu akciu</h4>", unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    with st.form("main_booking"):
        st.subheader("📩 Rezervačný dopyt")
        col1, col2 = st.columns(2)
        with col1:
            datum = st.date_input("Dátum akcie", min_value=datetime.now())
        with col2:
            cas = st.time_input("Čas (približne)")
        
        meno = st.text_input("Vaše meno a telefónne číslo")
        detaily = st.text_area("Povedzte nám viac (miesto konania, typ akcie, počet ľudí...)")
        
        if st.form_submit_button("ODOSLAŤ REZERVÁCIU"):
            db = nacti_data()
            if any(a['datum'] == str(datum) for a in db):
                st.error("Prepáčte, tento termín je už obsadený.")
            elif not meno:
                st.warning("Uveďte prosím aspoň meno a telefón.")
            else:
                msg = f"DOPYT Z WEBU!\nKedy: {datum} o {cas}\nKontakt: {meno}\nInfo: {detaily}"
                if posli_upozornenie(msg):
                    st.balloons()
                    st.success("Vaša správa pípala kapele v mobile! Čoskoro sa vám ozveme. ✅")

else:
    st.title("🔐 Správa akcií")
    if 'auth' not in st.session_state: st.session_state['auth'] = False

    if not st.session_state['auth']:
        with st.form("admin_login"):
            u = st.text_input("Užívateľské meno")
            h = st.text_input("Heslo", type="password")
            if st.form_submit_button("PRIHLÁSIŤ SA"):
                if u == LOGIN_MENO and h == LOGIN_HESLO:
                    st.session_state['auth'] = True
                    st.rerun()
                else: st.error("Nesprávne údaje!")
    else:
        if st.sidebar.button("ODHLÁSIŤ SA"):
            st.session_state['auth'] = False
            st.rerun()

        tab1, tab2 = st.tabs(["➕ Pridať termín", "📅 Zoznam akcií"])
        
        with tab1:
            with st.form("add_event"):
                d_in = st.date_input("Dátum")
                c_in = st.time_input("Čas")
                p_in = st.text_input("Názov/Miesto")
                if st.form_submit_button("ULOŽIŤ"):
                    db = nacti_data()
                    db.append({"id": str(datetime.now().timestamp()), "datum": str(d_in), "cas": str(c_in), "poznamka": p_in})
                    uloz_data(db)
                    st.success("Zapísané do kalendára!")

        with tab2:
            db = nacti_data()
            if db:
                db.sort(key=lambda x: x['datum'])
                for i, a in enumerate(db):
                    with st.expander(f"📅 {a['datum']} - {a['poznamka']}"):
                        nd = st.date_input("Dátum", value=datetime.strptime(a['datum'], '%Y-%m-%d'), key=f"d{i}")
                        nc = st.text_input("Čas", value=a['cas'], key=f"c{i}")
                        np = st.text_input("Miesto", value=a['poznamka'], key=f"p{i}")
                        c1, c2 = st.columns(2)
                        with c1:
                            if st.button("Uložiť", key=f"s{i}"):
                                db[i] = {"id": a['id'], "datum": str(nd), "cas": nc, "poznamka": np}
                                uloz_data(db); st.rerun()
                        with c2:
                            if st.button("Zmazať", key=f"r{i}"):
                                db.pop(i); uloz_data(db); st.rerun()
            else:
                st.write("Žiadne naplánované termíny.")

footer()
