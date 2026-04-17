import streamlit as st
import json
import os
from datetime import datetime
from pushbullet import Pushbullet

# --- KONFIGURÁCIA ---
DB_FILE = "kalendar_kapely.json"
PB_API_KEY = "o.Ir4LWAKm78pwEhpKkAf6WZY9uZPNCkSm"
LOGIN_MENO = "ovcanskeparobci"
LOGIN_HESLO = "OvcanskeParobci123"

# HLAVNÁ FOTKA POZADIA
KAPELA_FOTO_URL = "https://i.postimg.cc/T1Pkgjnw/1000027016.jpg" 

# --- DIZAJN ---
def apply_style():
    st.markdown(f"""
        <style>
        .stApp {{
            background: linear-gradient(rgba(0, 0, 0, 0.75), rgba(0, 0, 0, 0.75)), 
                        url("{KAPELA_FOTO_URL}");
            background-size: cover;
            background-position: center center;
            background-attachment: fixed;
            image-rendering: -webkit-optimize-contrast;
            color: #ffffff;
        }}
        [data-testid="stSidebar"] {{ background-color: rgba(20, 20, 20, 0.85) !important; backdrop-filter: blur(12px); border-right: 1px solid #d4af37; }}
        h1, h2, h3, h4 {{ color: #d4af37 !important; font-family: 'Playfair Display', serif; text-shadow: 4px 4px 8px #000000; text-align: center; }}
        
        .info-box {{
            background: rgba(212, 175, 55, 0.15);
            border: 1px solid #d4af37;
            padding: 15px;
            border-radius: 15px;
            text-align: center;
            margin: 10px 0;
        }}

        .stForm {{ background-color: rgba(0, 0, 0, 0.8) !important; border: 2px solid #d4af37 !important; border-radius: 20px; padding: 30px; }}
        .stButton>button {{ background-color: #d4af37 !important; color: black !important; border-radius: 12px !important; font-weight: bold !important; width: 100%; transition: 0.3s; }}
        
        /* Štýl pre zobrazenie detailov v admini */
        .admin-detail-box {{
            background-color: rgba(0, 100, 255, 0.15);
            border-left: 5px solid #0064ff;
            padding: 10px;
            margin: 10px 0;
            border-radius: 5px;
            font-size: 0.95rem;
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

# --- 1. REZERVÁCIA ---
if menu == "🎸 Rezervácia":
    st.title("🎻 Ovčanske Parobci")
    st.markdown('<div class="info-box">🪗 Akordeón | 🎻 Husle | 🥁 Bubon | 🎷 Saxofón</div>', unsafe_allow_html=True)
    
    with st.form("main_booking"):
        st.subheader("📩 Rezervačný dopyt")
        col1, col2 = st.columns(2)
        with col1: datum = st.date_input("Dátum akcie", min_value=datetime.now())
        with col2: cas = st.time_input("Čas začiatku")
        
        meno = st.text_input("Meno a priezvisko")
        tel = st.text_input("Telefónne číslo")
        email = st.text_input("E-mail")
        mesto_detaily = st.text_area("Miesto konania a iné detaily")
        
        if st.form_submit_button("ODOSLAŤ REZERVÁCIU"):
            db = nacti_data()
            if any(a['datum'] == str(datum) for a in db):
                st.error("Termín je už obsadený.")
            elif not meno or not tel:
                st.warning("Vyplňte meno a telefón.")
            else:
                nova = {
                    "id": str(datetime.now().timestamp()), 
                    "datum": str(datum), "cas": str(cas),
                    "meno": meno, "tel": tel, "email": email, 
                    "detaily": mesto_detaily, "stav": "cakajuce"
                }
                db.append(nova); uloz_data(db)
                posli_upozornenie(f"Nový dopyt: {datum}\n{meno} ({tel})\nMiesto: {mesto_detaily}")
                st.balloons(); st.success("Odoslané! Ozveme sa vám. ✅")

# --- 2. GALÉRIA ---
elif menu == "📸 Galéria":
    st.title("📸 Galéria")
    fotky = ["https://i.postimg.cc/vZKfzcN0/received-1165768235166057.jpg", "https://i.postimg.cc/6pPn0ymH/received-640306331056375.jpg", "https://i.postimg.cc/cLzwmrbT/received-796698713423840.jpg", "https://i.postimg.cc/RZYKRND1/received-936809825229820.jpg"]
    for f in fotky: st.image(f, use_container_width=True)

# --- 3. ADMIN ---
else:
    st.title("🔐 Administrácia")
    if 'auth' not in st.session_state: st.session_state['auth'] = False
    if not st.session_state['auth']:
        with st.form("login"):
            u = st.text_input("Meno"); h = st.text_input("Heslo", type="password")
            if st.form_submit_button("Vstúpiť"):
                if u == LOGIN_MENO and h == LOGIN_HESLO: st.session_state['auth'] = True; st.rerun()
                else: st.error("Chyba!")
    else:
        if st.sidebar.button("Odhlásiť sa"): st.session_state['auth'] = False; st.rerun()
        t1, t2, t3 = st.tabs(["📩 Nové dopyty", "📅 Kalendár", "➕ Pridať"])
        db = nacti_data()
        
        with t1:
            cakajuce = [a for a in db if a.get("stav") == "cakajuce"]
            for i, a in enumerate(cakajuce):
                # OŠETRENIE STARÝCH DÁT: Ak nemá pole 'detaily', skús 'poznamka'
                info_mesto = a.get('detaily', a.get('poznamka', 'Neuvedené'))
                with st.expander(f"DOPYT: {a['datum']} - {a.get('meno', 'Neznámy')}"):
                    st.write(f"📞 **Kontakt:** {a.get('tel', '---')} | 📧 {a.get('email', '---')}")
                    st.write(f"🕒 **Čas:** {a.get('cas', '---')}")
                    
                    # TOTO JE TEN BOX S DETAILAMI
                    st.markdown(f"""<div class="admin-detail-box"><b>Miesto a detaily:</b><br>{info_mesto}</div>""", unsafe_allow_html=True)
                    
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
                info_mesto = a.get('detaily', a.get('poznamka', 'Neuvedené'))
                with st.expander(f"📅 {a['datum']} - {a.get('meno', 'Akcia')}"):
                    st.write(f"📞 {a.get('tel', '')} | 🕒 {a.get('cas', '')}")
                    
                    # ZOBRAZENIE DETAILOV AJ V KALENDÁRI
                    st.markdown(f"""<div class="admin-detail-box"><b>Miesto/Poznámka:</b><br>{info_mesto}</div>""", unsafe_allow_html=True)
                    
                    if st.button("🗑️ Odstrániť", key=f"del{i}"):
                        db = [item for item in db if item['id'] != a['id']]
                        uloz_data(db); st.rerun()
        
        with t3:
            with st.form("add_manual"):
                d = st.date_input("Dátum"); m = st.text_input("Názov"); det = st.text_area("Miesto/Poznámka")
                if st.form_submit_button("Uložiť"):
                    db.append({"id": str(datetime.now().timestamp()), "datum": str(d), "meno": m, "detaily": det, "stav": "schvalene"})
                    uloz_data(db); st.success("OK"); st.rerun()

st.markdown(f'<div style="text-align:center; margin-top:50px; color:#ccc;"><b>Podpora:</b> 0944 757 122</div>', unsafe_allow_html=True)
