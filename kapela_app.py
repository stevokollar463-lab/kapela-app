import streamlit as st
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
from pushbullet import Pushbullet
from supabase import create_client
import calendar

# =========================
# BEZPEČNÁ KONFIGURÁCIA
# =========================
try:
    PB_API_KEY = st.secrets["PB_API_KEY"]
    LOGIN_MENO = st.secrets["ADMIN_USER"]
    LOGIN_HESLO = st.secrets["ADMIN_PASS"]
    SENDER_EMAIL = st.secrets["sender_email"]
    SENDER_PASSWORD = st.secrets["sender_password"]
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
except KeyError as e:
    st.error(f"❌ KRITICKÁ CHYBA: Chýba secret '{e.args[0]}' v Streamlit Secrets! Kontaktujte správcu.")
    st.stop()

# =========================
# KONŠTANTY
# =========================
KAPELA_FOTO_URL = "https://i.postimg.cc/T1Pkgjnw/1000027016.jpg"

CENA_OSLAVA_HODINA = 130
CENA_SPRIEVOD_ZAKLAD = 300
CENA_SPRIEVOD_POLHODINA = 50
CENA_STOLY_HODINA = 120
CENA_APARATURA = 100
CENA_ZA_KM = 0.50

# =========================
# SUPABASE
# =========================
@st.cache_resource
def get_supabase_client():
    try:
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        st.error(f"❌ Nepodarilo sa vytvoriť Supabase klienta: {e}")
        return None

supabase = get_supabase_client()

# =========================
# ŠTÝL
# =========================
def apply_style():
    st.markdown(f"""
        <style>
        .stApp {{
            background: linear-gradient(rgba(0, 0, 0, 0.74), rgba(0, 0, 0, 0.74)),
                        url("{KAPELA_FOTO_URL}");
            background-size: cover;
            background-position: center center;
            background-attachment: fixed;
            color: #ffffff;
        }}

        [data-testid="stToolbar"] {{
            display: none !important;
        }}

        .stDeployButton {{
            display: none !important;
        }}

        h1, h2, h3, h4 {{
            color: #d4af37 !important;
            font-family: 'Playfair Display', serif;
            text-shadow: 2px 2px 6px #000000;
        }}

        .subtle {{
            color: #cfcfcf;
            text-align: center;
            margin-top: -8px;
            margin-bottom: 20px;
        }}

        .card {{
            background: rgba(0, 0, 0, 0.78);
            border: 1px solid rgba(212,175,55,0.45);
            border-radius: 16px;
            padding: 18px;
            margin-bottom: 16px;
            transition: transform .18s ease, box-shadow .18s ease, border-color .18s ease;
        }}
        .card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 24px rgba(212,175,55,0.18);
            border-color: #d4af37;
        }}

        .kalkulacka-box {{
            background: rgba(212, 175, 55, 0.20);
            border: 1px dashed #d4af37;
            padding: 18px;
            border-radius: 12px;
            text-align: center;
            margin: 10px 0 18px 0;
        }}

        .section-title {{
            color: #d4af37;
            font-size: 1.1rem;
            font-weight: 700;
            margin-bottom: 10px;
        }}

        .stForm {{
            background-color: rgba(0, 0, 0, 0.72) !important;
            border: 1px solid rgba(212,175,55,0.45) !important;
            border-radius: 14px;
            padding: 20px;
        }}

        .stButton>button {{
            background-color: #d4af37 !important;
            color: black !important;
            border-radius: 10px !important;
            font-weight: 700 !important;
            border: none !important;
            transition: .18s ease;
        }}
        .stButton>button:hover {{
            transform: translateY(-1px);
            box-shadow: 0 6px 14px rgba(212,175,55,.28);
        }}

        .admin-detail-box {{
            background-color: rgba(0, 100, 255, 0.14);
            border-left: 4px solid #2e7bff;
            padding: 10px;
            margin: 10px 0;
            border-radius: 6px;
            font-size: 0.95rem;
        }}

        .small-muted {{
            color: #a7a7a7;
            font-size: .85rem;
        }}

        .footer-note {{
            text-align:center;
            margin-top:36px;
            color:#c9c9c9;
            line-height:1.5;
            font-size: .92rem;
        }}
        </style>
    """, unsafe_allow_html=True)

# =========================
# DATA FUNKCIE
# =========================
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

# =========================
# UI HELPERY
# =========================
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
    <div style="background: rgba(0,0,0,0.72); border: 1px solid rgba(212,175,55,0.45); border-radius: 12px; padding: 12px; margin-top: 6px;">
      <div style="text-align:center; color:#d4af37; margin-bottom:8px; font-weight:700;">📅 Obsadenosť (X = obsadené)</div>
      <table style="width:100%; border-collapse:collapse; text-align:center; color:white;">
        <tr>
    """
    for den in nazvy_dni:
        html += f'<th style="padding:6px; border-bottom:1px solid rgba(212,175,55,0.35); color:#d4af37;">{den}</th>'
    html += "</tr>"

    for tyzden in cal:
        html += "<tr>"
        for den in tyzden:
            if den == 0:
                html += '<td style="padding:8px; color:#555;">&nbsp;</td>'
            elif den in obsadene:
                html += '<td style="padding:8px; font-weight:700; color:#ff5f5f;">X</td>'
            else:
                html += f'<td style="padding:8px;">{den}</td>'
        html += "</tr>"

    html += "</table></div>"
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
E-mail: parobciovcanske@gmail.com
"""
        msg.attach(MIMEText(body, 'plain', 'utf-8'))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, to_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        st.warning(f"Nepodarilo sa odoslať potvrdzujúci e-mail zákazníkovi: {e}")
        return False

# =========================
# APP INIT
# =========================
st.set_page_config(page_title="Ovčanske Parobci", page_icon="🎻", layout="wide", initial_sidebar_state="expanded")
apply_style()

if 'auth' not in st.session_state:
    st.session_state['auth'] = False
if 'db_data' not in st.session_state:
    st.session_state['db_data'] = nacti_data()

# =========================
# SIDEBAR NAV
# =========================
with st.sidebar:
    st.markdown("## 🎻 Ovčanske Parobci")
    st.markdown("<div class='small-muted'>Ľudová hudba na svadby, oslavy a podujatia</div>", unsafe_allow_html=True)
    st.markdown("---")
    menu = st.radio(
        "Navigácia",
        ["🎸 Rezervácia", "💰 Cenník", "ℹ️ O nás", "📸 Galéria", "⭐ Recenzie", "🔐 Administrácia"]
    )
    st.markdown("---")
    st.caption("📞 0944 757 122")
    st.caption("📧 parobciovcanske@gmail.com")
    st.caption("📍 Obec Ovčie, Slovensko")

# =========================
# PAGES
# =========================
if menu == "🎸 Rezervácia":
    st.title("🎻 Rezervácia vystúpenia")
    st.markdown("<div class='subtle'>Vyplňte dopyt a orientačnú cenu vypočítame automaticky.</div>", unsafe_allow_html=True)

    col_left, col_right = st.columns([1.2, 1], gap="large")

    with col_left:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>⚙️ Výpočet ceny</div>", unsafe_allow_html=True)

        typ_akcie = st.selectbox(
            "Typ vystúpenia",
            ["🎂 Rodinná oslava / Jubileum", "👰 Svadobný sprievod a odobierka", "🍻 Hranie pomedzi stoly / Posedenie"]
        )

        c1, c2 = st.columns(2)
        cena_hudba = 0
        popis_hudby = ""

        with c1:
            if typ_akcie == "🎂 Rodinná oslava / Jubileum":
                hodiny = st.slider("Dĺžka hrania (hod.)", 1, 12, 5)
                cena_hudba = hodiny * CENA_OSLAVA_HODINA
                popis_hudby = f"Rodinná oslava ({hodiny} hod.)"
            elif typ_akcie == "👰 Svadobný sprievod a odobierka":
                st.info("Základná cena zahŕňa sprievod do 2 hodín (akusticky).")
                polhodiny_navyse = st.slider("Čas navyše (začaté polhodiny)", 0, 10, 0)
                cena_hudba = CENA_SPRIEVOD_ZAKLAD + (polhodiny_navyse * CENA_SPRIEVOD_POLHODINA)
                popis_hudby = f"Svadobný sprievod (2 hod. + {polhodiny_navyse}× polhodina)" if polhodiny_navyse > 0 else "Svadobný sprievod (základ do 2 hod.)"
            else:
                hodiny = st.slider("Dĺžka hrania (hod.)", 1, 12, 3)
                cena_hudba = hodiny * CENA_STOLY_HODINA
                popis_hudby = f"Hranie pomedzi stoly ({hodiny} hod.)"

        with c2:
            km = st.slider("Vzdialenosť z obce Ovčie (km, jednosmerne)", 0, 300, 0, 5)
            potrebuje_aparaturu = st.checkbox(f"Pridať aparatúru (+{CENA_APARATURA} €)", value=False)

        cena_doprava = km * 2 * CENA_ZA_KM
        prplatok_aparatura = CENA_APARATURA if potrebuje_aparaturu else 0
        celkova_cena = cena_hudba + cena_doprava + prplatok_aparatura

        detaily_vypoctu = f"{popis_hudby}: {cena_hudba:.2f} €"
        if potrebuje_aparaturu:
            detaily_vypoctu += f" | Ozvučenie: {CENA_APARATURA:.2f} €"
        detaily_vypoctu += f" | Doprava {km*2} km: {cena_doprava:.2f} €"

        st.markdown(f"""
            <div class="kalkulacka-box">
                <div style="font-size:1rem; color:#ddd;">Odhadovaná cena vystúpenia</div>
                <div style="font-size:2rem; font-weight:700; color:#d4af37;">{celkova_cena:.2f} €</div>
                <div class="small-muted">({detaily_vypoctu})</div>
            </div>
        """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='card'>", unsafe_allow_html=True)
        with st.expander("📅 Zobraziť kalendár obsadenosti", expanded=False):
            dnes = datetime.now().date()
            mc1, mc2 = st.columns(2)
            with mc1:
                vybrany_rok = st.number_input("Rok", min_value=dnes.year, max_value=dnes.year + 3, value=dnes.year, step=1)
            with mc2:
                vybrany_mesiac = st.selectbox("Mesiac", options=list(range(1, 13)), index=dnes.month - 1, format_func=lambda m: f"{m:02d}")
            st.markdown(zobraz_kalendar_obsadenosti(st.session_state['db_data'], int(vybrany_rok), int(vybrany_mesiac)), unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_right:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>📩 Rezervačný dopyt</div>", unsafe_allow_html=True)

        with st.form("main_booking"):
            f1, f2 = st.columns(2)
            with f1:
                datum = st.date_input("Dátum akcie", min_value=datetime.now())
            with f2:
                cas = st.time_input("Čas začiatku")

            meno = st.text_input("Meno a priezvisko")
            tel = st.text_input("Telefónne číslo")
            email = st.text_input("E-mail")
            mesto_detaily = st.text_area("Presná adresa a detaily", height=120)

            odoslat = st.form_submit_button("ODOSLAŤ REZERVÁCIU")

        if odoslat:
            db = nacti_data()
            if any(a['datum'] == str(datum) for a in db if a.get('stav') == 'schvalene'):
                st.error("❌ Tento termín je už obsadený. Prosím, vyberte si iný dátum.")
            elif not meno or not tel:
                st.warning("⚠️ Vyplňte, prosím, vaše meno a telefónne číslo.")
            else:
                txt_aparatury = "S APARATÚROU" if potrebuje_aparaturu else "BEZ aparatúry"
                vypocitana_cena_txt = f"{celkova_cena:.2f} € ({popis_hudby}, {txt_aparatury}, {km} km jednosmerne)"

                nova = {
                    "id": str(datetime.now().timestamp()),
                    "datum": str(datum),
                    "cas": cas.strftime('%H:%M'),
                    "meno": meno,
                    "tel": tel,
                    "email": email,
                    "detaily": f"[{typ_akcie}] [Ozvučenie: {txt_aparatury}] {mesto_detaily}",
                    "vypocitana_cena": vypocitana_cena_txt,
                    "stav": "cakajuce"
                }

                if supabase:
                    try:
                        res = supabase.table("kalendar").insert(nova).execute()
                        if res.data:
                            st.session_state['db_data'] = nacti_data()
                            posli_upozornenie(f"Nový dopyt: {datum}\n{meno} ({tel})\nTyp: {typ_akcie}\nMiesto: {mesto_detaily}\nCena: {vypocitana_cena_txt}")
                            if email:
                                posli_email_zakaznikovi(email, meno, str(datum), cas.strftime('%H:%M'), typ_akcie, vypocitana_cena_txt, mesto_detaily)
                            st.success("✅ Odoslané! Ozveme sa vám.")
                            st.balloons()
                        else:
                            st.error("Chyba: Dáta sa nepodarilo zapísať do databázy.")
                    except Exception as e:
                        st.error(f"Chyba zápisu do Supabase: {e}")
                else:
                    st.error("Chyba: Databáza Supabase nie je pripojená!")

        st.markdown("</div>", unsafe_allow_html=True)

elif menu == "💰 Cenník":
    st.title("💰 Cenník služieb")
    st.markdown("<div class='subtle'>Jednoduché a transparentné ceny.</div>", unsafe_allow_html=True)

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown(f"""
        <table style="width:100%; border-collapse:collapse; color:#fff;">
            <tr style="border-bottom:1px solid rgba(212,175,55,.4); text-align:left;">
                <th style="padding:10px; color:#d4af37;">Služba</th>
                <th style="padding:10px; color:#d4af37;">Cena</th>
                <th style="padding:10px; color:#d4af37;">Poznámka</th>
            </tr>
            <tr style="border-bottom:1px solid rgba(212,175,55,.2);">
                <td style="padding:10px;">🎂 Rodinná oslava / Jubileum</td>
                <td style="padding:10px; color:#d4af37; font-weight:700;">{CENA_OSLAVA_HODINA} € / hodina</td>
                <td style="padding:10px; color:#ccc;">Živé hranie na oslavách</td>
            </tr>
            <tr style="border-bottom:1px solid rgba(212,175,55,.2);">
                <td style="padding:10px;">👰 Svadobný sprievod a odobierka</td>
                <td style="padding:10px; color:#d4af37; font-weight:700;">{CENA_SPRIEVOD_ZAKLAD} € základ</td>
                <td style="padding:10px; color:#ccc;">Do 2 hodín, ďalšia polhodina +{CENA_SPRIEVOD_POLHODINA} €</td>
            </tr>
            <tr style="border-bottom:1px solid rgba(212,175,55,.2);">
                <td style="padding:10px;">🍻 Hranie pomedzi stoly / Posedenie</td>
                <td style="padding:10px; color:#d4af37; font-weight:700;">{CENA_STOLY_HODINA} € / hodina</td>
                <td style="padding:10px; color:#ccc;">Komorné akustické hranie</td>
            </tr>
            <tr style="border-bottom:1px solid rgba(212,175,55,.2);">
                <td style="padding:10px;">🎤 Profesionálna aparatúra</td>
                <td style="padding:10px; color:#d4af37; font-weight:700;">+{CENA_APARATURA} €</td>
                <td style="padding:10px; color:#ccc;">Jednorazový príplatok</td>
            </tr>
            <tr>
                <td style="padding:10px;">🚗 Doprava (z obce Ovčie)</td>
                <td style="padding:10px; color:#d4af37; font-weight:700;">{CENA_ZA_KM:.2f} € / km</td>
                <td style="padding:10px; color:#ccc;">Počíta sa cesta tam aj späť</td>
            </tr>
        </table>
    """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

elif menu == "ℹ️ O nás":
    st.title("ℹ️ O nás")
    st.markdown("<div class='subtle'>Tradičná hudba s energiou a srdcom.</div>", unsafe_allow_html=True)

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("""
        <p>
            Sme ľudová kapela založená v roku <b>2020</b>. Naša 5-členná zostava hrá na svadbách, oslavách,
            rodinných aj firemných podujatiach.
        </p>
        <ul>
            <li>🎂 Jubileá a oslavy</li>
            <li>👰 Svadobné sprievody</li>
            <li>🎉 Rodinné a firemné akcie</li>
            <li>🎵 Živá hudba na posedeniach</li>
        </ul>
    """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("### 🎼 Naši členovia")
    clenovia = [
        {"meno": "Akordeón", "pocet": 2},
        {"meno": "Husle", "pocet": 1},
        {"meno": "Bubon", "pocet": 1},
        {"meno": "Saxofón", "pocet": 1},
    ]
    for clen in clenovia:
        st.markdown(f"- **{clen['meno']}**: {clen['pocet']} {'člen' if clen['pocet']==1 else 'členovia'}")
    st.markdown("</div>", unsafe_allow_html=True)

elif menu == "📸 Galéria":
    st.title("📸 Galéria")
    st.markdown("<div class='subtle'>Momenty z vystúpení.</div>", unsafe_allow_html=True)

    media = nacti_media()

    if media["videa"]:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("🎥 Videá")
        v1, v2 = st.columns(2)
        for idx, video_url in enumerate(media["videa"]):
            with (v1 if idx % 2 == 0 else v2):
                st.video(video_url)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("🖼️ Fotogaléria")
    if media["fotky"]:
        c1, c2 = st.columns(2)
        for idx, f in enumerate(media["fotky"]):
            with (c1 if idx % 2 == 0 else c2):
                st.image(f, use_container_width=True)
    else:
        st.info("📸 Galéria je zatiaľ prázdna.")
    st.markdown("</div>", unsafe_allow_html=True)

elif menu == "⭐ Recenzie":
    st.title("⭐ Recenzie")
    st.markdown("<div class='subtle'>Ohlasy od zákazníkov.</div>", unsafe_allow_html=True)

    recenzie = nacti_recenzie()
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    if recenzie:
        st.write(f"**Celkovo recenzií:** {len(recenzie)}")
        for rec in recenzie:
            st.markdown(f"""
                <div style="background:rgba(0,0,0,.55); border:1px solid rgba(212,175,55,.35); border-radius:10px; padding:12px; margin:10px 0;">
                    <div style="display:flex; justify-content:space-between; color:#d4af37;">
                        <b>{rec.get('meno', 'Anonymný')}</b>
                        <span>{hvezdicky_html(rec.get('hvezdicky', 5))}</span>
                    </div>
                    <div style="color:#d6d6d6; margin-top:8px;">„{rec.get('text', '')}“</div>
                    <div class="small-muted">📅 {rec.get('created_at', '')[:10]}</div>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Zatiaľ tu nie sú žiadne recenzie.")
    st.markdown("</div>", unsafe_allow_html=True)

else:
    st.title("🔐 Administrácia")

    if not st.session_state['auth']:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        with st.form("login"):
            u = st.text_input("Meno")
            h = st.text_input("Heslo", type="password")
            if st.form_submit_button("Vstúpiť"):
                if u == LOGIN_MENO and h == LOGIN_HESLO:
                    st.session_state['auth'] = True
                    st.rerun()
                else:
                    st.error("❌ Nesprávne prihlasovacie údaje!")
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        if st.button("Odhlásiť sa"):
            st.session_state['auth'] = False
            st.rerun()

        t1, t2, t3, t4, t5 = st.tabs(["📩 Nové dopyty", "📅 Kalendár", "📁 Správa médií", "➕ Pridať udalosť", "⭐ Recenzie"])
        db = nacti_data()

        with t1:
            cakajuce = [a for a in db if a.get("stav") == "cakajuce"]
            if not cakajuce:
                st.info("Žiadne nové dopyty.")
            for i, a in enumerate(cakajuce):
                with st.expander(f"DOPYT: {a['datum']} - {a.get('meno', 'Neznámy')}"):
                    st.write(f"📞 {a.get('tel', '---')} | 📧 {a.get('email', '---')}")
                    st.write(f"🕒 {a.get('cas', '---')}")
                    st.write(f"💰 {a.get('vypocitana_cena', 'Nenapočítaná')}")
                    st.markdown(f"<div class='admin-detail-box'><b>Detaily:</b><br>{a.get('detaily', 'Neuvedené')}</div>", unsafe_allow_html=True)
                    c1, c2 = st.columns(2)
                    if c1.button("✅ Schváliť", key=f"ok{i}"):
                        try:
                            supabase.table("kalendar").update({"stav": "schvalene"}).eq("id", a['id']).execute()
                            st.session_state['db_data'] = nacti_data()
                            st.success("Dopyt schválený!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Chyba: {e}")
                    if c2.button("🗑️ Vymazať", key=f"no{i}"):
                        try:
                            supabase.table("kalendar").delete().eq("id", a['id']).execute()
                            st.session_state['db_data'] = nacti_data()
                            st.success("Dopyt vymazaný!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Chyba: {e}")

        with t2:
            schvalene = [a for a in db if a.get("stav") == "schvalene"]
            schvalene.sort(key=lambda x: x['datum'])
            if not schvalene:
                st.info("Kalendár je prázdny.")
            for i, a in enumerate(schvalene):
                with st.expander(f"📅 {a['datum']} - {a.get('meno', 'Akcia')}"):
                    st.write(f"📞 {a.get('tel', '')} | 🕒 {a.get('cas', '')}")
                    st.write(f"💰 {a.get('vypocitana_cena', 'Nenapočítaná')}")
                    st.markdown(f"<div class='admin-detail-box'><b>Miesto/Poznámka:</b><br>{a.get('detaily', 'Neuvedené')}</div>", unsafe_allow_html=True)
                    if st.button("🗑️ Odstrániť", key=f"del{i}"):
                        try:
                            supabase.table("kalendar").delete().eq("id", a['id']).execute()
                            st.session_state['db_data'] = nacti_data()
                            st.success("Akcia odstránená!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Chyba: {e}")

        with t3:
            st.subheader("📁 Nahrať fotky a videá")
            subor_na_nahratie = st.file_uploader(
                "Pretiahni alebo vyber súbor",
                type=["jpg", "jpeg", "png", "gif", "webp", "mp4", "mov", "avi", "webm"]
            )

            if subor_na_nahratie is not None and st.button("🚀 Nahrať súbor"):
                try:
                    subor_bytes = subor_na_nahratie.read()
                    cisty_nazov = f"{int(datetime.now().timestamp())}_{subor_na_nahratie.name.replace(' ', '_')}"
                    res = supabase.storage.from_("parobci-media").upload(
                        path=cisty_nazov,
                        file=subor_bytes,
                        file_options={"content-type": subor_na_nahratie.type}
                    )
                    if res:
                        st.success("Súbor nahraný.")
                        st.rerun()
                except Exception as e:
                    st.error(f"Chyba pri nahrávaní: {e}")

            st.markdown("---")
            st.subheader("📦 Všetky médiá")
            vsetky_media = nacti_vsetky_media()
            if vsetky_media:
                for idx, m in enumerate(vsetky_media):
                    c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
                    c1.write(f"📄 {m['nazov']}")
                    c2.write(m['typ'])
                    c3.write(f"{m['velkost']/1024:.1f} KB")
                    if c4.button("🗑️", key=f"delm{idx}"):
                        try:
                            supabase.storage.from_("parobci-media").remove([m['nazov']])
                            st.success("Vymazané.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Chyba: {e}")
            else:
                st.info("Galéria je prázdna.")

        with t4:
            with st.form("add_manual"):
                st.subheader("➕ Manuálne pridať akciu")
                d = st.date_input("Dátum akcie", value=datetime.today())
                t_time = st.time_input("Čas začiatku", value=datetime.now().time())
                m = st.text_input("Meno / Názov akcie")
                tel_cislo = st.text_input("Telefón")
                em_adresa = st.text_input("E-mail")
                dohodnuta_cena = st.text_input("Dohodnutá cena", value="0.00 €")
                det = st.text_area("Detaily")

                if st.form_submit_button("Uložiť do kalendára"):
                    if not m:
                        st.warning("Zadajte aspoň názov alebo meno akcie.")
                    else:
                        nova_akcia = {
                            "id": str(datetime.now().timestamp()),
                            "datum": str(d),
                            "cas": t_time.strftime('%H:%M'),
                            "meno": m,
                            "tel": tel_cislo,
                            "email": em_adresa,
                            "vypocitana_cena": dohodnuta_cena,
                            "detaily": det,
                            "stav": "schvalene"
                        }
                        try:
                            supabase.table("kalendar").insert(nova_akcia).execute()
                            st.session_state['db_data'] = nacti_data()
                            st.success("Akcia pridaná.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Chyba: {e}")

        with t5:
            st.subheader("⭐ Správa recenzií")
            recenzie = nacti_recenzie()
            if not recenzie:
                st.info("Zatiaľ nie sú žiadne recenzie.")
            else:
                for idx, rec in enumerate(recenzie):
                    with st.expander(f"⭐ {rec.get('meno', 'Anonymný')} - {hvezdicky_html(rec.get('hvezdicky', 5))}"):
                        st.write(f"**Komentár:** {rec.get('text', '')}")
                        st.write(f"**Dátum:** {rec.get('created_at', '')[:10]}")
                        if st.button("🗑️ Vymazať", key=f"del_rec_{idx}"):
                            try:
                                supabase.table("recenzie").delete().eq("id", rec['id']).execute()
                                st.success("Recenzia vymazaná.")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Chyba: {e}")

st.markdown("""
<div class="footer-note">
    <b>Podpora</b><br>
    Tel.: 0944 757 122 · Email: parobciovcanske@gmail.com
</div>
""", unsafe_allow_html=True)
    
