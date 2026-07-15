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

# --- NASTAVENIE CIEN ---
CENA_OSLAVA_HODINA = 130
CENA_SPRIEVOD_ZAKLAD = 300
CENA_SPRIEVOD_POLHODINA = 50
CENA_STOLY_HODINA = 150
CENA_APARATURA = 100  # Príplatok za ozvučenie, mixpult a mikrofóny
CENA_ZA_KM = 0.50     # 0.50 € za km (zahŕňa cestu tam aj späť)

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

        /* Box pre cenník */
        .cennik-container {{
            background: rgba(0, 0, 0, 0.85);
            border: 2px solid #d4af37;
            padding: 25px;
            border-radius: 20px;
            box-shadow: 0 0 25px rgba(212, 175, 55, 0.25);
            margin-bottom: 25px;
        }}

        /* Zlatý box pre výsledok kalkulačky */
        .kalkulacka-box {{
            background: rgba(212, 175, 55, 0.25);
            border: 2px dashed #d4af37;
            padding: 20px;
            border-radius: 15px;
            text-align: center;
            margin: 20px 0;
            box-shadow: 0 0 15px rgba(212, 175, 55, 0.20);
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

# MODERNÉ HORNÉ NAVIGAČNÉ MENU (Rezervácia, Cenník, Galéria, Admin)
menu = st.radio(
    "NAVIGÁCIA", 
    ["🎸 Rezervácia", "💰 Cenník", "📸 Galéria", "🔐 Administrácia"], 
    horizontal=True,
    label_visibility="collapsed"
)

st.markdown("<br>", unsafe_allow_html=True)

# --- 1. REZERVÁCIA (S kalkulačkou a aparatúrou) ---
if menu == "🎸 Rezervácia":
    st.title("🎻 Rezervácia vystúpenia")
    st.markdown('<div class="info-box">🪗 Akordeón | 🎻 Husle | 🥁 Bubon | 🎷 Saxofón</div>', unsafe_allow_html=True)
    
    # --- INTERAKTÍVNA KALKULAČKA (MIMO FORMULÁRA) ---
    st.markdown("<h4 style='text-align: center; margin-bottom: 5px; margin-top: 20px;'>Výpočet ceny vystúpenia</h4>", unsafe_allow_html=True)
    
    # Výber typu akcie
    typ_akcie = st.selectbox(
        "Vyberte typ vystúpenia:",
        ["🎂 Rodinná oslava / Jubileum", "👰 Svadobný sprievod a odobierka", "🍻 Hranie pomedzi stoly / Posedenie"]
    )
    
    col_vstupy, col_km = st.columns(2)
    
    cena_hudba = 0
    popis_hudby = ""
    
    with col_vstupy:
        if typ_akcie == "🎂 Rodinná oslava / Jubileum":
            hodiny = st.slider("Dĺžka hrania (v hodinách)", min_value=1, max_value=12, value=5, key="hours_oslava")
            cena_hudba = hodiny * CENA_OSLAVA_HODINA
            popis_hudby = f"Rodinná oslava ({hodiny} hod.)"
            
        elif typ_akcie == "👰 Svadobný sprievod a odobierka":
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
    
    # ZAŠKRTÁVACIE POLÍČKO PRE APARATÚRU
    potrebuje_aparaturu = st.checkbox(
        f"Zabezpečiť zvukovú aparatúru (aktívne reprobedne, mixpult, mikrofóny) (+{CENA_APARATURA} €)",
        value=False,
        help="Zvoľte, ak sa akcia koná vo väčšej sále alebo vonku a je potrebné, aby sme boli ozvučení."
    )
    
    # Výpočet dopravy a celkovej ceny
    cena_doprava = km * 2 * CENA_ZA_KM
    prplatok_aparatura = CENA_APARATURA if potrebuje_aparaturu else 0
    celkova_cena = cena_hudba + cena_doprava + prplatok_aparatura
    
    # Formátovanie popisu pre prehľadnosť
    detaily_vypoctu = f"{popis_hudby}: {cena_hudba:.2f} €"
    if potrebuje_aparaturu:
        detaily_vypoctu += f" | Ozvučenie: {CENA_APARATURA:.2f} €"
    detaily_vypoctu += f" | Doprava {km*2} km celkovo: {cena_doprava:.2f} €"
    
    # Zobrazenie ceny v reálnom čase
    st.markdown(f"""
        <div class="kalkulacka-box">
            <span style="font-size: 1.1rem; color: #ccc;">Odhadovaná cena vystúpenia:</span><br>
            <span style="font-size: 2.2rem; font-weight: bold; color: #d4af37;">{celkova_cena:.2f} €</span><br>
            <small style="color: #aaa;">({detaily_vypoctu})</small>
        </div>
    """, unsafe_allow_html=True)
    
    # --- SAMOTNÝ REZERVAČNÝ FORMULÁR ---
    with st.form("main_booking"):
        st.subheader("📩 Rezervačný dopyt")
        
        col1, col2 = st.columns(2)
        with col1: 
            datum = st.date_input("Dátum akcie", min_value=datetime.now())
        with col2: 
            cas = st.time_input("Čas začiatku")
            
        # OSOBNÉ ÚDAJE
        meno = st.text_input("Meno a priezvisko")
        tel = st.text_input("Telefónne číslo")
        email = st.text_input("E-mail")
        mesto_detaily = st.text_area("Presná adresa konania (mesto/sála) and iné detaily")
        
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
            <h3 style="margin-top: 0; padding-top: 20px; color: #d4af37; text-align: center;">Naše sadzby (sme 5-členná kapela)</h3>
            <table style="width: 100%; color: #fff; border-collapse: collapse; margin-top: 20px;">
                <tr style="border-bottom: 2px solid #d4af37; text-align: left;">
                    <th style="padding: 12px; color: #d4af37;">Služba</th>
                    <th style="padding: 12px; color: #d4af37;">Cena</th>
                    <th style="padding: 12px; color: #d4af37;">Poznámka</th>
                </tr>
                <tr style="border-bottom: 1px solid rgba(212,175,55,0.2);">
                    <td style="padding: 12px; font-weight: bold;">🎂 Rodinná oslava / Jubileum</td>
                    <td style="padding: 12px; color: #d4af37; font-weight: bold;">130 € / hodina</td>
                    <td style="padding: 12px; color: #ccc; font-size: 0.9rem;">Živé hranie na oslavách, narodeninách, jubileách.</td>
                </tr>
                <tr style="border-bottom: 1px solid rgba(212,175,55,0.2);">
                    <td style="padding: 12px; font-weight: bold;">👰 Svadobný sprievod a odobierka</td>
                    <td style="padding: 12px; color: #d4af37; font-weight: bold;">300 € základ</td>
                    <td style="padding: 12px; color: #ccc; font-size: 0.9rem;">Základ do 2 hodín. Každá ďalšia začatá polhodina je +50 €.</td>
                </tr>
                <tr style="border-bottom: 1px solid rgba(212,175,55,0.2);">
                    <td style="padding: 12px; font-weight: bold;">🍻 Hranie pomedzi stoly / Posedenie</td>
                    <td style="padding: 12px; color: #d4af37; font-weight: bold;">150 € / hodina</td>
                    <td style="padding: 12px; color: #ccc; font-size: 0.9rem;">Komorné akustické hranie naživo priamo medzi hosťami.</td>
                </tr>
                <tr style="border-bottom: 1px solid rgba(212,175,55,0.2);">
                    <td style="padding: 12px; font-weight: bold;">🎤 Profesionálna zvuková aparatúra</td>
                    <td style="padding: 12px; color: #d4af37; font-weight: bold;">+{CENA_APARATURA} € jednorazovo</td>
                    <td style="padding: 12px; color: #ccc; font-size: 0.9rem;">Aktívne reprobedne, mixpult a mikrofóny (pre väčšie sály/vonku).</td>
                </tr>
                <tr>
                    <td style="padding: 12px; font-weight: bold;">🚗 Doprava (z obce Ovčie)</td>
                    <td style="padding: 12px; color: #d4af37; font-weight: bold;">0.50 € / km</td>
                    <td style="padding: 12px; color: #ccc; font-size: 0.9rem;">Suma zahŕňa kompletnú cestu tam aj späť.</td>
                </tr>
            </table>
            <div style="padding: 20px; text-align: center; color: #aaa; font-size: 0.85rem;">
                * Ceny sú konečné pre celú našu 5-člennú zostavu (akordeóny, husle, saxofón, bubon).
            </div>
        </div>
        <div style="text-align: center; margin-top: 20px;">
            <p style="font-size: 1.1rem; color: #ccc;">Chcete si presne vypočítať cenu pre vaše podujatie?</p>
            <p>Prejdite hore na záložku <b>🎸 Rezervácia</b>, kde si zvolíte typ akcie a kalkulačka vám hneď napočíta presnú cenu.</p>
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
                    st.write(f"💰 **Vypočítaná cena na webe:** {kalkulacia}")
                    
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
