# app.py - CELÝ KÓD

import streamlit as st
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime, timedelta
from pushbullet import Pushbullet
from supabase import create_client
import json
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
    APP_BASE_URL = st.secrets["APP_BASE_URL"]
    ADMIN_NOTIFY_EMAIL = st.secrets["ADMIN_NOTIFY_EMAIL"]
except KeyError as e:
    st.error(f"❌ KRITICKÁ CHYBA: Chýba secret '{e.args[0]}' v Streamlit Secrets! Kontaktujte správcu.")
    st.stop()

KAPELA_FOTO_URL = "https://i.postimg.cc/T1Pkgjnw/1000027016.jpg"

# UPRAVENÉ CENY:
CENA_OSLAVA_HODINA = 120
CENA_SPRIEVOD_ZAKLAD = 250
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
            from {{ opacity: 0; transform: translateY(-20px); }}
            to {{ opacity: 1; transform: translateY(0); }}
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

        .stForm {{
            background-color: rgba(0, 0, 0, 0.8) !important;
            border: 2px solid #d4af37 !important;
            border-radius: 20px;
            padding: 30px;
        }}

        .stButton>button {{
            background-color: #d4af37 !important;
            color: black !important;
            border-radius: 12px !important;
            font-weight: bold !important;
            width: 100%;
        }}

        .admin-detail-box {{
            background-color: rgba(0, 100, 255, 0.15);
            border-left: 5px solid #0064ff;
            padding: 10px;
            margin: 10px 0;
            border-radius: 5px;
            font-size: 0.95rem;
        }}

        /* Floating chat */
        .chat-fab-wrap {{
            position: fixed;
            right: 18px;
            bottom: 18px;
            z-index: 99999;
        }}
        .chat-panel-wrap {{
            position: fixed;
            right: 18px;
            bottom: 78px;
            width: 360px;
            max-width: calc(100vw - 24px);
            z-index: 99999;
            background: rgba(0,0,0,.94);
            border: 2px solid #d4af37;
            border-radius: 14px;
            padding: 8px;
            box-shadow: 0 8px 30px rgba(0,0,0,.5);
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


def render_floating_chat():
    if "chat_open" not in st.session_state:
        st.session_state.chat_open = False
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = [
            {"role": "assistant", "content": "Ahoj 👋 Som asistent kapely Ovčanske Parobci. Ako ti môžem pomôcť?"}
        ]

    st.markdown('<div class="chat-fab-wrap">', unsafe_allow_html=True)
    if st.button("💬 Chat", key="chat_fab_btn"):
        st.session_state.chat_open = not st.session_state.chat_open
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    if st.session_state.chat_open:
        st.markdown('<div class="chat-panel-wrap">', unsafe_allow_html=True)
        st.markdown("### 💬 Rýchly chat")

        for m in st.session_state.chat_messages[-20:]:
            with st.chat_message(m["role"]):
                st.write(m["content"])

        user_text = st.chat_input("Napíš správu...")
        if user_text:
            st.session_state.chat_messages.append({"role": "user", "content": user_text})
            txt = user_text.lower()

            if "cena" in txt:
                answer = "Cenník nájdeš v sekcii 💰 Cenník. Ak chceš, pomôžem ti orientačne vypočítať cenu."
            elif "kontakt" in txt or "telefon" in txt or "tel" in txt:
                answer = "Kontakt: 📞 0944 757 122 | ✉️ parobciovcanske@gmail.com"
            elif "term" in txt or "rezerv" in txt:
                answer = "Termín si vieš poslať cez sekciu 🎸 Rezervácia. Po odoslaní príde potvrdenie na e-mail."
            elif "galer" in txt or "video" in txt or "foto" in txt:
                answer = "Pozri sekciu 📸 Galéria, tam sú naše fotky a videá."
            else:
                answer = "Ďakujeme za správu 🙌 Napíš prosím, či ťa zaujíma cena, voľný termín alebo kontakt."

            st.session_state.chat_messages.append({"role": "assistant", "content": answer})
            st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)


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
        st.warning(f"Nepodarilo sa odoslať e-mail: {e}")
        return False


def process_confirmation_from_query():
    token = st.query_params.get("confirm_token", None)
    if not token:
        return

    if isinstance(token, list):
        token = token[0]

    if not supabase:
        st.error("Chyba: Databáza Supabase nie je pripojená!")
        return

    try:
        res = supabase.table("kalendar").select("*").eq("confirmation_token", token).limit(1).execute()
        if not res.data:
            st.error("❌ Potvrdzovací odkaz je neplatný alebo už bol použitý.")
            return

        zaznam = res.data[0]

        if zaznam.get("klient_potvrdil_cenu") is True:
            st.success("✅ Tento dopyt už bol potvrdený klientom.")
            return

        token_expires_at = zaznam.get("token_expires_at")
        if token_expires_at:
            try:
                if datetime.now() > datetime.fromisoformat(token_expires_at):
                    st.error("❌ Potvrdzovací odkaz vypršal.")
                    return
            except Exception:
                pass

        supabase.table("kalendar").update({
            "klient_potvrdil_cenu": True,
            "confirmed_at": datetime.now().isoformat()
        }).eq("id", zaznam["id"]).execute()

        st.success("✅ Ďakujeme, cenu ste úspešne potvrdili.")
        st.query_params.clear()

    except Exception as e:
        st.error(f"Chyba pri potvrdzovaní: {e}")


def zobraz_footer_tlacidla():
    col1, col2, col3 = st.columns(3)
    with col1:
        st.button("❓ FAQ", key=f"faq_{st.session_state.get('page_id','main')}", use_container_width=True)
    with col2:
        st.button("⭐ RECENZIE", key=f"rec_{st.session_state.get('page_id','main')}", use_container_width=True)
    with col3:
        st.button("📞 KONTAKT", key=f"kon_{st.session_state.get('page_id','main')}", use_container_width=True)


st.set_page_config(page_title="Ovčanske Parobci", page_icon="🎻", layout="centered", initial_sidebar_state="collapsed")
apply_style()
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

if menu == "🎸 Rezervácia":
    st.session_state['page_id'] = 'rezaba'
    st.title("🎻 Rezervácia vystúpenia")
    st.markdown('<div class="info-box">🪗 Akordeón | 🎻 Husle | 🥁 Bubon | 🎷 Saxofón</div>', unsafe_allow_html=True)
    st.info("💡 Vypočítaná cena vám príde na e-mail na potvrdenie.")
    zobraz_footer_tlacidla()

elif menu == "💰 Cenník":
    st.session_state['page_id'] = 'cennik'
    st.title("💰 Cenník služieb")
    st.markdown(f"<div class='cennik-container'><h3>Rodinná oslava: {CENA_OSLAVA_HODINA}€/h</h3></div>", unsafe_allow_html=True)
    zobraz_footer_tlacidla()

elif menu == "ℹ️ O nás":
    st.session_state['page_id'] = 'onas'
    st.title("ℹ️ O nás")
    st.markdown("<div class='o-nas-box'><h3>🎻 Sme Ovčanske Parobci</h3></div>", unsafe_allow_html=True)
    zobraz_footer_tlacidla()

elif menu == "📸 Galéria":
    st.session_state['page_id'] = 'galeria'
    st.title("📸 Galéria a Videá")
    media = nacti_media()
    if media["fotky"]:
        for f in media["fotky"]:
            st.image(f, use_container_width=True)
    else:
        st.info("📸 Galéria je zatiaľ prázdna.")
    zobraz_footer_tlacidla()

elif menu == "⭐ Recenzie":
    st.session_state['page_id'] = 'recenzie'
    st.title("⭐ Ohlasy našich zákazníkov")
    recenzie = nacti_recenzie()
    if recenzie:
        for rec in recenzie:
            st.write(f"⭐ {rec.get('meno','Anonymný')}: {rec.get('text','')}")
    else:
        st.info("Zatiaľ nie sú recenzie.")
    zobraz_footer_tlacidla()

else:
    st.session_state['page_id'] = 'admin'
    st.title("🔐 Administrácia")
    if 'auth' not in st.session_state:
        st.session_state['auth'] = False
    if not st.session_state['auth']:
        with st.form("login"):
            u = st.text_input("Meno")
            h = st.text_input("Heslo", type="password")
            if st.form_submit_button("Vstúpiť"):
                if u == LOGIN_MENO and h == LOGIN_HESLO:
                    st.session_state['auth'] = True
                    st.rerun()
                else:
                    st.error("❌ Nesprávne prihlasovacie údaje!")
    else:
        st.success("Prihlásený admin.")

st.markdown('''
<div style="text-align:center; margin-top:50px; color:#ccc; line-height: 1.6;">
    <b>Podpora</b><br>
    <b>Tel. číslo:</b> 0944 757 122<br>
    <b>E-mail:</b> parobciovcanske@gmail.com
</div>
''', unsafe_allow_html=True)

# CHAT VPRAVO DOLE (vždy na konci renderu)
render_floating_chat()
