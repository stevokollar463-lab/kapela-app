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

# Odkaz na fotku (odporúčam nahradiť vašou reálnou fotkou)
HEADER_IMAGE = "https://images.unsplash.com/photo-1514525253361-bee8718a74a2?q=80&w=1000&auto=format&fit=crop"

# --- BRUTÁLNY DIZAJN (CSS) ---
def apply_style():
    st.markdown(f"""
        <style>
        .stApp {{
            background-color: #0e1117;
            color: #ffffff;
        }}
        [data-testid="stSidebar"] {{
            background-color: #161b22;
            border-right: 2px solid #d4af37;
        }}
        h1, h2, h3 {{
            color: #d4af37 !important;
            font-family: 'Playfair Display', serif;
            text-transform: uppercase;
            letter-spacing: 2px;
        }}
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
        .footer-text {{
            text-align: center;
            color: #808080;
            font-size: 0.85rem;
            margin-top: 50px;
            padding: 20px;
            border-top: 1px solid #333;
        }}
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

def footer():
    st.markdown(f"""
        <div class="footer-text">
            V prípade technických problémov kontaktujte správcu:<br>
            📞 <b>0944 757 122</b> | ✉️ <b>kollarstevo55@gmail.com</b>
        </div>
    """, unsafe_allow_html=True)

# --- KONFIGURÁCIA STRÁNKY ---
st.set_page_config(page_title="Ovčanske Parobci | Rezervácie", page_icon="🎸", layout="centered")
apply_style()

# --- SIDEBAR ---
st.sidebar.image(HEADER_IMAGE, use_container_width=True)
st.sidebar.markdown("<h2 style='text-align: center;'>MENU</h2>", unsafe_allow_html=True)
menu_moznost = st.sidebar.radio("", ["🎸 Chceme vás na akciu", "🔐 Vstup pre kapelu"])

# --- 1. VEREJNÁ ČASŤ ---
if menu_moznost == "🎸 Chceme vás na akciu":
    st.image(HEADER_IMAGE, caption="Ovčanske Parobci", use_container_width=True)
    st.title("🎻 Ovčanske Parobci")
    st.markdown("### Rezervujte si najlepšiu zábavu!")
    
    st.divider()
    
    with st.form("form_rezervacia"):
        d = st.date_input("Kedy sa bude žúrovať?", min_value=datetime.now())
        c = st.time_input("Odkedy máme začať?")
        m = st.text_input("Vaše meno a telefón")
        p = st.text_area("Povedzte nám o akcii viac (miesto, typ akcie...)")
        
        submit = st.form_submit_button("ODOSLAŤ REZERVÁCIU")
        
        if submit:
            data = nacti_data()
            if any(a['datum'] == str(d) for a in data):
                st.error(f"Tento termín ({d}) je už obsadený. Skúste prosím iný.")
            elif not m:
                st.warning("Zadajte prosím kontaktné údaje.")
            else:
                msg = f"DOPYT NA WEB!\nDátum: {d}\nČas: {c}\nKontakt: {m}\nInfo: {p}"
                if posli_upozornenie(msg):
                    st.balloons()
                    st.success("Rezervácia bola úspešne odoslaná! Ozveme sa vám. ✅")

# --- 2. ADMIN ČASŤ ---
else:
    st.title("🔐 Administrácia")
    
    if 'auth' not in st.session_state: st.session_state['auth'] = False

    if not st.session_state['auth']:
        st.info("Zadajte prístupové údaje pre správu kalendára.")
        v_meno = st.text_input("Užívateľ")
        v_heslo = st.text_input("Heslo", type="password")
        if st.button("PRIHLÁSIŤ SA"):
            if v_meno == LOGIN_MENO and v_heslo == LOGIN_HESLO:
                st.session_state['auth'] = True
                st.rerun()
            else: st.error("Nesprávne meno alebo heslo!")
    else:
        st.success("Ste prihlásený ako správca.")
        if st.sidebar.button("ODHLÁSIŤ SA"):
            st.session_state['auth'] = False
            st.rerun()

        t1, t2 = st.tabs(["➕ Pridať akciu", "📅 Plán akcií"])
        
        with t1:
            with st.form("add"):
                d = st.date_input("Dátum")
                c = st.time_input("Čas")
                p = st.text_input("Názov/Miesto")
                if st.form_submit_button("ULOŽIŤ DO KALENDÁRA"):
                    data = nacti_data()
                    data.append({"datum": str(d), "cas": str(c), "poznamka": p})
                    uloz_data(data)
                    st.success("Akcia bola úspešne uložená!")

        with t2:
            data = nacti_data()
            if data:
                data.sort(key=lambda x: x['datum'])
                for a in data:
                    st.write(f"🟡 **{a['datum']}** - {a['poznamka']} ({a['cas']})")
                
                st.divider()
                if st.button("🗑️ VYMAZAŤ CELÝ KALENDÁR"):
                    uloz_data([])
                    st.rerun()
            else:
                st.write("Kalendár je prázdny.")

# Zavolanie päty s tvojimi údajmi
footer()
