import streamlit as st
import json
import os
from datetime import datetime
from pushbullet import Pushbullet

# --- KONFIGURÁCIA ---
DB_FILE = "kalendar_kapely.json"
PB_API_KEY = "o.Lu0KSVq6YmpdGQU7oDoSpr5fEemwdDHL"  # Sem vlož svoj overený kľúč z Pushbulletu
LOGIN_MENO = "ovcanskeparobci"
LOGIN_HESLO = "OvcanskeParobci123"  # Sem si napíš svoje bezpečné heslo

# HLAVNÁ FOTKA POZADIA
KAPELA_FOTO_URL = "https://i.postimg.cc/T1Pkgjnw/1000027016.jpg" 

# --- NASTAVENIE CIEN ---
CENA_OSLAVA_HODINA = 130
CENA_SPRIEVOD_ZAKLAD = 300
CENA_SPRIEVOD_POLHODINA = 50
CENA_STOLY_HODINA = 120  
CENA_APARATURA = 100     
CENA_ZA_KM = 0.50        

# --- DIZAJN A MOBILNÁ OPTIMALIZÁCIA ---
def apply_style():
    st.markdown(f"""
        <style>
        /* Hlavné pozadie s tmavým prekrytím pre lepší kontrast */
        .stApp {{
            background: linear-gradient(rgba(0, 0, 0, 0.85), rgba(0, 0, 0, 0.85)), 
                        url("{KAPELA_FOTO_URL}");
            background-size: cover;
            background-position: center center;
            background-attachment: fixed;
            image-rendering: -webkit-optimize-contrast;
            color: #ffffff !important;
        }}
        
        /* Zaistenie čitateľnosti bežných textov, ktoré Streamlit generuje */
        .stApp p, .stApp span, .stApp label, .stApp li {{
            color: #ffffff !important;
            text-shadow: 1px 1px 3px #000000 !important;
            font-weight: 500 !important;
        }}
        
        /* Skrytie nepotrebného bočného menu */
        [data-testid="collapsedSidebarNoOverlay"], 
        [data-testid="stSidebar"], 
        button[data-testid="stSidebarCollapseButton"] {{
            display: none !important;
        }}
        
        /* Nadpisy optimalizované pre mobil s výrazným čiernym tieňom */
        h1 {{ 
            color: #d4af37 !important; 
            font-family: 'Playfair Display', serif; 
            text-shadow: 3px 3px 8px #000000 !important; 
            text-align: center;
            font-size: calc(1.8rem + 1vw) !important;
        }}
        h2, h3, h4 {{ 
            color: #d4af37 !important; 
            font-family: 'Playfair Display', serif; 
            text-shadow: 2px 2px 6px #000000 !important; 
            text-align: center; 
        }}
        
        /* Boxíky s tmavým pozadím, aby písmo nesplývalo */
        .info-box {{
            background: rgba(0, 0, 0, 0.8) !important;
            border: 2px solid #d4af37;
            padding: 15px;
            border-radius: 12px;
            text-align: center;
            margin: 10px 0;
            font-size: 1.0rem;
            color: #ffffff !important;
            box-shadow: 0 4px 10px rgba(0,0,0,0.5);
        }}

        .cennik-container {{
            background: rgba(0, 0, 0, 0.9) !important;
            border: 2px solid #d4af37;
            padding: 15px;
            border-radius: 15px;
            box-shadow: 0 5px 20px rgba(0, 0, 0, 0.8);
            margin-bottom: 20px;
        }}

        /* Zaistenie, že sa tabuľka na mobile dá posúvať do strán a nerozhádže sa */
        .table-responsive {{
            display: block;
            width: 100%;
            overflow-x: auto;
            -webkit-overflow-scrolling: touch;
        }}

        /* Kalkulačka s tmavým podkladom kvôli čitateľnosti */
        .kalkulacka-box {{
            background: rgba(0, 0, 0, 0.85) !important;
            border: 2px dashed #d4af37;
            padding: 20px;
            border-radius: 12px;
            text-align: center;
            margin: 15px 0;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.7);
        }}

        /* Formuláre musia byť dostatočne tmavé */
        .stForm {{ 
            background-color: rgba(0, 0, 0, 0.9) !important; 
            border: 2px solid #d4af37 !important; 
            border-radius: 15px; 
            padding: 20px !important; 
            box-shadow: 0 10px 25px rgba(0,0,0,0.7) !important;
        }}
        
        /* Vylepšenie textových polí (vstupov) pre lepšiu čitateľnosť */
        .stForm input, .stForm textarea {{
            background-color: rgba(30, 30, 30, 0.9) !important;
            color: #ffffff !important;
            border: 1px solid #d4af37 !important;
        }}
        
        .stButton>button {{ 
            background-color: #d4af37 !important; 
            color: black !important; 
            border-radius: 10px !important; 
            font-weight: bold !important; 
            width: 100%; 
            padding: 12px !important;
            box-shadow: 0 4px 10px rgba(0,0,0,0.4) !important;
            border: none !important;
        }}
        
        /* Mobilné prispôsobenie pre horné tlačidlá (NAVIGÁCIA) */
        div[data-testid="stRadio"] {{
            background: transparent !important;
            padding: 5px 0 !important;
        }}
        div[data-testid="stRadio"] > div[role="radiogroup"] {{
            display: flex !important;
            flex-direction: row !important;
            justify-content: center !important;
            flex-wrap: wrap !important;
            gap: 8px !important;
        }}
        div[data-testid="stRadio"] div[role="radiogroup"] > label > div:first-child {{
            display: none !important;
        }}
        div[data-testid="stRadio"] div[role="radiogroup"] > label {{
            background-color: rgba(0, 0, 0, 0.9) !important;
            border: 2px solid #d4af37 !important;
            color: #ffffff !important;
            padding: 8px 16px !important;
            border-radius: 20px !important;
            cursor: pointer !important;
            transition: all 0.2s ease !important;
            font-weight: bold !important;
            text-align: center !important;
            box-shadow: 0 4px 8px rgba(0,0,0,0.6) !important;
            font-size: 0.85rem !important;
            flex-grow: 1;
            max-width: 45%; /* Na mobile sa zoradia pekne 2 a 2 vedľa seba */
        }}
        @media (min-width: 600px) {{
            div[data-testid="stRadio"] div[role="radiogroup"] > label {{
                max-width: unset !important;
                font-size: 0.95rem !important;
            }}
        }}
        div[data-testid="stRadio"] div[role="radiogroup"] > label:hover {{
            background-color: rgba(212, 175, 55, 0.25) !important;
        }}
        div[data-testid="stRadio"] div[role="radiogroup"] > label[data-checked="true"] {{
            background-color: #d4af37 !important;
            color: #000000 !important;
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
    except Exception as e:
        st.error(f"⚠️ Pushbullet neodoslal správu! Chyba: {e}")
        return False

# --- ŠTART APP ---
st.set_page_config(page_title="Ovčanske Parobci", page_icon="🎻", layout="centered")
apply_style()

menu = st.radio(
    "NAVIGÁCIA", 
    ["🎸 Rezervácia", "💰 Cenník", "📸 Galéria", "🔐 Administrácia"], 
    horizontal=True,
    label_visibility="collapsed"
)

st.markdown("<br>", unsafe_allow_html=True)

# --- 1. REZERVÁCIA ---
if menu == "🎸 Rezervácia":
    st.title("🎻 Rezervácia vystúpenia")
    st.markdown('<div class="info-box">🪗 Akordeón | 🎻 Husle | 🥁 Bubon | 🎷 Saxofón</div>', unsafe_allow_html=True)
    
    st.markdown("<h4 style='text-align: center; margin-bottom: 5px; margin-top: 20px;'>Výpočet ceny vystúpenia</h4>", unsafe_allow_html=True)
    
    typ_akcie = st.selectbox(
        "Vyberte typ vystúpenia:",
        ["🎂 Rodinná oslava / Jubileum", "👰 Svadobný sprievod and odobierka", "🍻 Hranie pomedzi stoly / Posedenie"]
    )
    
    col_vstupy, col_km = st.columns([1, 1])
    cena_hudba = 0
    popis_hudby = ""
    
    with col_vstupy:
        if typ_akcie == "🎂 Rodinná oslava / Jubileum":
            hodiny = st.slider("Dĺžka hrania (v hodinách)", min_value=1, max_value=12, value=5, key="hours_oslava")
            cena_hudba = hodiny * CENA_OSLAVA_HODINA
            popis_hudby = f"Rodinná oslava ({hodiny} hod.)"
            
        elif typ_akcie == "👰 Svadobný sprievod and odobierka":
            st.info("Základná cena zahŕňa sprievod do 2 hodín (akusticky).")
            polhodiny_navyse = st.slider("Čas navyše (počet začatých polhodín)", min_value=0, max_value=10, value=0, key="extra_sprievod")
            cena_hudba = CENA_SPRIEVOD_ZAKLAD + (polhodiny_navyse * CENA_SPRIEVOD_POLHODINA)
            if polhodiny_navyse > 0:
                popis_hudby = f"Svadobný sprievod (2 hod. + {polhodiny_navyse}x polhodina navyše)"
            else:
                popis_hudby = "Svadobný sprievod (základ do 2 hod.)"
                
        elif typ_akcie == "🍻 Hranie pomedzi stoly / Posedenie":
            hodiny = st.slider("Dĺžka hrania (v hodinách)", min_value=1, max_value=12, value=3, key="hours_stoly")
            cena_hudba = hodiny * CENA_STOLY_HODINA
            popis_hudby = f"Hranie pomedzi stoly ({hodiny} hod.)"

    with col_km:
        km = st.slider("Vzdialenosť z obce Ovčie (v km jednosmerne)", min_value=0, max_value=300, value=0, step=5, key="calc_km")
    
    potrebuje_aparaturu = st.checkbox(
        f"Zabezpečiť zvukovú aparatúru (+{CENA_APARATURA} €)",
        value=False,
        help="Zvoľte, ak sa akcia koná vo väčšej sále alebo vonku a je potrebné ozvučenie."
    )
    
    cena_doprava = km * 2 * CENA_ZA_KM
    prplatok_aparatura = CENA_APARATURA if potrebuje_aparaturu else 0
    celkova_cena = cena_hudba + cena_doprava + prplatok_aparatura
    
    detaily_vypoctu = f"{popis_hudby}: {cena_hudba:.2f} €"
    if potrebuje_aparaturu:
        detaily_vypoctu += f" | Ozvučenie: {CENA_APARATURA:.2f} €"
    detaily_vypoctu += f" | Doprava: {cena_doprava:.2f} €"
    
    st.markdown(f"""
        <div class="kalkulacka-box">
            <span style="font-size: 1.1rem; color: #eee; text-shadow: 1px 1px 2px #000;">Odhadovaná cena vystúpenia:</span><br>
            <span style="font-size: 2.1rem; font-weight: bold; color: #d4af37; text-shadow: 2px 2px 4px #000;">{celkova_cena:.2f} €</span><br>
            <small style="color: #ddd; display: block; margin-top: 5px; text-shadow: 1px 1px 2px #000;">({detaily_vypoctu})</small>
        </div>
    """, unsafe_allow_html=True)
    
    with st.form("main_booking"):
        st.subheader("📩 Rezervačný dopyt")
        
        col1, col2 = st.columns(2)
        with col1: 
            datum = st.date_input("Dátum akcie", min_value=datetime.now())
        with col2: 
            cas = st.time_input("Čas začiatku")
            
        meno = st.text_input("Meno a priezvisko")
        tel = st.text_input("Telefónne číslo")
        email = st.text_input("E-mail")
        mesto_detaily = st.text_area("Presná adresa konania (mesto/sála) a iné detaily")
        
        if st.form_submit_button("ODOSLAŤ REZERVÁCIU S TOUTO CENOU"):
            db = nacti_data()
            if any(a['datum'] == str(datum) for a in db):
                st.error("Tento termín je už obsadený.")
            elif not meno or not tel:
                st.warning("Vyplňte, prosím, vaše meno a telefónne číslo.")
            else:
                txt_aparatury = "S APARATÚROU" if potrebuje_aparaturu else "BEZ aparatúry"
                vypocitana_cena_txt = f"{celkova_cena:.2f} € ({popis_hudby}, {txt_aparatury}, {km} km jednosmerne)"
                
                nova = {
                    "id": str(datetime.now().timestamp()), 
                    "datum": str(datum), 
                    "cas": f"{cas.strftime('%H:%M')}",
                    "meno": meno, 
                    "tel": tel, 
                    "email": email, 
                    "detaily": f"[{typ_akcie}] [Ozvučenie: {txt_aparatury}] {mesto_detaily}", 
                    "vypocitana_cena": vypocitana_cena_txt,  
                    "stav": "cakajuce"
                }
                db.append(nova); uloz_data(db)
                posli_upozornenie(f"Nový dopyt: {datum}\n{meno} ({tel})\nTyp: {typ_akcie} ({txt_aparatury})\nMiesto: {mesto_detaily}\nCena: {vypocitana_cena_txt}")
                st.balloons(); st.success("Odoslané! Ozveme sa vám. ✅")

# --- 2. PODROBNÝ CENNÍK ---
elif menu == "💰 Cenník":
    st.title("💰 Cenník služieb")
    
    st.markdown(f"""
        <div class="cennik-container">
            <h3 style="margin-top: 0; padding-top: 10px; color: #d4af37; text-align: center; font-size: 1.3rem;">Naše sadzby (sme 5-členná kapela)</h3>
            <div class="table-responsive">
                <table style="width: 100%; color: #fff; border-collapse: collapse; margin-top: 15px; font-size: 0.95rem; min-width: 500px;">
                    <tr style="border-bottom: 2px solid #d4af37; text-align: left;">
                        <th style="padding: 10px; color: #d4af37; text-shadow: 1px 1px 2px #000;">Služba</th>
                        <th style="padding: 10px; color: #d4af37; text-shadow: 1px 1px 2px #000;">Cena</th>
                        <th style="padding: 10px; color: #d4af37; text-shadow: 1px 1px 2px #000;">Poznámka</th>
                    </tr>
                    <tr style="border-bottom: 1px solid rgba(212,175,55,0.3);">
                        <td style="padding: 10px; font-weight: bold; text-shadow: 1px 1px 2px #000;">🎂 Rodinná oslava / Jubileum</td>
                        <td style="padding: 10px; color: #d4af37; font-weight: bold; text-shadow: 1px 1px 2px #000;">130 € / hod.</td>
                        <td style="padding: 10px; color: #fff; font-size: 0.85rem; text-shadow: 1px 1px 2px #000;">Živé hranie na oslavách, narodeninách, jubileách.</td>
                    </tr>
                    <tr style="border-bottom: 1px solid rgba(212,175,55,0.3);">
                        <td style="padding: 10px; font-weight: bold; text-shadow: 1px 1px 2px #000;">👰 Svadobný sprievod</td>
                        <td style="padding: 10px; color: #d4af37; font-weight: bold; text-shadow: 1px 1px 2px #000;">300 € základ</td>
                        <td style="padding: 10px; color: #fff; font-size: 0.85rem; text-shadow: 1px 1px 2px #000;">Do 2 hodín. Každá ďalšia začatá polhodina +50 €.</td>
                    </tr>
                    <tr style="border-bottom: 1px solid rgba(212,175,55,0.3);">
                        <td style="padding: 10px; font-weight: bold; text-shadow: 1px 1px 2px #000;">🍻 Hranie pomedzi stoly</td>
                        <td style="padding: 10px; color: #d4af37; font-weight: bold; text-shadow: 1px 1px 2px #000;">{CENA_STOLY_HODINA} € / hod.</td>
                        <td style="padding: 10px; color: #fff; font-size: 0.85rem; text-shadow: 1px 1px 2px #000;">Komorné akustické hranie naživo priamo medzi hosťami.</td>
                    </tr>
                    <tr style="border-bottom: 1px solid rgba(212,175,55,0.3);">
                        <td style="padding: 10px; font-weight: bold; text-shadow: 1px 1px 2px #000;">🎤 Ozvučovacia aparatúra</td>
                        <td style="padding: 10px; color: #d4af37; font-weight: bold; text-shadow: 1px 1px 2px #000;">+{CENA_APARATURA} €</td>
                        <td style="padding: 10px; color: #fff; font-size: 0.85rem; text-shadow: 1px 1px 2px #000;">Aktívne reprobedne, mixpult a mikrofóny.</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; font-weight: bold; text-shadow: 1px 1px 2px #000;">🚗 Doprava (z obce Ovčie)</td>
                        <td style="padding: 10px; color: #d4af37; font-weight: bold; text-shadow: 1px 1px 2px #000;">0.50 € / km</td>
                        <td style="padding: 10px; color: #fff; font-size: 0.85rem; text-shadow: 1px 1px 2px #000;">Zahŕňa kompletnú cestu tam aj späť.</td>
                    </tr>
                </table>
            </div>
            <div style="padding: 15px; text-align: center; color: #ddd; font-size: 0.85rem; text-shadow: 1px 1px 2px #000;">
                * Ceny sú konečné pre celú našu 5-člennú zostavu.
            </div>
        </div>
    """, unsafe_allow_html=True)

# --- 3. GALÉRIA ---
elif menu == "📸 Galéria":
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
    col_title, col_logout = st.columns([2, 1])
    with col_title:
        st.title("🔐 Admin")
    
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
                    st.write(f"💰 **Vypočítaná cena na webe:** {kalkulacia}")
                    st.markdown(f"""<div class="info-box"><b>Miesto a detaily:</b><br>{info_mesto}</div>""", unsafe_allow_html=True)
                    
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
                    st.markdown(f"""<div class="info-box"><b>Miesto/Poznámka:</b><br>{info_mesto}</div>""", unsafe_allow_html=True)
                    
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
<div style="text-align:center; margin-top:50px; color:#fff; line-height: 1.6; font-size: 0.95rem; text-shadow: 1px 1px 3px #000; background: rgba(0,0,0,0.8); padding: 15px; border-radius: 10px; border: 1px solid #d4af37;">
    <b>Podpora</b><br>
    <b>Tel. číslo:</b> 0944 757 122<br>
    <b>E-mail:</b> kollarstevo55@gmail.com
</div>
''', unsafe_allow_html=True)
