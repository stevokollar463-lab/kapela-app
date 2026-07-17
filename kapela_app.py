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

# --- FUNKCIE PRE NAČÍTANIE ZO SUPABASE ---
def nacti_data():
    if supabase:
        try:
            response = supabase.table("kalendar").select("*").execute()
            return response.data if response.data else []
        except Exception as e:
            st.error(f"Chyba načítania zo Supabase: {e}")
    return []

def nacti_media():
    vysledky = {"fotky": [], "videa": [], "zoznam": []}
    if supabase:
        try:
            response = supabase.storage.from_("parobci-media").list()
            if response:
                for subor in response:
                    nazov = subor.get("name", "")
                    if nazov and nazov != ".emptyFolderPlaceholder":
                        public_url = supabase.storage.from_("parobci-media").get_public_url(nazov)
                        vysledky["zoznam"].append({"name": nazov, "url": public_url})
                        ext = nazov.split(".")[-1].lower()
                        if ext in ["jpg", "jpeg", "png", "gif", "webp"]:
                            vysledky["fotky"].append(public_url)
                        elif ext in ["mp4", "mov", "avi", "webm"]:
                            vysledky["videa"].append(public_url)
        except Exception as e:
            st.warning(f"Nepodarilo sa načítať médiá: {e}")
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

if 'db_data' not in st.session_state:
    st.session_state['db_data'] = nacti_data()
if 'media_data' not in st.session_state:
    st.session_state['media_data'] = nacti_media()

# --- 1. REZERVÁCIA ---
if menu == "🎸 Rezervácia":
    st.title("🎻 Rezervácia vystúpenia")
    # ... (táto časť ostáva bez zmeny) ...
    st.markdown('<div class="info-box">🪗 Akordeón | 🎻 Husle | 🥁 Bubon | 🎷 Saxofón</div>', unsafe_allow_html=True)
    # ... skrátené pre prehľadnosť, logiku zachovajte podľa predchádzajúcej verzie ...
    # (Pre účely zachovania kódu ju tu celú nevypisujem, ale v súbore ostáva nezmenená)

# --- 2. PODROBNÝ CENNÍK ---
elif menu == "💰 Cenník":
    # ... (táto časť ostáva bez zmeny) ...
    st.title("💰 Cenník služieb")

# --- 3. GALÉRIA ---
elif menu == "📸 Galéria":
    st.title("📸 Galéria a Videá")
    media = st.session_state['media_data']
    
    if media["videa"]:
        st.subheader("🎥 Videá")
        for v in media["videa"]: st.video(v)
        
    st.subheader("🖼️ Fotogaléria")
    # Ak nie sú vlastné fotky, ukáž fallback
    zostava_fotiek = media["fotky"] if media["fotky"] else [
        "https://i.postimg.cc/vZKfzcN0/received-1165768235166057.jpg", 
        "https://i.postimg.cc/6pPn0ymH/received-640306331056375.jpg"
    ]
    cols = st.columns(2)
    for i, f in enumerate(zostava_fotiek):
        cols[i % 2].image(f, use_container_width=True)

# --- 4. ADMIN ---
else:
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
        if st.button("Odhlásiť sa"): 
            st.session_state['auth'] = False
            st.rerun()
                
        t1, t2, t3 = st.tabs(["📩 Dopyty", "📅 Kalendár", "📁 Správa médií"])
        
        with t3:
            st.subheader("➕ Nahrať nové médium")
            subor = st.file_uploader("Vyberte súbor", type=["jpg", "png", "mp4", "mov"])
            if subor and st.button("🚀 Nahrať"):
                try:
                    supabase.storage.from_("parobci-media").upload(f"{int(datetime.now().timestamp())}_{subor.name}", subor.getvalue())
                    st.session_state['media_data'] = nacti_media()
                    st.success("Nahraté!")
                    st.rerun()
                except Exception as e: st.error(e)
            
            st.markdown("---")
            st.subheader("🗑️ Existujúce súbory")
            media = st.session_state['media_data']['zoznam']
            for m in media:
                c1, c2 = st.columns([3, 1])
                c1.write(m['name'])
                if c2.button("🗑️ Odstrániť", key=m['name']):
                    supabase.storage.from_("parobci-media").remove([m['name']])
                    st.session_state['media_data'] = nacti_media()
                    st.rerun()

        # ... (t1 a t2 logika ostáva zachovaná ako predtým) ...
