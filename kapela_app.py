import streamlit as st
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
from pushbullet import Pushbullet
from supabase import create_client

# --- BEZPEČNÁ KONFIGURÁCIA (st.secrets) ---
PB_API_KEY = st.secrets.get("PB_API_KEY", "")
LOGIN_MENO = st.secrets.get("ADMIN_USER", "ovcanskeparobci")
LOGIN_HESLO = st.secrets.get("ADMIN_PASS", "OvcanskeParobci123")

# E-mailové nastavenia pre odosielanie cez Gmail
SENDER_EMAIL = st.secrets.get("sender_email", "parobciovcanske@gmail.com")
SENDER_PASSWORD = st.secrets.get("sender_password", "")

# Supabase konfigurácia
SUPABASE_URL = st.secrets.get("SUPABASE_URL", "")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", "")

KAPELA_FOTO_URL = "https://i.postimg.cc/T1Pkgjnw/1000027016.jpg" 

# --- NASTAVENIE CIEN ---
CENA_OSLAVA_HODINA = 130
CENA_SPRIEVOD_ZAKLAD = 300
CENA_SPRIEVOD_POLHODINA = 50  
CENA_STOLY_HODINA = 120  
CENA_APARATURA = 100      
CENA_ZA_KM = 0.50        

# --- INICIALIZÁCIA SUPABASE ---
if not SUPABASE_URL or not SUPABASE_KEY:
    st.error("⚠️ POZOR: Chýbajú SUPABASE_URL alebo SUPABASE_KEY v Secrets! Nastavte ich v Streamlit Cloud, inak sa dáta neuložia.")

@st.cache_resource
def get_supabase_client():
    try:
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        st.error(f"Nepodarilo sa vytvoriť Supabase klienta: {e}")
        return None

supabase = get_supabase_client()

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
        
        [data-testid="collapsedSidebarNoOverlay"], 
        [data-testid="stSidebar"], 
        button[data-testid="stSidebarCollapseButton"] {{
            display: none !important;
        }}
        
        h1, h2, h3, h4 {{ color: #d4af37 !important; font-family: 'Playfair Display', serif; text-shadow: 4px 4px 8px #000000; text-align: center; }}
        
        .info-box {{
            background: rgba(212, 175, 55, 0.15);
            border: 1px solid #d4af37;
            padding: 15px;
            border-radius: 15px;
            text-align: center;
            margin: 10px 0;
        }}

        .cennik-container {{
            background: rgba(0, 0, 0, 0.85);
            border: 2px solid #d4af37;
            padding: 25px;
            border-radius: 20px;
            box-shadow: 0 0 25px rgba(212, 175, 55, 0.25);
            margin-bottom: 25px;
        }}

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
        
        .admin-detail-box {{
            background-color: rgba(0, 100, 255, 0.15);
            border-left: 5px solid #0064ff;
            padding: 10px;
            margin: 10px 0;
            border-radius: 5px;
            font-size: 0.95rem;
        }}

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
        div[data-testid="stRadio"] div[role="radiogroup"] > label > div:first-child {{
            display: none !important;
        }}
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
        div[data-testid="stRadio"] div[role="radiogroup"] > label:hover {{
            background-color: rgba(212, 175, 55, 0.25) !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 15px rgba(212, 175, 55, 0.3) !important;
        }}
        div[data-testid="stRadio"] div[role="radiogroup"] > label[data-checked="true"] {{
            background-color: #d4af37 !important;
            color: #000000 !important;
            box-shadow: 0 0 18px #d4af37 !important;
            border-color: #ffffff !important;
        }}
        </style>
    """, unsafe_allow_html=True)

# --- FUNKCIE PRE NAČÍTANIE ZO SUPABASE (Použitie tvojich nových tabuliek) ---
def nacti_objednavky():
    if supabase:
        try:
            response = supabase.table("objednavky").select("*").execute()
            return response.data if response.data else []
        except Exception as e:
            st.error(f"Chyba načítania objednávok zo Supabase: {e}")
    return []

def nacti_galeriu_db():
    vysledky = {"fotky": [], "videa": []}
    if supabase:
        try:
            response = supabase.table("galeria").select("*").execute()
            data = response.data if response.data else []
            for polozka in data:
                # Rozdelenie podla stlpca typ_suboru ('foto' / 'video')
                if polozka.get("typ_suboru") == "foto":
                    vysledky["fotky"].append(polozka)
                elif polozka.get("typ_suboru") == "video":
                    vysledky["videa"].append(polozka)
        except Exception as e:
            st.warning(f"Nepodarilo sa načítať galériu z databázy: {e}")
    return vysledky

# --- NOTIFIKÁCIE ---
def posli_upozornenie(text):
    try:
        if PB_API_KEY:
            pb = Pushbullet(PB_API_KEY)
            pb.push_note("🎸 NOVÝ DOPYT", text)
            return True
    except Exception as e:
        st.error(f"⚠️ Pushbullet neodoslal správu! Chyba: {e}")
    return False

def posli_email_zakaznikovi(to_email, meno_klienta, datum_akcie, cas_akcie, typ_vystupenia, celkova_cena, detaily_miesta):
    if not to_email or "@" not in to_email or not SENDER_PASSWORD:
        return False
    try:
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = to_email
        msg['Subject'] = f"Status: Prijatie dopytu - Ovčanske Parobci ({datum_akcie})"
        
        body = f"""Dobrý deň, {meno_klienta},

ďakujeme za Váš záujem o vystúpenie našej hudobnej skupiny Ovčanske Parobci.
Vašu požiadavku sme úspešne prijali a momentálne ju spracovávame. 

Rekapitulácia Vášho dopytu:
------------------------------------------
Dátum akcie: {datum_akcie}
Čas začiatku: {cas_akcie}
Typ vystúpenia: {typ_vystupenia}
Orientačná cena: {celkova_cena}
Miesto konania a detaily: {detaily_miesta}
------------------------------------------

Čoskoro Vás budeme kontaktovať pre telefonické potvrdenie termínu a doladenie detailov.

S pozdravom,
Ľudová hudba Ovčanske Parobci
Tel. číslo: 0944 757 122
E-mail: {SENDER_EMAIL}
"""
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        text = msg.as_string()
        server.sendmail(SENDER_EMAIL, to_email, text)
        server.quit()
        return True
    except Exception as e:
        st.warning(f"Nepodarilo sa odoslať potvrdzujúci e-mail zákazníkovi: {e}")
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

# Inicializácia dát do Session State
if 'db_objednavky' not in st.session_state:
    st.session_state['db_objednavky'] = nacti_objednavky()
if 'db_galeria' not in st.session_state:
    st.session_state['db_galeria'] = nacti_galeriu_db()

# --- 1. REZERVÁCIA ---
if menu == "🎸 Rezervácia":
    st.title("🎻 Rezervácia vystúpenia")
    st.markdown('<div class="info-box">🪗 Akordeón | 🎻 Husle | 🥁 Bubon | 🎷 Saxofón</div>', unsafe_allow_html=True)
    
    st.markdown("<h4 style='text-align: center; margin-bottom: 5px; margin-top: 20px;'>Výpočet ceny vystúpenia</h4>", unsafe_allow_html=True)
    
    typ_akcie = st.selectbox(
        "Vyberte typ vystúpenia:",
        ["🎂 Rodinná oslava / Jubileum", "👰 Svadobný sprievod and odobierka", "🍻 Hranie pomedzi stoly / Posedenie"]
    )
    
    col_vstupy, col_km = st.columns(2)
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
        f"Zabezpečiť zvukovú aparatúru (aktívne reprobedne, mixpult, mikrofóny) (+{CENA_APARATURA} €)",
        value=False
    )
    
    cena_doprava = km * 2 * CENA_ZA_KM
    prplatok_aparatura = CENA_APARATURA if potrebuje_aparaturu else 0
    celkova_cena = cena_hudba + cena_doprava + prplatok_aparatura
    
    detaily_vypoctu = f"{popis_hudby}: {cena_hudba:.2f} €"
    if potrebuje_aparaturu:
        detaily_vypoctu += f" | Ozvučenie: {CENA_APARATURA:.2f} €"
    detaily_vypoctu += f" | Doprava {km*2} km celkovo: {cena_doprava:.2f} €"
    
    st.markdown(f"""
        <div class="kalkulacka-box">
            <span style="font-size: 1.1rem; color: #ccc;">Odhadovaná cena vystúpenia:</span><br>
            <span style="font-size: 2.2rem; font-weight: bold; color: #d4af37;">{celkova_cena:.2f} €</span><br>
            <small style="color: #aaa;">({detaily_vypoctu})</small>
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
        mesto_detaily = st.text_area("Presná adresa konania (mesto/sála) and iné detaily")
        
        if st.form_submit_button("ODOSLAŤ REZERVÁCIU S TOUTO CENOU"):
            db_obj = nacti_objednavky()
            
            # Kontrola duplicity pre schválené akcie na rovnaký deň
            if any(str(a['datum_akcie']) == str(datum) for a in db_obj if a.get('status') == 'Schválená'):
                st.error("Tento termín je už obsadený.")
            elif not meno or not tel:
                st.warning("Vyplňte, prosím, vaše meno and telefónne číslo.")
            else:
                txt_aparatury = "S APARATÚROU" if potrebuje_aparaturu else "BEZ aparatúry"
                vypocitana_cena_txt = f"{celkova_cena:.2f} € ({popis_hudby}, {txt_aparatury}, {km} km jednosmerne)"
                
                # Zlučujeme parametre do stĺpca typ_sluzby, aby sme nestratili žiadne dôležité informácie z dopytu
                sluzba_komplet = (
                    f"Typ: {typ_akcie} | Čas: {cas.strftime('%H:%M')} | Tel: {tel} | Email: {email} | "
                    f"Cena: {vypocitana_cena_txt} | Miesto a detaily: {mesto_detaily}"
                )
                
                nova = {
                    "meno_klienta": meno,
                    "datum_akcie": str(datum),
                    "typ_sluzby": sluzba_komplet,
                    "status": "Nová"
                }
                
                if supabase:
                    try:
                        res = supabase.table("objednavky").insert(nova).execute()
                        if res.data:
                            st.session_state['db_objednavky'] = nacti_objednavky()
                            
                            posli_upozornenie(f"Nový dopyt: {datum}\n{meno} ({tel})\nCena: {vypocitana_cena_txt}\nMiesto: {mesto_detaily}")
                            if email:
                                posli_email_zakaznikovi(email, meno, str(datum), cas.strftime('%H:%M'), typ_akcie, vypocitana_cena_txt, mesto_detaily)
                            
                            st.balloons()
                            st.success("Odoslané! Ozveme sa vám. ✅ Taktiež sme Vám odoslali potvrdzujúci e-mail.")
                        else:
                            st.error("Chyba: Dáta sa nepodarilo zapísať do databázy.")
                    except Exception as e:
                        st.error(f"Chyba zápisu do Supabase: {e}")
                else:
                    st.error("Chyba: Databáza Supabase nie je pripojená!")

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
                    <td style="padding: 12px; color: #d4af37; font-weight: bold;">{CENA_OSLAVA_HODINA} € / hodina</td>
                    <td style="padding: 12px; color: #ccc; font-size: 0.9rem;">Živé hranie na oslavách.</td>
                </tr>
                <tr style="border-bottom: 1px solid rgba(212,175,55,0.2);">
                    <td style="padding: 12px; font-weight: bold;">👰 Svadobný sprievod and odobierka</td>
                    <td style="padding: 12px; color: #d4af37; font-weight: bold;">{CENA_SPRIEVOD_ZAKLAD} € základ</td>
                    <td style="padding: 12px; color: #ccc; font-size: 0.9rem;">Do 2 hodín. Každá ďalšia polhodina +{CENA_SPRIEVOD_POLHODINA} €.</td>
                </tr>
                <tr style="border-bottom: 1px solid rgba(212,175,55,0.2);">
                    <td style="padding: 12px; font-weight: bold;">🍻 Hranie pomedzi stoly / Posedenie</td>
                    <td style="padding: 12px; color: #d4af37; font-weight: bold;">{CENA_STOLY_HODINA} € / hodina</td>
                    <td style="padding: 12px; color: #ccc; font-size: 0.9rem;">Komorné akustické hranie naživo.</td>
                </tr>
                <tr style="border-bottom: 1px solid rgba(212,175,55,0.2);">
                    <td style="padding: 12px; font-weight: bold;">🎤 Profesionálna zvuková aparatúra</td>
                    <td style="padding: 12px; color: #d4af37; font-weight: bold;">+{CENA_APARATURA} € jednorazovo</td>
                    <td style="padding: 12px; color: #ccc; font-size: 0.9rem;">Pre väčšie sály/vonku.</td>
                </tr>
                <tr>
                    <td style="padding: 12px; font-weight: bold;">🚗 Doprava (z obce Ovčie)</td>
                    <td style="padding: 12px; color: #d4af37; font-weight: bold;">{CENA_ZA_KM:.2f} € / km</td>
                    <td style="padding: 12px; color: #ccc; font-size: 0.9rem;">Počíta sa cesta tam aj späť.</td>
                </tr>
            </table>
        </div>
    """, unsafe_allow_html=True)

# --- 3. GALÉRIA (Pre verejnosť z SQL tabuľky `galeria`) ---
elif menu == "📸 Galéria":
    st.title("📸 Galéria a Videá")
    
    media = st.session_state['db_galeria']
    
    # 🎥 Zobrazenie nahraných videí
    if media["videa"]:
        st.subheader("🎥 Videá z našich vystúpení")
        col_v1, col_v2 = st.columns(2)
        for idx, p in enumerate(media["videa"]):
            video_url = p.get("url_adresa", "")
            if video_url:
                if idx % 2 == 0:
                    with col_v1: st.video(video_url)
                else:
                    with col_v2: st.video(video_url)
        st.markdown("<hr style='border-color: rgba(212,175,55,0.3);'>", unsafe_allow_html=True)
        
    # 🖼️ Zobrazenie nahraných fotiek
    st.subheader("🖼️ Fotogaléria")
    
    # Ak je prázdno v DB, dáme základné defaulty
    if media["fotky"]:
        zostava_fotiek = [p.get("url_adresa") for p in media["fotky"] if p.get("url_adresa")]
    else:
        zostava_fotiek = [
            "https://i.postimg.cc/vZKfzcN0/received-1165768235166057.jpg", 
            "https://i.postimg.cc/6pPn0ymH/received-640306331056375.jpg", 
            "https://i.postimg.cc/cLzwmrbT/received-796698713423840.jpg", 
            "https://i.postimg.cc/RZYKRND1/received-936809825229820.jpg"
        ]
    
    col_img1, col_img2 = st.columns(2)
    for idx, f in enumerate(zostava_fotiek):
        if idx % 2 == 0:
            with col_img1: st.image(f, use_container_width=True)
        else:
            with col_img2: st.image(f, use_container_width=True)

# --- 4. ADMIN (S tvojimi novými požiadavkami) ---
else:
    col_title, col_logout = st.columns([3, 1])
    with col_title:
        st.title("🔐 Administrácia")
    
    if 'auth' not in st.session_state: st.session_state['auth'] = False
    
    if not st.session_state['auth']:
        with st.form("login"):
            u = st.text_input("Meno")
            h = st.text_input("Heslo", type="password")
            if st.form_submit_button("Vstúpiť"):
                if u == LOGIN_MENO and h == LOGIN_HESLO: 
                    st.session_state['auth'] = True
                    st.rerun()
                else: 
                    st.error("Nesprávne prihlasovacie údaje!")
    else:
        with col_logout:
            st.write("") 
            if st.button("Odhlásiť sa", key="logout_btn"): 
                st.session_state['auth'] = False
                st.rerun()
                
        # ZMENENÉ: Záložky presne podľa tvojich požiadaviek
        t_obj, t_gal = st.tabs(["📩 Objednávky / Akcie", "📸 Galéria (Fotky & Videá)"])
        
        # --- ZÁLOŽKA 1: OBJEDNÁVKY / AKCIE ---
        with t_obj:
            st.subheader("📊 Správa objednávok a akcií")
            
            db_obj = nacti_objednavky()
            
            # Formulár na rýchle manuálne pridanie akcie priamo administrátorom
            with st.expander("➕ Pridať novú akciu manuálne"):
                with st.form("add_manual_admin"):
                    m_meno = st.text_input("Meno klienta / Názov akcie")
                    m_datum = st.date_input("Dátum akcie", value=datetime.today())
                    m_typ = st.text_area("Detaily (typ služby, cena, telefón, miesto...)")
                    m_status = st.selectbox("Status", ["Nová", "Schválená", "Zrušená"])
                    
                    if st.form_submit_button("Uložiť akciu"):
                        if not m_meno:
                            st.warning("Meno klienta / Názov akcie nesmie byť prázdny.")
                        else:
                            nova_manual = {
                                "meno_klienta": m_meno,
                                "datum_akcie": str(m_datum),
                                "typ_sluzby": m_typ,
                                "status": m_status
                            }
                            if supabase:
                                try:
                                    res = supabase.table("objednavky").insert(nova_manual).execute()
                                    if res.data:
                                        st.session_state['db_objednavky'] = nacti_objednavky()
                                        st.success("Akcia úspešne pridaná!")
                                        st.rerun()
                                except Exception as e:
                                    st.error(f"Chyba zápisu do Supabase: {e}")
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            if not db_obj:
                st.info("Žiadne objednávky v databáze.")
            else:
                # Rozdelíme objednávky na "Nové" a ostatné (Schválené/Zrušené)
                nove_obj = [a for a in db_obj if a.get("status") == "Nová"]
                ostatne_obj = [a for a in db_obj if a.get("status") != "Nová"]
                
                st.write(f"### 📥 Nové dopyty ({len(nove_obj)})")
                for i, o in enumerate(nove_obj):
                    with st.expander(f"🆕 {o['datum_akcie']} - {o['meno_klienta']}"):
                        st.markdown(f'<div class="admin-detail-box"><b>Informácie a detaily:</b><br>{o["typ_sluzby"]}</div>', unsafe_allow_html=True)
                        
                        c1, c2, c3 = st.columns(3)
                        if c1.button("✅ Schváliť", key=f"schval_obj_{o['id']}"):
                            if supabase:
                                try:
                                    supabase.table("objednavky").update({"status": "Schválená"}).eq("id", o['id']).execute()
                                    st.session_state['db_objednavky'] = nacti_objednavky()
                                    st.success("Objednávka schválená!")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Chyba: {e}")
                                    
                        if c2.button("❌ Zrušiť", key=f"zrus_obj_{o['id']}"):
                            if supabase:
                                try:
                                    supabase.table("objednavky").update({"status": "Zrušená"}).eq("id", o['id']).execute()
                                    st.session_state['db_objednavky'] = nacti_objednavky()
                                    st.success("Objednávka zrušená!")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Chyba: {e}")
                                    
                        if c3.button("🗑️ Vymazať", key=f"del_obj_{o['id']}"):
                            if supabase:
                                try:
                                    supabase.table("objednavky").delete().eq("id", o['id']).execute()
                                    st.session_state['db_objednavky'] = nacti_objednavky()
                                    st.success("Dopyt zmazaný!")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Chyba vymazania: {e}")
                                    
                st.write(f"### 📅 Ostatné akcie a kalendár ({len(ostatne_obj)})")
                ostatne_obj.sort(key=lambda x: x['datum_akcie'])
                for i, o in enumerate(ostatne_obj):
                    farba_statusu = "🟢" if o.get("status") == "Schválená" else "🔴"
                    with st.expander(f"{farba_statusu} {o['datum_akcie']} - {o['meno_klienta']} ({o.get('status')})"):
                        st.markdown(f'<div class="admin-detail-box"><b>Detaily:</b><br>{o["typ_sluzby"]}</div>', unsafe_allow_html=True)
                        
                        c1, c2 = st.columns(2)
                        
                        # Možnosť prepnúť status späť
                        novy_stav = "Schválená" if o.get("status") == "Zrušená" else "Zrušená"
                        if c1.button(f"Zmeniť na: {novy_stav}", key=f"switch_status_{o['id']}"):
                            if supabase:
                                try:
                                    supabase.table("objednavky").update({"status": novy_stav}).eq("id", o['id']).execute()
                                    st.session_state['db_objednavky'] = nacti_objednavky()
                                    st.success("Status zmenený!")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Chyba: {e}")
                                    
                        if c2.button("🗑️ Úplne zmazať", key=f"del_permanent_{o['id']}"):
                            if supabase:
                                try:
                                    supabase.table("objednavky").delete().eq("id", o['id']).execute()
                                    st.session_state['db_objednavky'] = nacti_objednavky()
                                    st.success("Akcia zmazaná!")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Chyba: {e}")

        # --- ZÁLOŽKA 2: GALÉRIA (FOTKY & VIDEÁ) ---
        with t_gal:
            st.subheader("🖼️ Správa galérie na webe")
            
            # Pridanie nového média do tabuľky
            st.write("#### ➕ Pridať nové médium")
            with st.form("form_pridat_galeriu"):
                url_vstup = st.text_input("Vložte priamu URL adresu súboru (napr. z PostImages, YouTube alebo iného hostingu)")
                typ_sub = st.selectbox("Typ súboru", ["foto", "video"])
                nazov_sub = st.text_input("Názov súboru (nepovinné)")
                
                if st.form_submit_button("💾 Pridať do galérie"):
                    if not url_vstup:
                        st.warning("Musíte zadať URL adresu.")
                    else:
                        nove_medium = {
                            "url_adresa": url_vstup,
                            "typ_suboru": typ_sub,
                            "nazov_suboru": nazov_sub if nazov_sub else "Súbor bez názvu"
                        }
                        if supabase:
                            try:
                                res = supabase.table("galeria").insert(nove_medium).execute()
                                if res.data:
                                    st.session_state['db_galeria'] = nacti_galeriu_db()
                                    st.success("Médium úspešne pridané do databázy! 🎉")
                                    st.rerun()
                            except Exception as e:
                                st.error(f"Chyba pri ukladaní do databázy: {e}")
            
            st.markdown("<hr style='border-color: rgba(212,175,55,0.3);'>", unsafe_allow_html=True)
            
            st.write("#### 🗑️ Zoznam médií a odstraňovanie")
            
            galeria_data = st.session_state['db_galeria']
            vsetky_media = galeria_data["fotky"] + galeria_data["videa"]
            
            if not vsetky_media:
                st.info("V galérii momentálne nie sú žiadne médiá.")
            else:
                for idx, m in enumerate(vsetky_media):
                    typ_emoji = "🖼️" if m.get("typ_suboru") == "foto" else "🎥"
                    with st.container():
                        c_img, c_txt, c_btn = st.columns([1, 2, 1])
                        
                        with c_img:
                            # Zobrazíme miniatúru pre fotku, pre video len ikonku
                            if m.get("typ_suboru") == "foto":
                                st.image(m.get("url_adresa"), width=80)
                            else:
                                st.write("🎥 *Video-odkaz*")
                                
                        with c_txt:
                            st.write(f"**{m.get('nazov_suboru', 'Súbor')}** ({m.get('typ_suboru')})")
                            st.caption(f"URL: {m.get('url_adresa')[:45]}...")
                            
                        with c_btn:
                            st.write("") # prázdne miesto pre zarovnanie
                            if st.button("❌ Vymazať", key=f"del_gal_{m['id']}"):
                                if supabase:
                                    try:
                                        supabase.table("galeria").delete().eq("id", m['id']).execute()
                                        st.session_state['db_galeria'] = nacti_galeriu_db()
                                        st.success("Súbor vymazaný z galérie!")
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"Chyba pri mazaní: {e}")
                        st.markdown("<hr style='border-color: rgba(255,255,255,0.1); margin: 5px 0;'>", unsafe_allow_html=True)
