import streamlit as st
import json
import os
from datetime import datetime, time
from pushbullet import Pushbullet

# --- KONFIGURÁCIA ---
DB_FILE = "kalendar_kapely.json"
PB_API_KEY = "o.Ir4LWAKm78pwEhpKkAf6WZY9uZPNCkSm"
LOGIN_MENO = "ovcanskeparobci"
LOGIN_HESLO = "OvcanskeParobci123"

# HLAVNÁ FOTKA POZADIA
KAPELA_FOTO_URL = "https://i.postimg.cc/T1Pkgjnw/1000027016.jpg" 

# --- NASTAVENIE CIEN PRE KALKULAČKU ---
CENA_ZA_HODINU = 150  # 150 € za hodinu hrania
CENA_ZA_KM = 1.00     # 1.00 € za km (už počíta cestu tam aj späť)

# --- DIZAJN ---
def apply_style():
    st.markdown(f"""
        <style>
        /* Pozadie aplikácie */
        .stApp {{
            background: linear-gradient(rgba(0, 0, 0, 0.75), rgba(0, 0, 0, 0.75)), 
                        url("{KAPELA_FOTO_URL}");
            background-size: cover;
            background-position: center center;
            background-attachment: fixed;
            image-rendering: -webkit-optimize-contrast;
            color: #ffffff;
        }}
        
        /* ÚPLNÉ SKRYTIE BOČNÉHO PANELU A ŠÍPKY */
        [data-testid="collapsedSidebarNoOverlay"], 
        [data-testid="stSidebar"], 
        button[data-testid="stSidebarCollapseButton"] {{
            display: none !important;
        }}
        
        /* Nadpisy */
        h1, h2, h3, h4 {{ color: #d4af37 !important; font-family: 'Playfair Display', serif; text-shadow: 4px 4px 8px #000000; text-align: center; }}
        
        .info-box {{
            background: rgba(212, 175, 55, 0.15);
            border: 1px solid #d4af37;
            padding: 15px;
            border-radius: 15px;
            text-align: center;
            margin: 10px 0;
        }}

        /* Veľký zlatý box pre Cenník / Kalkulačku */
        .cennik-container {{
            background: rgba(0, 0, 0, 0.85);
            border: 2px solid #d4af37;
            padding: 25px;
            border-radius: 20px;
            box-shadow: 0 0 25px rgba(212, 175, 55, 0.25);
            margin-bottom: 25px;
        }}

        .kalkulacka-vysledok {{
            background: rgba(212, 175, 55, 0.2);
            border: 2px dashed #d4af37;
            padding: 20px;
            border-radius: 15px;
            text-align: center;
            margin-top: 20px;
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

        /* --- ŠTÝLOVANIE HORNÉHO MENU --- */
        div[data-testid="stRadio"] {{
            background: transparent !important;
            padding: 10px 0 !important;
        }}
        div[data-testid="stRadio"] > div[role="radiogroup"] {{
            display: flex !important;
            flex-direction: row !important;
            justify-content: center !important;
            flex-wrap: wrap !important;
            gap: 12px !important;
        }}
        /* Skrytie guličiek */
        div[data-testid="stRadio"] div[role="radiogroup"] > label > div:first-child {{
            display: none !important;
        }}
        /* Tlačidlá menu */
        div[data-testid="stRadio"] div[role="radiogroup"] > label {{
            background-color: rgba(0, 0, 0, 0.75) !important;
            border: 2px solid #d4af37 !important;
            color: #ffffff !important;
            padding: 12px 24px !important;
            border-radius: 30px !important;
            cursor: pointer !important;
            transition: all 0.3s ease !important;
            font-weight: bold !important;
            text-align: center !important;
            box-shadow: 0 4px 10px rgba(0,0,0,0.5) !important;
            min-width: 140px !important;
        }}
        /* Hover efekt */
        div[data-testid="stRadio"] div[role="radiogroup"] > label:hover {{
            background-color: rgba(212, 175, 55, 0.25) !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 15px rgba(212, 175, 55, 0.3) !important;
        }}
        /* Aktívne menu */
        div[data-testid="stRadio"] div[role="radiogroup"] > label[data-checked="true"] {{
            background-color: #d4af37 !important;
            color: #000000 !important;
            box-shadow: 0 0 18px #d4af37 !important;
            border-color: #ffffff !important;
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

# Inicializácia premenných pre prenos z Cenníka do Rezervácie
if "pref_hodiny" not in st.session_state: st.session_state["pref_hodiny"] = 5
if "pref_cena" not in st.session_state: st.session_state["pref_cena"] = "Nenapočítaná"
if "pref_cas_od" not in st.session_state: st.session_state["pref_cas_od"] = time(18, 0)
if "pref_cas_do" not in st.session_state: st.session_state["pref_cas_do"] = time(23, 0)
if "pref_km" not in st.session_state: st.session_state["pref_km"] = 0
if "aktivne_menu" not in st.session_state: st.session_state["aktivne_menu"] = "🎸 Rezervácia"

# Pomocná funkcia na prepnutie menu
def zmen_menu(nove_menu):
    st.session_state["aktivne_menu"] = nove_menu

# MODERNÉ HORNÉ NAVIGAČNÉ MENU (Pridaný Cenník)
menu_moznosti = ["🎸 Rezervácia", "💰 Cenník", "📸 Galéria", "🔐 Administrácia"]
zvolene_menu = st.radio(
    "NAVIGÁCIA", 
    menu_moznosti, 
    index=menu_moznosti.index(st.session_state["aktivne_menu"]),
    horizontal=True,
    label_visibility="collapsed",
    key="navigation_radio"
)

# Ak užívateľ klikol priamo na menu, zosynchronizujeme stav
if zvolene_menu != st.session_state["aktivne_menu"]:
    st.session_state["aktivne_menu"] = zvolene_menu
    st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

# --- 1. REZERVÁCIA ---
if st.session_state["aktivne_menu"] == "🎸 Rezervácia":
    st.title("🎻 Rezervácia vystúpenia")
    st.markdown('<div class="info-box">🪗 Akordeón | 🎻 Husle | 🥁 Bubon | 🎷 Saxofón</div>', unsafe_allow_html=True)
    
    with st.form("main_booking"):
        st.subheader("📩 Rezervačný formulár")
        
        col1, col2 = st.columns(2)
        with col1: 
            datum = st.date_input("Dátum akcie", min_value=datetime.now())
        with col2: 
            # Použijeme predvolený čas z kalkulačky, ak existuje
            cas = st.time_input("Čas začiatku", value=st.session_state["pref_cas_od"])
            
        st.markdown("---")
        
        # Zobrazenie kalkulácie z cenníka, ak si ju užívateľ klikol
        st.markdown(f"""
            <div style="background: rgba(212, 175, 55, 0.1); border: 1px solid #d4af37; padding: 15px; border-radius: 10px; margin-bottom: 20px;">
                <h5 style="color:#d4af37; margin:0 0 5px 0; text-align:left;">📊 Vybraná kalkulácia:</h5>
                <p style="margin:0; font-size: 1.1rem;">
                    <b>Cena spolu: {st.session_state["pref_cena"]}</b><br>
                    <small style="color:#bbb;">Plánovaný čas: {st.session_state["pref_cas_od"].strftime('%H:%M')} do {st.session_state["pref_cas_do"].strftime('%H:%M')} ({st.session_state["pref_hodiny"]}h hrania) | Doprava: {st.session_state["pref_km"]} km</small>
                </p>
                <p style="margin: 8px 0 0 0; font-size: 0.85rem; color: #aaa;"><i>* Ak chcete cenu zmeniť alebo prepočítať, kliknite hore na záložku "💰 Cenník".</i></p>
            </div>
        """, unsafe_allow_html=True)
        
        # --- OSOBNÉ ÚDAJE ---
        st.subheader("✍️ Vaše kontaktné údaje")
        meno = st.text_input("Meno a priezvisko")
        tel = st.text_input("Telefónne číslo")
        email = st.text_input("E-mail")
        mesto_detaily = st.text_area("Presná adresa konania (mesto/sála) a iné detaily")
        
        if st.form_submit_button("ODOSLAŤ REZERVÁCIU"):
            db = nacti_data()
            if any(a['datum'] == str(datum) for a in db):
                st.error("Tento termín je už obsadený.")
            elif not meno or not tel:
                st.warning("Vyplňte, prosím, vaše meno a telefónne číslo.")
            else:
                nova = {
                    "id": str(datetime.now().timestamp()), 
                    "datum": str(datum), 
                    "cas": f"{cas.strftime('%H:%M')} (Hranie {st.session_state['pref_hodiny']}h)",
                    "meno": meno, 
                    "tel": tel, 
                    "email": email, 
                    "detaily": mesto_detaily, 
                    "vypocitana_cena": f"{st.session_state['pref_cena']} ({st.session_state['pref_hodiny']}h, {st.session_state['pref_km']} km od Ovčieho)",
                    "stav": "cakajuce"
                }
                db.append(nova); uloz_data(db)
                posli_upozornenie(f"Nový dopyt: {datum}\n{meno} ({tel})\nČas: {cas.strftime('%H:%M')} ({st.session_state['pref_hodiny']}h)\nKalkulácia: {st.session_state['pref_cena']}")
                st.balloons(); st.success("Odoslané! Ozveme sa vám hneď, ako to schválime. ✅")

# --- 2. CENNÍK & INTERAKTÍVNA KALKULAČKA ---
elif st.session_state["aktivne_menu"] == "💰 Cenník":
    st.title("💰 Cenník & Kalkulačka")
    
    st.markdown(f"""
        <div class="cennik-container">
            <h3 style="margin-top: 0;">Základné sadzby</h3>
            <p style="font-size: 1.2rem; text-align: center; margin-bottom: 5px;">
                🎻 <b>Hranie na akcii:</b> <span style="color: #d4af37; font-weight: bold;">{CENA_ZA_HODINU} € / hodina</span>
            </p>
            <p style="font-size: 1.2rem; text-align: center; margin-bottom: 0;">
                🚗 <b>Doprava (z obce Ovčie):</b> <span style="color: #d4af37; font-weight: bold;">{CENA_ZA_KM:.2f} € / km</span> <small style="color:#aaa;">(zahŕňa cestu tam aj späť)</small>
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    st.subheader("🧮 Vypočítajte si cenu na vašu akciu")
    
    # Výber od-do pomocou výberových polí pre čas
    col_od, col_do = st.columns(2)
    with col_od:
        cas_od = st.time_input("Čas od", value=st.session_state["pref_cas_od"], step=1800)
    with col_do:
        cas_do = st.time_input("Čas do", value=st.session_state["pref_cas_do"], step=1800)
        
    # Výpočet hodín na základe vybraných časov
    datetime_od = datetime.combine(datetime.today(), cas_od)
    datetime_do = datetime.combine(datetime.today(), cas_do)
    
    # Ak čas "do" prechádza cez polnoc
    if datetime_do <= datetime_od:
        datetime_do = datetime.combine(datetime.today() + datetime.timedelta(days=1), cas_do)
        
    rozdiel_sekundy = (datetime_do - datetime_od).total_seconds()
    odhad_hodin = round(rozdiel_sekundy / 3600.0, 1)
    
    # Zadanie kilometrov
    km = st.number_input("Vzdialenosť z obce Ovčie (km v jednom smere)", min_value=0, value=st.session_state["pref_km"], step=5)
    
    # Výpočty
    cena_hudba = odhad_hodin * CENA_ZA_HODINU
    cena_doprava = km * CENA_ZA_KM # Už berieme, že 1€ / km zahŕňa všetko
    celkova_cena = cena_hudba + cena_doprava
    
    st.markdown(f"""
        <div class="kalkulacka-vysledok">
            <span style="font-size: 1.1rem; color: #ccc;">Predbežná kalkulácia ceny:</span><br>
            <span style="font-size: 2.2rem; font-weight: bold; color: #d4af37;">{celkova_cena:.2f} €</span><br>
            <span style="font-size: 1rem; color: #eee;">Dĺžka hrania: <b>{odhad_hodin} hod.</b> ({cena_hudba:.2f} €) | Doprava: <b>{km} km</b> ({cena_doprava:.2f} €)</span>
        </div>
        <br>
    """, unsafe_allow_html=True)
    
    # Tlačidlo pre potvrdenie kalkulácie a prenos do formulára
    if st.button("👉 SÚHLASÍM S TOUTO CENOU, CHCEM SI REZERVOVAŤ TERMÍN"):
        # Uložíme hodnoty do session_state
        st.session_state["pref_hodiny"] = odhad_hodin
        st.session_state["pref_cena"] = f"{celkova_cena:.2f} €"
        st.session_state["pref_cas_od"] = cas_od
        st.session_state["pref_cas_do"] = cas_do
        st.session_state["pref_km"] = km
        
        # Prepnutie na rezervačnú kartu
        zmen_menu("🎸 Rezervácia")
        st.rerun()

# --- 3. GALÉRIA ---
elif st.session_state["aktivne_menu"] == "📸 Galéria":
    st.title("📸 Galéria")
    fotky = [
        "https://i.postimg.cc/vZKfzcN0/received-1165768235166057.jpg", 
        "https://i.postimg.cc/6pPn0ymH/received-640306331056375.jpg", 
        "https://i.postimg.cc/cLzwmrbT/received-796698713423840.jpg", 
        "https://i.postimg.cc/RZYKRND1/received-936809825229820.jpg"
    ]
    col_img1, col_img2 = st.columns(2)
    for idx, f in enumerate(fotky):
        if idx % 2 == 0:
            with col_img1: st.image(f, use_container_width=True)
        else:
            with col_img2: st.image(f, use_container_width=True)

# --- 4. ADMIN ---
else:
    col_title, col_logout = st.columns([3, 1])
    with col_title:
        st.title("🔐 Administrácia")
    
    if 'auth' not in st.session_state: st.session_state['auth'] = False
    
    if not st.session_state['auth']:
        with st.form("login"):
            u = st.text_input("Meno"); h = st.text_input("Heslo", type="password")
            if st.form_submit_button("Vstúpiť"):
                if u == LOGIN_MENO and h == LOGIN_HESLO: st.session_state['auth'] = True; st.rerun()
                else: st.error("Chyba!")
    else:
        with col_logout:
            st.write("") 
            if st.button("Odhlásiť sa", key="logout_btn"): 
                st.session_state['auth'] = False
                st.rerun()
                
        t1, t2, t3 = st.tabs(["📩 Nové dopyty", "📅 Kalendár", "➕ Pridať"])
        db = nacti_data()
        
        with t1:
            cakajuce = [a for a in db if a.get("stav") == "cakajuce"]
            for i, a in enumerate(cakajuce):
                info_mesto = a.get('detaily', a.get('poznamka', 'Neuvedené'))
                kalkulacia = a.get('vypocitana_cena', 'Nenapočítaná')
                with st.expander(f"DOPYT: {a['datum']} - {a.get('meno', 'Neznámy')}"):
                    st.write(f"📞 **Kontakt:** {a.get('tel', '---')} | 📧 {a.get('email', '---')}")
                    st.write(f"🕒 **Čas:** {a.get('cas', '---')}")
                    st.write(f"💰 **Vypočítaná cena v cenníku:** {kalkulacia}")
                    
                    st.markdown(f"""<div class="admin-detail-box"><b>Miesto a detaily:</b><br>{info_mesto}</div>""", unsafe_allow_html=True)
                    
                    c1, c2, c3 = st.columns(3)
                    if c1.button("✅ Schváliť", key=f"ok{i}"):
                        for item in db:
                            if item['id'] == a['id']: item['stav'] = "schvalene"
                        uloz_data(db); st.rerun()
                    
                    if c2.button("🗑️ Zmazať", key=f"no{i}"):
                        db = [item for item in db if item['id'] != a['id']]
                        uloz_data(db); st.rerun()
                        
                    edit_key = f"edit_active_t1_{a['id']}"
                    if edit_key not in st.session_state:
                        st.session_state[edit_key] = False
                        
                    if c3.button("✍️ Upraviť", key=f"btn_edit_t1_{i}"):
                        st.session_state[edit_key] = not st.session_state[edit_key]
                        st.rerun()
                    
                    if st.session_state[edit_key]:
                        st.markdown("---")
                        st.subheader("✏️ Upraviť dopyt")
                        with st.form(key=f"form_edit_t1_{a['id']}"):
                            novy_datum = st.text_input("Dátum", value=a.get('datum', ''))
                            novy_cas = st.text_input("Čas", value=a.get('cas', ''))
                            nove_meno = st.text_input("Meno", value=a.get('meno', ''))
                            novy_tel = st.text_input("Telefón", value=a.get('tel', ''))
                            novy_email = st.text_input("E-mail", value=a.get('email', ''))
                            nove_detaily = st.text_area("Miesto/Poznámka", value=info_mesto)
                            
                            if st.form_submit_button("Uložiť zmeny"):
                                for item in db:
                                    if item['id'] == a['id']:
                                        item['datum'] = novy_datum
                                        item['cas'] = novy_cas
                                        item['meno'] = nove_meno
                                        item['tel'] = novy_tel
                                        item['email'] = novy_email
                                        item['detaily'] = nove_detaily
                                uloz_data(db)
                                st.session_state[edit_key] = False
                                st.success("Zmeny boli uložené!")
                                st.rerun()
        
        with t2:
            schvalene = [a for a in db if a.get("stav") == "schvalene" or "stav" not in a]
            schvalene.sort(key=lambda x: x['datum'])
            for i, a in enumerate(schvalene):
                info_mesto = a.get('detaily', a.get('poznamka', 'Neuvedené'))
                kalkulacia = a.get('vypocitana_cena', 'Nenapočítaná')
                with st.expander(f"📅 {a['datum']} - {a.get('meno', 'Akcia')}"):
                    st.write(f"📞 {a.get('tel', '')} | 🕒 {a.get('cas', '')}")
                    st.write(f"💰 **Orientačná kalkulácia:** {kalkulacia}")
                    
                    st.markdown(f"""<div class="admin-detail-box"><b>Miesto/Poznámka:</b><br>{info_mesto}</div>""", unsafe_allow_html=True)
                    
                    c1, c2 = st.columns(2)
                    if c1.button("🗑️ Odstrániť", key=f"del{i}"):
                        db = [item for item in db if item['id'] != a['id']]
                        uloz_data(db); st.rerun()
                    
                    edit_key_t2 = f"edit_active_t2_{a['id']}"
                    if edit_key_t2 not in st.session_state:
                        st.session_state[edit_key_t2] = False
                        
                    if c2.button("✍️ Upraviť", key=f"btn_edit_t2_{i}"):
                        st.session_state[edit_key_t2] = not st.session_state[edit_key_t2]
                        st.rerun()
                    
                    if st.session_state[edit_key_t2]:
                        st.markdown("---")
                        st.subheader("✏️ Upraviť akciu")
                        with st.form(key=f"form_edit_t2_{a['id']}"):
                            novy_datum = st.text_input("Dátum", value=a.get('datum', ''))
                            novy_cas = st.text_input("Čas", value=a.get('cas', ''))
                            nove_meno = st.text_input("Meno / Názov", value=a.get('meno', ''))
                            novy_tel = st.text_input("Telefón", value=a.get('tel', ''))
                            novy_email = st.text_input("E-mail", value=a.get('email', ''))
                            nove_detaily = st.text_area("Miesto/Poznámka", value=info_mesto)
                            
                            if st.form_submit_button("Uložiť zmeny"):
                                for item in db:
                                    if item['id'] == a['id']:
                                        item['datum'] = novy_datum
                                        item['cas'] = novy_cas
                                        item['meno'] = nove_meno
                                        item['tel'] = novy_tel
                                        item['email'] = novy_email
                                        item['detaily'] = nove_detaily
                                uloz_data(db)
                                st.session_state[edit_key_t2] = False
                                st.success("Zmeny boli uložené!")
                                st.rerun()
        
        with t3:
            with st.form("add_manual"):
                d = st.date_input("Dátum"); m = st.text_input("Názov"); det = st.text_area("Miesto/Poznámka")
                if st.form_submit_button("Uložiť"):
                    db.append({"id": str(datetime.now().timestamp()), "datum": str(d), "meno": m, "detaily": det, "stav": "schvalene"})
                    uloz_data(db); st.success("OK"); st.rerun()

st.markdown(f'''
<div style="text-align:center; margin-top:50px; color:#ccc; line-height: 1.6;">
    <b>Podpora</b><br>
    <b>Tel. číslo:</b> 0944 757 122<br>
    <b>E-mail:</b> kollarstevo55@gmail.com
</div>
''', unsafe_allow_html=True)
