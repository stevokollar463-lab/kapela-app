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

        /* FOOTER S TLAČIDLAMI */
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

        /* EXPANDOVACIA SEKCIA */
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
    """Vykreslí mesiac, kde obsadené (schválené) dni sú označené X."""
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


def zobraz_footer_tlacidla(is_recenzie_page=False):
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("❓ FAQ", key=f"btn_faq_{st.session_state.get('page_id', 'main')}", use_container_width=True):
            st.session_state[f"expand_faq_{st.session_state.get('page_id', 'main')}"] = not st.session_state.get(f"expand_faq_{st.session_state.get('page_id', 'main')}", False)
            st.rerun()

    with col2:
        if st.button("⭐ RECENZIE", key=f"btn_rec_{st.session_state.get('page_id', 'main')}", use_container_width=True):
            st.session_state[f"expand_rec_{st.session_state.get('page_id', 'main')}"] = not st.session_state.get(f"expand_rec_{st.session_state.get('page_id', 'main')}", False)
            st.rerun()

    with col3:
        if st.button("📞 KONTAKT", key=f"btn_kon_{st.session_state.get('page_id', 'main')}", use_container_width=True):
            st.session_state[f"expand_kon_{st.session_state.get('page_id', 'main')}"] = not st.session_state.get(f"expand_kon_{st.session_state.get('page_id', 'main')}", False)
            st.rerun()

    if st.session_state.get(f"expand_faq_{st.session_state.get('page_id', 'main')}", False):
        st.markdown('<div class="expandable-section">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">❓ Často kladené otázky</div>', unsafe_allow_html=True)

        faq_otazky = [
            {"otazka": "Ako dlho hráte minimálne?", "odpoved": "Minimálna doba hrania je 1 hodina. Nižšie doby sa neposkytujú."},
            {"otazka": "Aká je minimálna doba rezervácie?", "odpoved": "Rezervácia musí byť uskutočnená minimálne 1 mesiac vopred. To nám umožňuje správne si naplánovať našu kapelu."},
            {"otazka": "Ako sa počíta cena?", "odpoved": f"Rodinná oslava: {CENA_OSLAVA_HODINA} € za hodinu | Svadobný sprievod: {CENA_SPRIEVOD_ZAKLAD} € za 2 hodiny | Hranie pomedzi stoly: {CENA_STOLY_HODINA} € za hodinu + doprava {CENA_ZA_KM} € za km"}
        ]

        for faq in faq_otazky:
            st.markdown(f"""
            <div class="faq-item">
                <div class="faq-otazka">❓ {faq['otazka']}</div>
                <div class="faq-odpoved">{faq['odpoved']}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    if st.session_state.get(f"expand_rec_{st.session_state.get('page_id', 'main')}", False):
        st.markdown('<div class="expandable-section">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">⭐ Zanechaj svoj ohlas</div>', unsafe_allow_html=True)

        with st.form(f"nova_recenzia_{st.session_state.get('page_id', 'main')}"):
            typ_mena = st.radio("Ako sa chceš reprezentovať?", ["❌ Anonymne", "✅ Pod mojim menom"], horizontal=True, key=f"radio_rec_{st.session_state.get('page_id', 'main')}")

            meno = ""
            if typ_mena == "✅ Pod mojim menom":
                meno = st.text_input("Tvoje meno", placeholder="Napíš svoje meno...", key=f"input_meno_{st.session_state.get('page_id', 'main')}")
                if not meno:
                    meno = "Anonymný"
            else:
                meno = "Anonymný"

            hvezdicky = st.slider("Ako hodnotíš našu kapelu? (1-5 hviezd)", min_value=1, max_value=5, value=5, key=f"slider_rec_{st.session_state.get('page_id', 'main')}")
            text = st.text_area("Tvoj komentár", placeholder="Napíš nám tvoj názor na naše vystúpenie...", height=120, key=f"textarea_rec_{st.session_state.get('page_id', 'main')}")

            if st.form_submit_button("🚀 ODOSLAŤ RECENZIU", key=f"submit_rec_{st.session_state.get('page_id', 'main')}"):
                if not text or len(text) < 5:
                    st.warning("⚠️ Napíš prosím aspoň pár slov do komentára!")
                else:
                    nova_recenzia = {
                        "id": str(datetime.now().timestamp()),
                        "meno": meno,
                        "hvezdicky": hvezdicky,
                        "text": text,
                        "created_at": datetime.now().isoformat()
                    }

                    if supabase:
                        try:
                            res = supabase.table("recenzie").insert(nova_recenzia).execute()
                            if res.data:
                                st.success("✅ Ďakujeme za tvoj ohlas! 🎉")
                                st.balloons()
                                st.rerun()
                            else:
                                st.error("Chyba: Recenzija sa nepodarila uložiť.")
                        except Exception as e:
                            st.error(f"Chyba: {e}")
                    else:
                        st.error("Chyba: Databáza Supabase nie je pripojená!")

        st.markdown('</div>', unsafe_allow_html=True)

    if st.session_state.get(f"expand_kon_{st.session_state.get('page_id', 'main')}", False):
        st.markdown('<div class="expandable-section">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">📞 Kontaktujte nás</div>', unsafe_allow_html=True)

        st.markdown("""
            <div class="kontakt-info">
                <div class="kontakt-label">☎️ Telefón</div>
                <div class="kontakt-value">0944 757 122</div>
            </div>
            <div class="kontakt-info">
                <div class="kontakt-label">📧 Email</div>
                <div class="kontakt-value">parobciovcanske@gmail.com</div>
            </div>
            <div class="kontakt-info">
                <div class="kontakt-label">📍 Mesto</div>
                <div class="kontakt-value">Obec Ovčie, Slovensko</div>
            </div>
            <div style="text-align: center; margin-top: 15px;">
                <a href="https://www.instagram*

