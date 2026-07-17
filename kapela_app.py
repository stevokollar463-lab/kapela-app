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
    st.error("⚠️ POZOR: Chýbajú SUPABASE_URL alebo SUPABASE_KEY v Secrets!")

@st.cache_resource
def get_supabase_client():
    try:
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
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
            color: #ffffff;
        }}
        [data-testid="stSidebar"] {{ display: none !important; }}
        h1, h2, h3, h4 {{ color: #d4af37 !important; font-family: 'Playfair Display', serif; text-align: center; }}
        .info-box {{ background: rgba(212, 175, 55, 0.15); border: 1px solid #d4af37; padding: 15px; border-radius: 15px; text-align: center; margin: 10px 0; }}
        .cennik-container {{ background: rgba(0, 0, 0, 0.85); border: 2px solid #d4af37; padding: 25px; border-radius: 20px; margin-bottom: 25px; }}
        .kalkulacka-box {{ background: rgba(212, 175, 55, 0.25); border: 2px dashed #d4af37; padding: 20px; border-radius: 15px; text-align: center; margin: 20px 0; }}
        .stButton>button {{ background-color: #d4af37 !important; color: black !important; border-radius: 12px !important; font-weight: bold !important; width: 100%; }}
        .admin-detail-box {{ background-color: rgba(0, 100, 255, 0.15); border-left: 5px solid #0064ff; padding: 10px; margin: 10px 0; border-radius: 5px; }}
        </style>
    """, unsafe_allow_html=True)

# --- FUNKCIE ---
def nacti_data():
    if supabase:
        try:
            return supabase.table("kalendar").select("*").execute().data
        except: return []
    return []

def nacti_media():
    vysledky = {"fotky": [], "videa": []}
    if supabase:
        try:
            res = supabase.storage.from_("parobci-media").list()
            for subor in res:
                nazov = subor.get("name", "")
                if nazov and nazov != ".emptyFolderPlaceholder":
                    url = supabase.storage.from_("parobci-media").get_public_url(nazov)
                    ext = nazov.split(".")[-1].lower()
                    m = {"url": url, "name": nazov}
                    if ext in ["jpg", "jpeg", "png", "gif", "webp"]: vysledky["fotky"].append(m)
                    elif ext in ["mp4", "mov", "avi", "webm"]: vysledky["videa"].append(m)
        except: pass
    return vysledky

def posli_upozornenie(text):
    if PB_API_KEY:
        try: Pushbullet(PB_API_KEY).push_note("🎸 NOVÝ DOPYT", text)
        except: pass

def posli_email_zakaznikovi(to_email, meno_klienta, datum_akcie, cas_akcie, typ_vystupenia, celkova_cena, detaily_miesta):
    if not to_email or "@" not in to_email or not SENDER_PASSWORD: return False
    try:
        msg = MIMEMultipart()
        msg['From'], msg['To'], msg['Subject'] = SENDER_EMAIL, to_email, f"Status: Prijatie dopytu - Ovčanske Parobci ({datum_akcie})"
        body = f"Dobrý deň, {meno_klienta},\n\nVašu požiadavku sme prijali.\n\nDátum: {datum_akcie}\nCena: {celkova_cena}\n\nS pozdravom, Ovčanske Parobci"
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, to_email, msg.as_string())
        server.quit()
        return True
    except: return False

# --- APP ---
st.set_page_config(page_title="Ovčanske Parobci", layout="centered")
apply_style()

menu = st.radio("NAVIGÁCIA", ["🎸 Rezervácia", "💰 Cenník", "📸 Galéria", "🔐 Administrácia"], horizontal=True, label_visibility="collapsed")

if 'db_data' not in st.session_state: st.session_state['db_data'] = nacti_data()
if 'media_data' not in st.session_state: st.session_state['media_data'] = nacti_media()

if menu == "🎸 Rezervácia":
    st.title("🎻 Rezervácia vystúpenia")
    typ_akcie = st.selectbox("Typ vystúpenia:", ["🎂 Rodinná oslava / Jubileum", "👰 Svadobný sprievod and odobierka", "🍻 Hranie pomedzi stoly / Posedenie"])
    
    col_vstupy, col_km = st.columns(2)
    with col_vstupy:
        if "Oslava" in typ_akcie:
            h = st.slider("Dĺžka (hod)", 1, 12, 5)
            c_h = h * CENA_OSLAVA_HODINA
        elif "Svadobný" in typ_akcie:
            p = st.slider("Polhodiny navyše", 0, 10, 0)
            c_h = CENA_SPRIEVOD_ZAKLAD + (p * CENA_SPRIEVOD_POLHODINA)
        else:
            h = st.slider("Dĺžka (hod)", 1, 12, 3)
            c_h = h * CENA_STOLY_HODINA
    with col_km: km = st.slider("Vzdialenosť z Ovčieho (km jednosmerne)", 0, 300, 0, 5)
    
    ap = st.checkbox("Zabezpečiť aparatúru (+100 €)")
    celkova = c_h + (km * 2 * CENA_ZA_KM) + (CENA_APARATURA if ap else 0)
    
    st.markdown(f"### Odhadovaná cena: {celkova:.2f} €")
    
    with st.form("main_booking"):
        col1, col2 = st.columns(2)
        datum = col1.date_input("Dátum", min_value=datetime.now())
        cas = col2.time_input("Čas")
        meno = st.text_input("Meno")
        tel = st.text_input("Telefón")
        email = st.text_input("E-mail")
        detaily = st.text_area("Adresa a detaily")
        
        if st.form_submit_button("ODOSLAŤ"):
            if not meno or not tel: st.warning("Vyplňte meno a telefón!")
            else:
                vypocitana_cena_txt = f"{celkova:.2f} €"
                nova = {"datum": str(datum), "cas": str(cas), "meno": meno, "tel": tel, "email": email, "detaily": detaily, "vypocitana_cena": vypocitana_cena_txt, "stav": "cakajuce", "id": str(datetime.now().timestamp())}
                if supabase:
                    supabase.table("kalendar").insert(nova).execute()
                    posli_upozornenie(f"Nový dopyt: {datum} od {meno}")
                    posli_email_zakaznikovi(email, meno, str(datum), str(cas), typ_akcie, vypocitana_cena_txt, detaily)
                    st.success("Odoslané!")

elif menu == "📸 Galéria":
    st.title("📸 Galéria")
    media = st.session_state['media_data']
    for v in media["videa"]: st.video(v["url"])
    col1, col2 = st.columns(2)
    for i, f in enumerate(media["fotky"]):
        (col1 if i % 2 == 0 else col2).image(f["url"])

elif menu == "🔐 Administrácia":
    if 'auth' not in st.session_state: st.session_state['auth'] = False
    if not st.session_state['auth']:
        with st.form("login"):
            if st.text_input("Meno") == LOGIN_MENO and st.text_input("Heslo", type="password") == LOGIN_HESLO:
                if st.form_submit_button("Vstúpiť"): st.session_state['auth'] = True; st.rerun()
    else:
        if st.button("Odhlásiť"): st.session_state['auth'] = False; st.rerun()
        t1, t2, t3, t4 = st.tabs(["📩 Dopyty", "📅 Kalendár", "🖼️ Správa galérie", "➕ Pridať akciu"])
        
        db = nacti_data()
        with t1:
            for a in [x for x in db if x.get("stav") == "cakajuce"]:
                with st.expander(f"{a['datum']} - {a['meno']}"):
                    if st.button("Schváliť", key=f"ok{a['id']}"): supabase.table("kalendar").update({"stav": "schvalene"}).eq("id", a['id']).execute(); st.rerun()
        with t2:
            for a in [x for x in db if x.get("stav") == "schvalene"]: st.write(f"{a['datum']} | {a['meno']} | {a['detaily']}")
        with t3:
            up = st.file_uploader("Nahrať súbor", type=["jpg", "png", "mp4"])
            if up and st.button("Nahrať"): 
                supabase.storage.from_("parobci-media").upload(f"{int(datetime.now().timestamp())}_{up.name}", up.getvalue())
                st.rerun()
            st.write("Existujúce súbory:")
            for m in st.session_state['media_data']["fotky"] + st.session_state['media_data']["videa"]:
                col_n, col_d = st.columns([3, 1])
                col_n.write(m['name'])
                if col_d.button("Zmazať", key=m['name']): supabase.storage.from_("parobci-media").remove([m['name']]); st.rerun()
        with t4:
            with st.form("add_man"):
                d = st.date_input("Dátum"); t = st.time_input("Čas"); m = st.text_input("Meno"); det = st.text_area("Detaily")
                if st.form_submit_button("Uložiť"):
                    supabase.table("kalendar").insert({"datum": str(d), "cas": str(t), "meno": m, "detaily": det, "stav": "schvalene", "id": str(datetime.now().timestamp())}).execute()
                    st.success("Pridané!")
