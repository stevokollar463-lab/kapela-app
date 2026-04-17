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
        
        /* Zloženie a Cenník boxy */
        .info-box {{
            background: rgba(212, 175, 55, 0.15);
            border: 1px solid #d4af37;
            padding: 15px;
            border-radius: 15px;
            text-align: center;
            margin: 10px 0;
            text-shadow: 2px 2px 4px #000;
        }}

        .stForm {{ background-color: rgba(0, 0, 0, 0.8) !important; border: 2px solid #d4af37 !important; border-radius: 20px; padding: 30px; }}
        .stButton>button {{ background-color: #d4af37 !important; color: black !important; border-radius: 12px !important; font-weight: bold !important; width: 100%; transition: 0.3s; }}
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
    
    # SEKCIA ZLOŽENIE
    st.markdown("""
        <div class="info-box">
            🪗 <b>Akordeón</b> &nbsp; 🪗 <b>Akordeón</b> &nbsp; 🎻 <b>Husle</b> &nbsp; 🥁 <b>Bubon</b> &nbsp; 🎷 <b>Saxofón</b>
        </div>
    """, unsafe_allow_html=True)

    # SEKCIA CENNÍK
    st.markdown("""
        <div class="info-box" style="border-color: #eee; background: rgba(255,255,255,0.05);">
            💰 <b>Cenová ponuka:</b> Cenu stanovujeme individuálne podľa dĺžky hrania a miesta akcie. <br>
            Napíšte nám detaily a obratom vám pošleme nezáväzný návrh.
        </div>
    """, unsafe_allow_html=True)
    
    with st.form("main_booking"):
        st.subheader("📩 Rezervačný dopyt")
        col1, col2 = st.columns(2)
        with col1: datum = st.date_input("Dátum akcie", min_value=datetime.now())
        with col2: cas = st.time_input("Čas začiatku")
        
        meno = st.text_input("Meno a telefón")
        email_zakaznika = st.text_input("Váš E-mail (pre zaslanie potvrdenia)")
        detaily = st.text_area("Detaily (miesto konania, typ akcie, počet hodín...)")
        
        if st.form_submit_button("ODOSLAŤ REZERVÁCIU"):
            if not meno or not email_zakaznika:
                st.warning("Uveďte prosím meno aj e-mail.")
            else:
                db = nacti_data()
                nova = {
                    "id": str(datetime.now().timestamp()), 
                    "datum": str(datum), 
                    "cas": str(cas), 
                    "poznamka": f"{meno} | {email_zakaznika} | {detaily}", 
                    "stav": "cakajuce"
                }
                db.append(nova); uloz_data(db)
                
                # Oznámenie kapele
                posli_upozornenie(f"Dopyt: {datum} od {meno}\nE-mail: {email_zakaznika}")
                
                st.balloons()
                st.success(f"Dopyt bol odoslaný! Na adresu {email_zakaznika} sme vám pripravili potvrdenie.")
                
                # Tlačidlo pre zákazníka na odoslanie mailu kapele (Mailto odkaz)
                subject = "Rezervácia - Ovčanske Parobci"
                body = f"Dobrý deň, posielam detaily k akcii dňa {datum}. Moje tel. číslo: {meno}."
                mailto_link = f"mailto:kollarstevo55@gmail.com?subject={subject}&body={body}"
                
                st.markdown(f"""
                    <div style="text-align:center; margin-top:10px;">
                        <a href="{mailto_link}" style="background-color:#d4af37; color:black; padding:10px 20px; text-decoration:none; border-radius:10px; font-weight:bold;">
                            📧 KLIKNITE SEM PRE POTVRDENIE E-MAILOM
                        </a>
                    </div>
                """, unsafe_allow_html=True)

# --- 2. GALÉRIA ---
elif menu == "📸 Galéria":
    st.title("📸 Naša Zábava")
    fotky = [
        "https://i.postimg.cc/vZKfzcN0/received-1165768235166057.jpg",
        "https://i.postimg.cc/6pPn0ymH/received-640306331056375.jpg",
        "https://i.postimg.cc/cLzwmrbT/received-796698713423840.jpg",
        "https://i.postimg.cc/RZYKRND1/received-936809825229820.jpg"
    ]
    for foto in fotky:
        st.image(foto, use_container_width=True)

# --- 3. ADMIN ---
else:
    # (Zostáva nezmenené - správa dopytov)
    st.title("🔐 Administrácia")
    if 'auth' not in st.session_state: st.session_state['auth'] = False
    if not st.session_state['auth']:
        with st.form("login"):
            u = st.text_input("Užívateľ"); h = st.text_input("Heslo", type="password")
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
                with st.expander(f"{a['datum']} - {a['poznamka'][:30]}..."):
                    st.write(f"Kontakt a detaily: {a['poznamka']}")
                    c1, col2 = st.columns(2)
                    if c1.button("✅ Schváliť", key=f"ok{i}"):
                        for item in db:
                            if item['id'] == a['id']: item['stav'] = "schvalene"
                        uloz_data(db); st.rerun()
                    if col2.button("🗑️ Zmazať", key=f"no{i}"):
                        db = [item for item in db if item['id'] != a['id']]
                        uloz_data(db); st.rerun()
        
        with t2:
            schvalene = [a for a in db if a.get("stav") == "schvalene" or "stav" not in a]
            schvalene.sort(key=lambda x: x['datum'])
            for i, a in enumerate(schvalene):
                with st.expander(f"📅 {a['datum']} - {a['poznamka'][:30]}..."):
                    e_date = st.date_input("Dátum", value=datetime.strptime(a['datum'], '%Y-%m-%d'), key=f"d_{i}")
                    e_note = st.text_area("Poznámka", value=a['poznamka'], key=f"n_{i}")
                    if st.button("💾 Uložiť", key=f"s_{i}"):
                        for item in db:
                            if item['id'] == a['id']: item['datum'] = str(e_date); item['poznamka'] = e_note
                        uloz_data(db); st.rerun()
                    if st.button("🗑️ Vymazať", key=f"del{i}"):
                        db = [item for item in db if item['id'] != a['id']]
                        uloz_data(db); st.rerun()
        
        with t3:
            with st.form("add"):
                d = st.date_input("Dátum"); p = st.text_input("Poznámka")
                if st.form_submit_button("Uložiť"):
                    db.append({"id": str(datetime.now().timestamp()), "datum": str(d), "cas": "---", "poznamka": p, "stav": "schvalene"})
                    uloz_data(db); st.rerun()

st.markdown(f'<div style="text-align:center; margin-top:50px; color:#ccc;"><b>Podpora:</b> 0944 757 122</div>', unsafe_allow_html=True)
