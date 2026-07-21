import streamlit as st
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime, timedelta
from pushbullet import Pushbullet
from supabase import create_client
import calendar
import secrets
import urllib.parse

# --- BEZPEČNÁ KONFIGURÁCIA (IBA st.secrets) ---
try:
    PB_API_KEY = st.secrets["PB_API_KEY"]
    LOGIN_MENO = st.secrets["ADMIN_USER"]
    LOGIN_HESLO = st.secrets["ADMIN_PASS"]
    SENDER_EMAIL = st.secrets["sender_email"]
    SENDER_PASSWORD = st.secrets["sender_password"]
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

    # NOVÉ:
    APP_BASE_URL = st.secrets["APP_BASE_URL"]  # napr. https://moja-app.streamlit.app
    ADMIN_NOTIFY_EMAIL = st.secrets["ADMIN_NOTIFY_EMAIL"]  # admin email na notifikácie

except KeyError as e:
    st.error(f"❌ KRITICKÁ CHYBA: Chýba secret '{e.args[0]}' v Streamlit Secrets! Kontaktujte správcu.")
    st.stop()

KAPELA_FOTO_URL = "https://i.postimg.cc/T1Pkgjnw/1000027016.jpg"

CENA_OSLAVA_HODINA = 130
CENA_SPRIEVOD_ZAKLAD = 300
CENA_SPRIEVOD_POLHODINA = 50
CENA_STOLY_HODINA = 120
CENA_APARATURA = 100
CENA_ZA_KM = 0.50


@st.cache_resource
def get_supabase_client():
    try:
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        st.error(f"❌ Nepodarilo sa vytvoriť Supabase klienta: {e}")
        return None


supabase = get_supabase_client()


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

        [data-testid="stToolbar"] {{
            display: none !important;
        }}

        .stDeployButton {{
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

        .footer-buttons {{
            display: flex;
            justify-content: space-around;
            align-items: center;
            gap: 10px;
            margin-top: 60px;
            padding: 20px 0;
            border-top: 2px solid rgba(212, 175, 55, 0.3);
            position: relative;
            z-index: 10;
        }}

        .footer-btn {{
            background-color: #d4af37;
            color: black;
            border: none;
            padding: 12px 24px;
            border-radius: 25px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s ease;
            flex: 1;
            max-width: 180px;
            text-align: center;
            box-shadow: 0 4px 10px rgba(0,0,0,0.5);
        }}

        .footer-btn:hover {{
            background-color: #FFD700;
            transform: translateY(-2px);
            box-shadow: 0 6px 15px rgba(212, 175, 55, 0.4);
        }}

        .footer-btn:active {{
            transform: translateY(0px);
        }}

        .expandable-section {{
            background: rgba(0, 0, 0, 0.9);
            border: 2px solid #d4af37;
            border-radius: 15px;
            padding: 25px;
            margin-top: 20px;
            margin-bottom: 20px;
            box-shadow: 0 0 30px rgba(212, 175, 55, 0.3);
            animation: slideDown 0.3s ease-out;
        }}

        @keyframes slideDown {{
            from {{
                opacity: 0;
                transform: translateY(-20px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}

        .section-title {{
            color: #d4af37;
            font-size: 1.5rem;
            font-weight: bold;
            text-align: center;
            margin-bottom: 20px;
            border-bottom: 2px solid #d4af37;
            padding-bottom: 10px;
        }}

        .faq-item {{
            margin-bottom: 15px;
            padding-bottom: 15px;
            border-bottom: 1px solid rgba(212, 175, 55, 0.3);
        }}

        .faq-item:last-child {{
            border-bottom: none;
        }}

        .faq-otazka {{
            font-weight: bold;
            color: #d4af37;
            margin-bottom: 8px;
            font-size: 1rem;
        }}

        .faq-odpoved {{
            color: #ccc;
            line-height: 1.5;
            font-size: 0.95rem;
        }}

        .kontakt-info {{
            text-align: center;
            margin: 15px 0;
            padding: 12px;
            background: rgba(212, 175, 55, 0.1);
            border-left: 4px solid #d4af37;
            border-radius: 8px;
        }}

        .kontakt-label {{
            color: #d4af37;
            font-weight: bold;
            font-size: 1rem;
        }}

        .kontakt-value {{
            color: #fff;
            font-size: 1rem;
            margin-top: 5px;
        }}

        .recenzia-item {{
            margin-bottom: 15px;
            padding: 15px;
            background: rgba(212, 175, 55, 0.05);
            border-left: 4px solid #d4af37;
            border-radius: 8px;
        }}

        .recenzia-meno {{
            font-weight: bold;
            color: #d4af37;
            font-size: 1rem;
        }}

        .recenzia-hvezdicky {{
            color: #FFD700;
            font-size: 1.1rem;
            margin-top: 5px;
        }}

        .recenzia-text {{
            color: #ccc;
            font-style: italic;
            margin-top: 10px;
            font-size: 0.95rem;
            line-height: 1.5;
        }}

        .o-nas-box {{
            background: rgba(0, 0, 0, 0.85);
            border: 2px solid #d4af37;
            padding: 25px;
            border-radius: 15px;
            margin: 20px 0;
        }}

        .o-nas-text {{
            color: #ccc;
            line-height: 1.8;
            font-size: 1rem;
        }}

        .clenovia-box {{
            background: rgba(212, 175, 55, 0.1);
            border-left: 4px solid #d4af37;
            padding: 15px;
            margin: 10px 0;
            border-radius: 8px;
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


def nacti_data():
    if supabase:
        try:
            response = supabase.table("kalendar").select("*").execute()
            return response.data if response.data else []
        except Exception as e:
            st.error(f"Chyba načítania zo Supabase: {e}")
    return []


def nacti_recenzie():
    if supabase:
        try:
            response = supabase.table("recenzie").select("*").order("created_at", desc=True).execute()
            return response.data if response.data else []
        except Exception:
            pass
    return []


def nacti_media():
    vysledky = {"fotky": [], "videa": []}
    if supabase:
        try:
            response = supabase.storage.from_("parobci-media").list()
            if response:
                for subor in response:
                    nazov = subor.get("name", "")
                    if nazov and nazov != ".emptyFolderPlaceholder":
                        try:
                            public_url = supabase.storage.from_("parobci-media").get_public_url(nazov)
                            ext = nazov.split(".")[-1].lower()
                            if ext in ["jpg", "jpeg", "png", "gif", "webp"]:
                                vysledky["fotky"].append(public_url)
                            elif ext in ["mp4", "mov", "avi", "webm"]:
                                vysledky["videa"].append(public_url)
                        except Exception:
                            pass
        except Exception:
            pass
    return vysledky


def nacti_vsetky_media():
    subbory_list = []
    if supabase:
        try:
            response = supabase.storage.from_("parobci-media").list()
            if response:
                for subor in response:
                    nazov = subor.get("name", "")
                    if nazov and nazov != ".emptyFolderPlaceholder":
                        ext = nazov.split(".")[-1].lower()
                        typ = "Foto" if ext in ["jpg", "jpeg", "png", "gif", "webp"] else "Video" if ext in ["mp4", "mov", "avi", "webm"] else "Iný"
                        subbory_list.append({
                            "nazov": nazov,
                            "ext": ext,
                            "typ": typ,
                            "velkost": subor.get("metadata", {}).get("size", 0),
                            "vytvorene": subor.get("created_at", "")
                        })
        except Exception:
            pass
    return subbory_list


def zobraz_kalendar_obsadenosti(db_data, rok, mesiac):
    obsadene = set()
    for event in db_data:
        if event.get("stav") == "schvalene":
            try:
                d = datetime.strptime(event["datum"], "%Y-%m-%d").date()
                if d.year == rok and d.month == mesiac:
                    obsadene.add(d.day)
            except Exception:
                pass

    cal = calendar.monthcalendar(rok, mesiac)
    nazvy_dni = ["Po", "Ut", "St", "Št", "Pi", "So", "Ne"]

    html = """
    <div style="background: rgba(0,0,0,0.85); border: 2px solid #d4af37; border-radius: 12px; padding: 15px; margin: 10px 0 20px 0;">
      <h4 style="text-align:center; color:#d4af37; margin-bottom:10px;">📅 Obsadenosť termínov (X = obsadené)</h4>
      <table style="width:100%; border-collapse:collapse; text-align:center; color:white;">
        <tr>
    """
    for den in nazvy_dni:
        html += f'<th style="padding:8px; border-bottom:1px solid rgba(212,175,55,0.4); color:#d4af37;">{den}</th>'
    html += "</tr>"

    for tyzden in cal:
        html += "<tr>"
        for den in tyzden:
            if den == 0:
                html += '<td style="padding:10px; color:#555;">&nbsp;</td>'
            elif den in obsadene:
                html += '<td style="padding:10px; font-weight:bold; color:#ff4d4d;">X</td>'
            else:
                html += f'<td style="padding:10px;">{den}</td>'
        html += "</tr>"

    html += """
      </table>
      <div style="text-align:center; margin-top:10px; color:#aaa; font-size:0.9rem;">
        Červené <b>X</b> = termín je už obsadený (schválená akcia)
      </div>
    </div>
    """
    return html


def hvezdicky_html(pocet):
    return "⭐" * pocet + "☆" * (5 - pocet)


def posli_upozornenie(text):
    try:
        if PB_API_KEY:
            pb = Pushbullet(PB_API_KEY)
            pb.push_note("🎸 NOVÝ DOPYT", text)
            return True
    except Exception as e:
        st.error(f"⚠️ Pushbullet neodoslal správu! Chyba: {e}")
    return False


def send_email(to_email, subject, plain_body, html_body=None):
    if not to_email or "@" not in to_email or not SENDER_PASSWORD:
        return False
    try:
        msg = MIMEMultipart("alternative")
        msg['From'] = SENDER_EMAIL
        msg['To'] = to_email
        msg['Subject'] = subject

        msg.attach(MIMEText(plain_body, 'plain', 'utf-8'))
        if html_body:
            msg.attach(MIMEText(html_body, 'html', 'utf-8'))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, to_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        st.warning(f"Nepodarilo sa odoslať e-mail na {to_email}: {e}")
        return False


def posli_email_zakaznikovi_s_potvrdenim(to_email, meno_klienta, datum_akcie, cas_akcie, typ_vystupenia, celkova_cena, detaily_miesta, confirm_url):
    subject = f"Potvrdenie ceny dopytu - Ovčanske Parobci ({datum_akcie})"

    plain_body = f"""Dobrý deň, {meno_klienta},

ďakujeme za Váš záujem o vystúpenie našej hudobnej skupiny Ovčanske Parobci.

Rekapitulácia:
Dátum akcie: {datum_akcie}
Čas začiatku: {cas_akcie}
Typ vystúpenia: {typ_vystupenia}
Vypočítaná cena: {celkova_cena}
Miesto a detaily: {detaily_miesta}

Ak súhlasíte s cenou, potvrďte ju kliknutím na tento odkaz:
{confirm_url}

Po potvrdení Vám príde potvrdzujúci e-mail.

S pozdravom,
Ľudová hudba Ovčanske Parobci
Tel. číslo: 0944 757 122
E-mail: parobciovcanske@gmail.com
"""

    html_body = f"""
    <html>
      <body style="font-family: Arial, sans-serif; line-height:1.6;">
        <p>Dobrý deň, <b>{meno_klienta}</b>,</p>
        <p>ďakujeme za Váš záujem o vystúpenie našej hudobnej skupiny <b>Ovčanske Parobci</b>.</p>

        <h3>Rekapitulácia dopytu</h3>
        <ul>
          <li><b>Dátum akcie:</b> {datum_akcie}</li>
          <li><b>Čas začiatku:</b> {cas_akcie}</li>
          <li><b>Typ vystúpenia:</b> {typ_vystupenia}</li>
          <li><b>Vypočítaná cena:</b> {celkova_cena}</li>
          <li><b>Miesto a detaily:</b> {detaily_miesta}</li>
        </ul>

        <p>Ak súhlasíte s cenou, kliknite na tlačidlo:</p>
        <p>
          <a href="{confirm_url}" style="display:inline-block;padding:12px 20px;background:#d4af37;color:#000;text-decoration:none;border-radius:8px;font-weight:bold;">
            ✅ Potvrdiť cenu
          </a>
        </p>

        <p>Po potvrdení Vám príde potvrdzujúci e-mail.</p>

        <p>S pozdravom,<br>
        Ľudová hudba Ovčanske Parobci<br>
        Tel. číslo: 0944 757 122<br>
        E-mail: parobciovcanske@gmail.com</p>
      </body>
    </html>
    """
    return send_email(to_email, subject, plain_body, html_body)


def posli_email_o_potvrdeni_zakaznikovi(to_email, meno, datum_akcie, cena):
    subject = f"Potvrdenie prijaté - Ovčanske Parobci ({datum_akcie})"
    plain = f"""Dobrý deň, {meno},

ďakujeme, Vaše potvrdenie ceny sme úspešne prijali.

Dátum akcie: {datum_akcie}
Potvrdená cena: {cena}

Čoskoro Vás budeme kontaktovať telefonicky.

S pozdravom,
Ovčanske Parobci
"""
    html = f"""
    <html><body>
    <p>Dobrý deň, <b>{meno}</b>,</p>
    <p>ďakujeme, Vaše potvrdenie ceny sme úspešne prijali.</p>
    <ul>
      <li><b>Dátum akcie:</b> {datum_akcie}</li>
      <li><b>Potvrdená cena:</b> {cena}</li>
    </ul>
    <p>Čoskoro Vás budeme kontaktovať telefonicky.</p>
    <p>S pozdravom,<br>Ovčanske Parobci</p>
    </body></html>
    """
    return send_email(to_email, subject, plain, html)


def posli_email_adminovi_o_potvrdeni(meno, tel, email, datum_akcie, cas_akcie, cena, detaily):
    subject = f"✅ Klient potvrdil cenu - {datum_akcie}"
    plain = f"""Klient potvrdil cenu dopytu.

Meno: {meno}
Tel: {tel}
Email: {email}
Dátum: {datum_akcie}
Čas: {cas_akcie}
Cena: {cena}
Detaily: {detaily}
"""
    html = f"""
    <html><body>
    <h3>✅ Klient potvrdil cenu dopytu</h3>
    <ul>
      <li><b>Meno:</b> {meno}</li>
      <li><b>Tel:</b> {tel}</li>
      <li><b>Email:</b> {email}</li>
      <li><b>Dátum:</b> {datum_akcie}</li>
      <li><b>Čas:</b> {cas_akcie}</li>
      <li><b>Cena:</b> {cena}</li>
      <li><b>Detaily:</b> {detaily}</li>
    </ul>
    </body></html>
    """
    return send_email(ADMIN_NOTIFY_EMAIL, subject, plain, html)


def process_confirmation_from_query():
    # Zachytí klik z emailu: ?confirm_token=XYZ
    token = st.query_params.get("confirm_token", None)
    if not token:
        return

    if isinstance(token, list):
        token = token[0]

    if not supabase:
        st.error("Nepodarilo sa pripojiť k databáze.")
        return

    try:
        res = supabase.table("kalendar").select("*").eq("confirmation_token", token).limit(1).execute()
        if not res.data:
            st.error("❌ Potvrdzovací odkaz je neplatný alebo už bol použitý.")
            return

        zaznam = res.data[0]

        # Ak už potvrdené, len info
        if zaznam.get("stav") == "potvrdene_klientom":
            st.success("✅ Tento dopyt už bol potvrdený.")
            return

        # Kontrola expirácie tokenu (ak je vyplnený)
        token_expires_at = zaznam.get("token_expires_at")
        if token_expires_at:
            try:
                exp_dt = datetime.fromisoformat(token_expires_at)
                if datetime.now() > exp_dt:
                    st.error("❌ Potvrdzovací odkaz vypršal.")
                    return
            except Exception:
                pass

        update_payload = {
            "stav": "potvrdene_klientom",
            "confirmed_at": datetime.now().isoformat()
        }

        supabase.table("kalendar").update(update_payload).eq("id", zaznam["id"]).execute()

        meno = zaznam.get("meno", "Klient")
        tel = zaznam.get("tel", "")
        email = zaznam.get("email", "")
        datum_akcie = zaznam.get("datum", "")
        cas_akcie = zaznam.get("cas", "")
        cena = zaznam.get("vypocitana_cena", "Neuvedená")
        detaily = zaznam.get("detaily", "")

        # Pushbullet adminovi
        posli_upozornenie(
            f"✅ KLIENT POTVRDIL CENU\n"
            f"Dátum: {datum_akcie} {cas_akcie}\n"
            f"Meno: {meno}\n"
            f"Tel: {tel}\n"
            f"Email: {email}\n"
            f"Cena: {cena}\n"
            f"Detaily: {detaily}"
        )

        # Email adminovi + klientovi
        posli_email_adminovi_o_potvrdeni(meno, tel, email, datum_akcie, cas_akcie, cena, detaily)
        if email:
            posli_email_o_potvrdeni_zakaznikovi(email, meno, datum_akcie, cena)

        st.success("✅ Ďakujeme, cenu ste úspešne potvrdili. Budeme Vás kontaktovať.")

        # Voliteľne vyčisti query param (aby po refreshi znova nepotvrdzovalo)
        st.query_params.clear()

    except Exception as e:
        st.error(f"Chyba pri potvrdzovaní: {e}")


st.set_page_config(page_title="Ovčanske Parobci", page_icon="🎻", layout="centered", initial_sidebar_state="collapsed")
apply_style()

# DÔLEŽITÉ: spracovanie potvrdzovacieho linku hneď po načítaní appky
process_confirmation_from_query()

menu = st.radio(
    "NAVIGÁCIA",
    ["🎸 Rezervácia", "💰 Cenník", "ℹ️ O nás", "📸 Galéria", "⭐ Recenzie", "🔐 Administrácia"],
    horizontal=True,
    label_visibility="collapsed"
)

st.markdown("<br>", unsafe_allow_html=True)

if 'db_data' not in st.session_state:
    st.session_state['db_data'] = nacti_data()

# --- 1. REZERVÁCIA ---
if menu == "🎸 Rezervácia":
    st.session_state['page_id'] = 'rezaba'
    st.title("🎻 Rezervácia vystúpenia")
    st.markdown('<div class="info-box">🪗 Akordeón | 🎻 Husle | 🥁 Bubon | 🎷 Saxofón</div>', unsafe_allow_html=True)

    st.markdown("<h4 style='text-align: center; margin-bottom: 5px; margin-top: 20px;'>Nastavenie dopytu</h4>", unsafe_allow_html=True)

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

    # ÚMYSELNE SKRYTÉ:
    st.info("💡 Presná vypočítaná cena Vám príde e-mailom na potvrdenie.")

    with st.expander("📅 Zobraziť kalendár obsadenosti"):
        dnes = datetime.now().date()
        col_m1, col_m2 = st.columns(2)

        with col_m1:
            vybrany_rok = st.number_input("Rok", min_value=dnes.year, max_value=dnes.year + 3, value=dnes.year, step=1)

        with col_m2:
            vybrany_mesiac = st.selectbox("Mesiac", options=list(range(1, 13)), index=dnes.month - 1, format_func=lambda m: f"{m:02d}")

        kal_html = zobraz_kalendar_obsadenosti(st.session_state['db_data'], int(vybrany_rok), int(vybrany_mesiac))
        st.markdown(kal_html, unsafe_allow_html=True)

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

        if st.form_submit_button("ODOSLAŤ REZERVAČNÝ DOPYT"):
            db = nacti_data()

            if any(a['datum'] == str(datum) for a in db if a.get('stav') == 'schvalene'):
                st.error("❌ Tento termín je už obsadený. Prosím, vyberte si iný dátum.")
            elif not meno or not tel or not email:
                st.warning("⚠️ Vyplňte, prosím, meno, telefón a e-mail.")
            else:
                txt_aparatury = "S APARATÚROU" if potrebuje_aparaturu else "BEZ aparatúry"
                vypocitana_cena_txt = f"{celkova_cena:.2f} € ({popis_hudby}, {txt_aparatury}, {km} km jednosmerne)"

                token = secrets.token_urlsafe(32)
                exp = datetime.now() + timedelta(days=3)

                # Streamlit query link:
                confirm_url = f"{APP_BASE_URL}?confirm_token={urllib.parse.quote(token)}"

                nova = {
                    "id": str(datetime.now().timestamp()),
                    "datum": str(datum),
                    "cas": f"{cas.strftime('%H:%M')}",
                    "meno": meno,
                    "tel": tel,
                    "email": email,
                    "detaily": f"[{typ_akcie}] [Ozvučenie: {txt_aparatury}] {mesto_detaily}",
                    "vypocitana_cena": vypocitana_cena_txt,
                    "stav": "cakajuce",
                    "confirmation_token": token,
                    "token_expires_at": exp.isoformat(),
                    "confirmed_at": None
                }

                if supabase:
                    try:
                        res = supabase.table("kalendar").insert(nova).execute()
                        if res.data:
                            st.session_state['db_data'] = nacti_data()

                            # Notifikácia o novom dopyte (bez potvrdenia ešte)
                            posli_upozornenie(
                                f"Nový dopyt (čaká na potvrdenie ceny): {datum}\n"
                                f"{meno} ({tel})\nTyp: {typ_akcie}\nMiesto: {mesto_detaily}\nCena: {vypocitana_cena_txt}"
                            )

                            ok_mail = posli_email_zakaznikovi_s_potvrdenim(
                                to_email=email,
                                meno_klienta=meno,
                                datum_akcie=str(datum),
                                cas_akcie=cas.strftime('%H:%M'),
                                typ_vystupenia=typ_akcie,
                                celkova_cena=vypocitana_cena_txt,
                                detaily_miesta=mesto_detaily,
                                confirm_url=confirm_url
                            )

                            st.balloons()
                            if ok_mail:
                                st.success("✅ Dopyt bol odoslaný. Na e-mail sme Vám poslali cenu na potvrdenie.")
                            else:
                                st.warning("⚠️ Dopyt sa uložil, ale e-mail s potvrdením sa nepodarilo odoslať.")
                        else:
                            st.error("Chyba: Dáta sa nepodarilo zapísať do databázy.")
                    except Exception as e:
                        st.error(f"Chyba zápisu do Supabase: {e}")
                else:
                    st.error("Chyba: Databáza Supabase nie je pripojená!")

    # Ak chceš, sem si vlož svoju pôvodnú funkciu footeru:
    # zobraz_footer_tlacidla()

# Ostatné menu časti (Cenník, O nás, Galéria, Recenzie, Admin) môžeš nechať z pôvodného kódu.
# V administrácii odporúčam vidieť aj stav "potvrdene_klientom".
