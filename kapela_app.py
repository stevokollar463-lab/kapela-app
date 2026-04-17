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

HEADER_IMAGE = "https://images.unsplash.com/photo-1514525253361-bee8718a74a2?q=80&w=1000&auto=format&fit=crop"

# --- DIZAJN (CSS) ---
def apply_style():
    st.markdown(f"""
        <style>
        .stApp {{ background-color: #0e1117; color: #ffffff; }}
        [data-testid="stSidebar"] {{ background-color: #161b22; border-right: 2px solid #d4af37; }}
        h1, h2, h3 {{ color: #d4af37 !important; font-family: 'Playfair Display', serif; text-transform: uppercase; letter-spacing: 2px; }}
        .stButton>button {{ background-color: #d4af37 !important; color: black !important; border-radius: 20px !important; border: none !important; font-weight: bold !important; transition: 0.3s; }}
        .stButton>button:hover {{ transform: scale(1.02); box-shadow: 0px 0px 15px #d4af37; }}
        .footer-text {{ text-align: center; color: #808080; font-size: 0.85rem; margin-top: 50px; padding: 20px; border-top: 1px solid #333; }}
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
    st.markdown(f"""<div class="footer-text">V prípade technických problémov kontaktujte správcu:<br>📞 <b>0944 757 122</b> | ✉️ <b>kollarstevo55@gmail.com</b></div>""", unsafe_allow_html=True)

# --- KONFIGURÁCIA STRÁNKY ---
st.set_page_config(page_title="Ovčanske Parobci | Rezervácie", page_icon="🎸", layout="centered")
apply_style()

# --- SIDEBAR ---
st.sidebar.image(HEADER_IMAGE, use_container_width=True)
menu_moznost = st.sidebar.radio("MENU", ["🎸 Chceme vás na akciu", "🔐 Vstup pre kapelu"])

# --- 1. VEREJNÁ ČASŤ ---
if menu_moznost == "🎸 Chceme vás na akciu":
    st.image(HEADER_IMAGE, caption="Ovčanske Parobci", use_container_width=True)
    st.title("🎻 Ovčanske Parobci")
    st.markdown("### Rezervujte si najlepšiu zábavu!")
    
    with st.form("form_rezervacia"):
        d = st.date_input("Kedy sa bude žúrovať?", min_value=datetime.now())
        c = st.time_input("Odkedy máme začať?")
        m = st.text_input("Vaše meno a telefón")
        p = st.text_area("Povedzte nám o akcii viac")
        if st.form_submit_button("ODOSLAŤ REZERVÁCIU"):
            data = nacti_data()
            if any(a['datum'] == str(d) for a in data):
                st.error("Tento termín je už obsadený.")
            elif not m:
                st.warning("Zadajte kontakt.")
            else:
                if posli_upozornenie(f"DOPYT: {d} o {c}\nKontakt: {m}\nInfo: {p}"):
                    st.balloons()
                    st.success("Odoslané! ✅")

# --- 2. ADMIN ČASŤ ---
else:
    st.title("🔐 Administrácia")
    if 'auth' not in st.session_state: st.session_state['auth'] = False

    if not st.session_state['auth']:
        v_meno = st.text_input("Užívateľ")
        v_heslo = st.text_input("Heslo", type="password")
        if st.button("PRIHLÁSIŤ SA"):
            if v_meno == LOGIN_MENO and v_heslo == LOGIN_HESLO:
                st.session_state['auth'] = True
                st.rerun()
            else: st.error("Nesprávne údaje!")
    else:
        if st.sidebar.button("ODHLÁSIŤ SA"):
            st.session_state['auth'] = False
            st.rerun()

        t1, t2 = st.tabs(["➕ Pridať akciu", "📅 Plán akcií"])
        
        with t1:
            with st.form("add_form"):
                d_in = st.date_input("Dátum")
                c_in = st.time_input("Čas")
                p_in = st.text_input("Miesto / Názov")
                if st.form_submit_button("ULOŽIŤ"):
                    data = nacti_data()
                    data.append({"id": str(datetime.now().timestamp()), "datum": str(d_in), "cas": str(c_in), "poznamka": p_in})
                    uloz_data(data)
                    st.success("Uložené!")

        with t2:
            data = nacti_data()
            if data:
                data.sort(key=lambda x: x['datum'])
                for idx, a in enumerate(data):
                    with st.expander(f"📅 {a['datum']} - {a['poznamka']}"):
                        # EDITÁCIA PRIAMO V EXPANDERI
                        new_date = st.date_input("Upraviť dátum", value=datetime.strptime(a['datum'], '%Y-%m-%d'), key=f"date_{idx}")
                        new_time = st.text_input("Upraviť čas", value=a['cas'], key=f"time_{idx}")
                        new_note = st.text_input("Upraviť názov/miesto", value=a['poznamka'], key=f"note_{idx}")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("💾 Uložiť zmeny", key=f"save_{idx}"):
                                data[idx]['datum'] = str(new_date)
                                data[idx]['cas'] = new_time
                                data[idx]['poznamka'] = new_note
                                uloz_data(data)
                                st.success("Upravené!")
                                st.rerun()
                        with col2:
                            if st.button("🗑️ Vymazať akciu", key=f"del_{idx}"):
                                data.pop(idx)
                                uloz_data(data)
                                st.rerun()
                
                if st.button("🗑️ VYMAZAŤ CELÝ KALENDÁR"):
                    uloz_data([])
                    st.rerun()
            else:
                st.write("Žiadne akcie.")

footer()
