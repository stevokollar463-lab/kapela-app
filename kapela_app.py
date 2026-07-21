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


def inject_live_chat():
    st.markdown("""
    <!--Start of Tawk.to Script-->
    <script type="text/javascript">
    var Tawk_API=Tawk_API||{}, Tawk_LoadStart=new Date();
    (function(){
      var s1=document.createElement("script"),s0=document.getElementsByTagName("script")[0];
      s1.async=true;
      s1.src='https://embed.tawk.to/6a5f209b4693711d483c3318/1ju1peoj1';
      s1.charset='UTF-8';
      s1.setAttribute('crossorigin','*');
      s0.parentNode.insertBefore(s1,s0);
    })();
    </script>
    <!--End of Tawk.to Script-->
    """, unsafe_allow_html=True)


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
                <a href="https://www.instagram.com/ovcanske_parobci/" target="_blank" style="display: inline-block; padding: 10px 20px; background-color: #d4af37; color: black; text-decoration: none; border-radius: 8px; font-weight: bold;">
                    📸 Sleduj nás na Instagrame
                </a>
            </div>
        """, unsafe_allow_html=True)

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


def posli_email_zakaznikovi_s_potvrdenim(to_email, meno_klienta, datum_akcie, cas_akcie, typ_vystupenia, celkova_cena, detaily_miesta, confirm_url):
    subject = f"Status: Prijatie dopytu - Ovčanske Parobci ({datum_akcie})"

    body_plain = f"""Dobrý deň, {meno_klienta},

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

Ak súhlasíte s cenou, potvrďte ju kliknutím na tento odkaz:
{confirm_url}

Čoskoro Vás budeme kontaktovať pre telefonické potvrdenie termínu a doladenie detailov.

S pozdravom,
Ľudová hudba Ovčanske Parobci
Tel. číslo: 0944 757 122
E-mail: parobciovcanske@gmail.com
"""

    body_html = f"""
    <html><body style="font-family:Arial,sans-serif;line-height:1.6;">
      <p>Dobrý deň, {meno_klienta},</p>
      <p>ďakujeme za Váš záujem o vystúpenie našej hudobnej skupiny Ovčanske Parobci.<br>
      Vašu požiadavku sme úspešne prijali a momentálne ju spracovávame.</p>

      <p><b>Rekapitulácia Vášho dopytu:</b><br>
      ------------------------------------------<br>
      Dátum akcie: {datum_akcie}<br>
      Čas začiatku: {cas_akcie}<br>
      Typ vystúpenia: {typ_vystupenia}<br>
      Orientačná cena: {celkova_cena}<br>
      Miesto konania a detaily: {detaily_miesta}<br>
      ------------------------------------------</p>

      <p>
        <a href="{confirm_url}" style="display:inline-block;padding:12px 20px;background:#d4af37;color:#000;text-decoration:none;border-radius:8px;font-weight:bold;">
          ✅ Potvrdiť cenu
        </a>
      </p>

      <p>Čoskoro Vás budeme kontaktovať pre telefonické potvrdenie termínu a doladenie detailov.</p>

      <p>S pozdravom,<br>
      Ľudová hudba Ovčanske Parobci<br>
      Tel. číslo: 0944 757 122<br>
      E-mail: parobciovcanske@gmail.com</p>
    </body></html>
    """
    return send_email(to_email, subject, body_plain, body_html)


def posli_email_o_potvrdeni_zakaznikovi(to_email, meno, datum_akcie, cena):
    subject = f"Potvrdenie prijaté - Ovčanske Parobci ({datum_akcie})"
    body = f"""Dobrý deň, {meno},

ďakujeme, Vaše potvrdenie ceny sme úspešne prijali.

Dátum akcie: {datum_akcie}
Potvrdená cena: {cena}

S pozdravom,
Ovčanske Parobci
"""
    return send_email(to_email, subject, body)


def posli_email_adminovi_o_potvrdeni(meno, tel, email, datum_akcie, cas_akcie, cena, detaily):
    subject = f"✅ Klient potvrdil cenu - {datum_akcie}"
    body = f"""Klient potvrdil cenu dopytu.

Meno: {meno}
Tel: {tel}
Email: {email}
Dátum: {datum_akcie}
Čas: {cas_akcie}
Cena: {cena}
Detaily: {detaily}
"""
    return send_email(ADMIN_NOTIFY_EMAIL, subject, body)


def posli_email_o_zamietnuti(to_email, meno, datum_akcie):
    subject = f"Oznam o dopyte - Ovčanske Parobci ({datum_akcie})"
    body = f"""Dobrý deň, {meno},

ďakujeme za Váš záujem o vystúpenie našej hudobnej skupiny Ovčanske Parobci.

Veľmi nás to mrzí, ale Váš dopyt na termín {datum_akcie} musíme z organizačných dôvodov zamietnuť.

Ospravedlňujeme sa za komplikácie a ďakujeme za pochopenie.
V prípade záujmu nás môžete kontaktovať pre iný termín.

S pozdravom,
Ľudová hudba Ovčanske Parobci
Tel. číslo: 0944 757 122
E-mail: parobciovcanske@gmail.com
"""
    return send_email(to_email, subject, body)


def posli_email_o_zruseni_akcie(to_email, meno, datum_akcie):
    subject = f"Zrušenie akcie - Ovčanske Parobci ({datum_akcie})"
    body = f"""Dobrý deň, {meno},

ospravedlňujeme sa, ale dohodnutú akciu na dátum {datum_akcie} musíme z organizačných dôvodov zrušiť.

Mrzí nás to a ďakujeme za pochopenie.
V prípade záujmu nás kontaktujte a dohodneme náhradný termín.

S pozdravom,
Ľudová hudba Ovčanske Parobci
Tel. číslo: 0944 757 122
E-mail: parobciovcanske@gmail.com
"""
    return send_email(to_email, subject, body)


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

        meno = zaznam.get("meno", "Klient")
        tel = zaznam.get("tel", "")
        email = zaznam.get("email", "")
        datum_akcie = zaznam.get("datum", "")
        cas_akcie = zaznam.get("cas", "")
        cena = zaznam.get("vypocitana_cena", "")
        detaily = zaznam.get("detaily", "")

        posli_upozornenie(
            f"✅ KLIENT POTVRDIL CENU\nDátum: {datum_akcie} {cas_akcie}\nMeno: {meno}\nTel: {tel}\nEmail: {email}\nCena: {cena}\nDetaily: {detaily}"
        )
        posli_email_adminovi_o_potvrdeni(meno, tel, email, datum_akcie, cas_akcie, cena, detaily)
        if email:
            posli_email_o_potvrdeni_zakaznikovi(email, meno, datum_akcie, cena)

        st.success("✅ Ďakujeme, cenu ste úspešne potvrdili.")
        st.query_params.clear()

    except Exception as e:
        st.error(f"Chyba pri potvrdzovaní: {e}")


st.set_page_config(page_title="Ovčanske Parobci", page_icon="🎻", layout="centered", initial_sidebar_state="collapsed")
inject_live_chat()
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

# --- 1. REZERVÁCIA ---
if menu == "🎸 Rezervácia":
    st.session_state['page_id'] = 'rezaba'
    st.title("🎻 Rezervácia vystúpenia")
    st.markdown('<div class="info-box">🪗 Akordeón | 🎻 Husle | 🥁 Bubon | 🎷 Saxofón</div>', unsafe_allow_html=True)

    st.markdown("<h4 style='text-align: center; margin-bottom: 5px; margin-top: 20px;'>Výpočet ceny vystúpenia</h4>", unsafe_allow_html=True)

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

    # SKRYTÁ kalkulácia
    st.info("💡 Vypočítaná cena vám príde na e-mail na potvrdenie.")

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

        if st.form_submit_button("ODOSLAŤ REZERVÁCIU S TOUTO CENOU"):
            db = nacti_data()

            if any(a['datum'] == str(datum) for a in db if a.get('stav') == 'schvalene'):
                st.error("❌ Tento termín je už obsadený. Prosím, vyberte si iný dátum.")
            elif not meno or not tel or not email:
                st.warning("⚠️ Vyplňte, prosím, vaše meno, telefónne číslo a e-mail.")
            else:
                txt_aparatury = "S APARATÚROU" if potrebuje_aparaturu else "BEZ aparatúry"
                vypocitana_cena_txt = f"{celkova_cena:.2f} € ({popis_hudby}, {txt_aparatury}, {km} km jednosmerne)"

                token = secrets.token_urlsafe(32)
                token_exp = (datetime.now() + timedelta(days=3)).isoformat()
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
                    "token_expires_at": token_exp,
                    "confirmed_at": None,
                    "klient_potvrdil_cenu": False
                }

                if supabase:
                    try:
                        res = supabase.table("kalendar").insert(nova).execute()
                        if res.data:
                            st.session_state['db_data'] = nacti_data()
                            posli_upozornenie(f"Nový dopyt: {datum}\n{meno} ({tel})\nTyp: {typ_akcie}\nMiesto: {mesto_detaily}\nCena: {vypocitana_cena_txt}")
                            posli_email_zakaznikovi_s_potvrdenim(
                                email, meno, str(datum), cas.strftime('%H:%M'),
                                typ_akcie, vypocitana_cena_txt, mesto_detaily, confirm_url
                            )
                            st.balloons()
                            st.success("✅ Odoslané! Cena bola zaslaná na e-mail na potvrdenie.")
                        else:
                            st.error("Chyba: Dáta sa nepodarilo zapísať do databázy.")
                    except Exception as e:
                        st.error(f"Chyba zápisu do Supabase: {e}")
                else:
                    st.error("Chyba: Databáza Supabase nie je pripojená!")

    zobraz_footer_tlacidla()

# --- 2. PODROBNÝ CENNÍK ---
elif menu == "💰 Cenník":
    st.session_state['page_id'] = 'cennik'
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
                    <td style="padding: 12px; font-weight: bold;">👰 Svadobný sprievod a odobierka</td>
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
    zobraz_footer_tlacidla()

elif menu == "ℹ️ O nás":
    st.session_state['page_id'] = 'onas'
    st.title("ℹ️ O nás")
    st.markdown("""
        <div class="o-nas-box">
            <h3 style="color: #d4af37; text-align: center;">🎻 Sme Ovčanske Parobci</h3>
            <div class="o-nas-text">
                <p>
                    Sme ľudová kapela založená v roku <strong>2020</strong>, ktorá sa špecializuje na vytváranie nezabudnuteľných zážitkov
                    na najrôznejších podujatiach. Naša päťčlenná kapela hrá s vášňou a energiou tradičnú ľudovú hudbu.
                </p>
                <p><strong>Čo nám robíme:</strong></p>
                <ul style="color: #ccc;">
                    <li>🎂 Jubileá a oslavy narodenín</li>
                    <li>👰 Svadobné sprievody a sprevody novomanželov</li>
                    <li>🎉 Výstupy na rodinných a firemných akciách</li>
                    <li>🎵 Živá hudba na posedeniach a stretnutiach</li>
                </ul>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.subheader("🎼 Naši členovia")
    clenovia = [
        {"meno": "Akordeón", "pocet": 2},
        {"meno": "Husle", "pocet": 1},
        {"meno": "Bubon", "pocet": 1},
        {"meno": "Saxofón", "pocet": 1}
    ]
    for clen in clenovia:
        st.markdown(f"""
            <div class="clenovia-box">
                <strong style="color: #d4af37;">🎵 {clen['meno']}</strong>
                <p style="margin: 5px 0; color: #ccc;">{clen['pocet']} {'člen' if clen['pocet'] == 1 else 'členovia'}</p>
            </div>
        """, unsafe_allow_html=True)

    st.subheader("📍 Kde nás nájdete")
    st.markdown(
        """
        <div style="text-align:center; margin-bottom:10px; color:#ccc;">
            Obec Ovčie, Slovensko
        </div>
        """,
        unsafe_allow_html=True
    )

    # Mapa
    st.components.v1.iframe(
        "https://www.google.com/maps?q=Ov%C4%8Die,+Slovensko&output=embed",
        height=400,
        scrolling=False
    )

    # Medzera pod mapou
    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)

    # Tlačidlo s väčším spodným odsadením, aby sa neprekrývalo s ďalšou sekciou
    st.markdown(
        """
        <div style="text-align:center; margin-top:10px; margin-bottom:40px;">
            <a href="https://www.google.com/maps/search/?api=1&query=Ov%C4%8Die%2C+Slovensko" target="_blank"
               style="display:inline-block;padding:10px 18px;background:#d4af37;color:#000;text-decoration:none;border-radius:8px;font-weight:bold;">
               🗺️ Otvoriť mapu v Google Maps
            </a>
        </div>
        """,
        unsafe_allow_html=True
    )

    zobraz_footer_tlacidla()
    

elif menu == "📸 Galéria":
    st.session_state['page_id'] = 'galeria'
    st.title("📸 Galéria a Videá")
    media = nacti_media()

    if media["videa"]:
        st.subheader("🎥 Videá z našich akcií")
        col_v1, col_v2 = st.columns(2)
        for idx, video_url in enumerate(media["videa"]):
            with (col_v1 if idx % 2 == 0 else col_v2):
                st.video(video_url)
        st.markdown("<hr style='border-color: rgba(212,175,55,0.3);'>", unsafe_allow_html=True)

    st.subheader("🖼️ Fotogaléria")
    if media["fotky"]:
        col_img1, col_img2 = st.columns(2)
        for idx, f in enumerate(media["fotky"]):
            with (col_img1 if idx % 2 == 0 else col_img2):
                st.image(f, use_container_width=True)
    else:
        st.info("📸 Galéria je zatiaľ prázdna. Fotky budú pridané čoskoro.")

    zobraz_footer_tlacidla()

elif menu == "⭐ Recenzie":
    st.session_state['page_id'] = 'recenzie'
    st.title("⭐ Ohlasy našich zákazníkov")
    recenzie = nacti_recenzie()

    if recenzie:
        st.subheader(f"💬 {len(recenzie)} ohlasov od našich zákazníkov")
        for rec in recenzie:
            st.markdown(f"""
            <div style="background: rgba(0, 0, 0, 0.8); border: 2px solid #d4af37; padding: 15px; border-radius: 12px; margin: 12px 0;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; color: #d4af37;">
                    <span style="font-weight: bold;">{rec.get('meno', 'Anonymný')}</span>
                    <span style="font-size: 1.3rem; color: #FFD700;">{hvezdicky_html(rec.get('hvezdicky', 5))}</span>
                </div>
                <div style="color: #ccc; font-style: italic; margin-top: 10px; line-height: 1.5;">"{rec.get('text', '')}"</div>
                <div style="font-size: 0.85rem; color: #999; margin-top: 8px;">📅 {rec.get('created_at', '')[:10]}</div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("<hr style='border-color: rgba(212,175,55,0.3); margin: 30px 0;'>", unsafe_allow_html=True)
    else:
        st.info("Zatiaľ tu nie sú žiadne recenzie. Buď prvý a nechaj svoj ohlas! 😊")

    zobraz_footer_tlacidla(is_recenzie_page=True)

else:
    st.session_state['page_id'] = 'admin'
    col_title, col_logout = st.columns([3, 1])
    with col_title:
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
        with col_logout:
            st.write("")
            if st.button("Odhlásiť sa", key="logout_btn"):
                st.session_state['auth'] = False
                st.rerun()

        t1, t2, t3, t4, t5 = st.tabs(["📩 Nové dopyty", "📅 Kalendár", "📁 Sprava medii", "➕ Pridat udalost", "⭐ Recenzie"])
        db = nacti_data()

        with t1:
            cakajuce = [a for a in db if a.get("stav") == "cakajuce"]
            if not cakajuce:
                st.info("Žiadne nové dopyty.")
            for i, a in enumerate(cakajuce):
                info_mesto = a.get('detaily', 'Neuvedené')
                kalkulacia = a.get('vypocitana_cena', 'Nenapočítaná')
                with st.expander(f"DOPYT: {a['datum']} - {a.get('meno', 'Neznámy')}"):
                    st.write(f"📞 **Kontakt:** {a.get('tel', '---')} | 📧 {a.get('email', '---')}")
                    st.write(f"🕒 **Čas:** {a.get('cas', '---')}")
                    st.write(f"💰 **Cena:** {kalkulacia}")

                    if a.get("klient_potvrdil_cenu", False):
                        st.success("✅ Klient POTVRDIL cenu")
                    else:
                        st.warning("⌛ Klient ešte NEPOTVRDIL cenu")

                    st.markdown(f"""<div class="admin-detail-box"><b>Miesto a detaily:</b><br>{info_mesto}</div>""", unsafe_allow_html=True)

                    c1, c2, c3 = st.columns(3)
                    if c1.button("✅ Schváliť", key=f"ok{i}"):
                        if not a.get("klient_potvrdil_cenu", False):
                            st.error("Klient ešte nepotvrdil cenu. Najprv musí potvrdiť cez e-mail.")
                        else:
                            if supabase:
                                try:
                                    supabase.table("kalendar").update({"stav": "schvalene"}).eq("id", a['id']).execute()
                                    st.session_state['db_data'] = nacti_data()
                                    st.success("Dopyt schválený!")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Nepodarilo sa schváliť v Supabase: {e}")

                    if c2.button("❌ Zamietnuť", key=f"no{i}"):
                        if supabase:
                            try:
                                supabase.table("kalendar").update({"stav": "zamietnute"}).eq("id", a['id']).execute()
                                if a.get("email"):
                                    posli_email_o_zamietnuti(a.get("email"), a.get("meno", "zákazník"), a.get("datum", ""))
                                st.session_state['db_data'] = nacti_data()
                                st.success("Dopyt zamietnutý a e-mail odoslaný.")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Nepodarilo sa zamietnuť dopyt: {e}")

                    edit_key = f"edit_active_t1_{a['id']}"
                    if edit_key not in st.session_state:
                        st.session_state[edit_key] = False

                    if c3.button("✍️ Upraviť", key=f"btn_edit_t1_{i}"):
                        st.session_state[edit_key] = not st.session_state[edit_key]
                        st.rerun()

                    if st.session_state[edit_key]:
                        with st.form(key=f"form_edit_t1_{a['id']}"):
                            novy_datum = st.text_input("Dátum", value=a.get('datum', ''))
                            novy_cas = st.text_input("Čas", value=a.get('cas', ''))
                            nove_meno = st.text_input("Meno", value=a.get('meno', ''))
                            novy_tel = st.text_input("Telefón", value=a.get('tel', ''))
                            novy_email = st.text_input("E-mail", value=a.get('email', ''))
                            nove_detaily = st.text_area("Miesto/Poznámka", value=info_mesto)

                            if st.form_submit_button("Uložiť zmeny"):
                                upravene = {"datum": novy_datum, "cas": novy_cas, "meno": nove_meno, "tel": novy_tel, "email": novy_email, "detaily": nove_detaily}
                                if supabase:
                                    try:
                                        supabase.table("kalendar").update(upravene).eq("id", a['id']).execute()
                                        st.session_state['db_data'] = nacti_data()
                                        st.session_state[edit_key] = False
                                        st.success("Zmeny uložené!")
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"Chyba úpravy Supabase: {e}")

        with t2:
            schvalene = [a for a in db if a.get("stav") == "schvalene"]
            schvalene.sort(key=lambda x: x['datum'])
            if not schvalene:
                st.info("Kalendár je prázdny.")
            for i, a in enumerate(schvalene):
                info_mesto = a.get('detaily', 'Neuvedené')
                kalkulacia = a.get('vypocitana_cena', 'Nenapočítaná')
                with st.expander(f"📅 {a['datum']} - {a.get('meno', 'Akcia')}"):
                    st.write(f"📞 {a.get('tel', '')} | 🕒 {a.get('cas', '')}")
                    st.write(f"💰 **Orientačná kalkulácia:** {kalkulacia}")
                    st.markdown(f"""<div class="admin-detail-box"><b>Miesto/Poznámka:</b><br>{info_mesto}</div>""", unsafe_allow_html=True)

                    c1, c2 = st.columns(2)

                    if c1.button("❌ Zrušiť akciu", key=f"del{i}"):
                        if supabase:
                            try:
                                supabase.table("kalendar").update({"stav": "zrusene"}).eq("id", a['id']).execute()
                                if a.get("email"):
                                    posli_email_o_zruseni_akcie(a.get("email"), a.get("meno", "zákazník"), a.get("datum", ""))
                                st.session_state['db_data'] = nacti_data()
                                st.success("Akcia zrušená a e-mail odoslaný.")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Nepodarilo sa zrušiť akciu: {e}")

                    edit_key_t2 = f"edit_active_t2_{a['id']}"
                    if edit_key_t2 not in st.session_state:
                        st.session_state[edit_key_t2] = False

                    if c2.button("✍️ Upraviť", key=f"btn_edit_t2_{i}"):
                        st.session_state[edit_key_t2] = not st.session_state[edit_key_t2]
                        st.rerun()

                    if st.session_state[edit_key_t2]:
                        with st.form(key=f"form_edit_t2_{a['id']}"):
                            novy_datum = st.text_input("Dátum", value=a.get('datum', ''))
                            novy_cas = st.text_input("Čas", value=a.get('cas', ''))
                            nove_meno = st.text_input("Meno / Názov", value=a.get('meno', ''))
                            novy_tel = st.text_input("Telefón", value=a.get('tel', ''))
                            novy_email = st.text_input("E-mail", value=a.get('email', ''))
                            nove_detaily = st.text_area("Miesto/Poznámka", value=info_mesto)

                            if st.form_submit_button("Uložiť zmeny"):
                                upravene = {"datum": novy_datum, "cas": novy_cas, "meno": nove_meno, "tel": novy_tel, "email": novy_email, "detaily": nove_detaily}
                                if supabase:
                                    try:
                                        supabase.table("kalendar").update(upravene).eq("id", a['id']).execute()
                                        st.session_state['db_data'] = nacti_data()
                                        st.session_state[edit_key_t2] = False
                                        st.success("Zmeny uložené!")
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"Chyba úpravy Supabase: {e}")

        with t3:
            st.subheader("📁 Nahrať fotky a videá priamo z počítača")
            st.write("Tu môžete nahrať fotky (.jpg, .png) alebo videá (.mp4), ktoré sa ihneď zobrazia v Galérii.")

            subor_na_nahratie = st.file_uploader(
                "Kliknite sem alebo pretiahnite súbor",
                type=["jpg", "jpeg", "png", "gif", "webp", "mp4", "mov", "avi", "webm"],
                key="uploader_medii"
            )

            if subor_na_nahratie is not None:
                if st.button("🚀 NAHRAŤ VYBRANÝ SÚBOR"):
                    if supabase:
                        try:
                            subor_bytes = subor_na_nahratie.read()
                            povodny_nazov = subor_na_nahratie.name
                            cisty_nazov = f"{int(datetime.now().timestamp())}_{povodny_nazov.replace(' ', '_')}"

                            res = supabase.storage.from_("parobci-media").upload(
                                path=cisty_nazov,
                                file=subor_bytes,
                                file_options={"content-type": subor_na_nahratie.type}
                            )

                            if res:
                                st.success(f"Súbor '{povodny_nazov}' bol úspešne nahraný! 🎉")
                                st.rerun()
                        except Exception as e:
                            st.error(f"Chyba pri nahrávaní súboru: {e}")
                    else:
                        st.error("Chyba: Pripojenie k Supabase nie je aktívne.")

            st.markdown("<hr style='border-color: rgba(212,175,55,0.3); margin-top: 30px;'>", unsafe_allow_html=True)
            st.subheader("📸 Všetky médiá v galérii")

            vsetky_media = nacti_vsetky_media()

            if vsetky_media:
                st.write(f"**Počet súborov:** {len(vsetky_media)}")

                for idx, media_item in enumerate(vsetky_media):
                    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])

                    with col1:
                        st.write(f"📄 **{media_item['nazov'][:40]}...**" if len(media_item['nazov']) > 40 else f"📄 **{media_item['nazov']}**")
                    with col2:
                        st.write(f"🏷️ {media_item['typ']}")
                    with col3:
                        velkost_kb = media_item['velkost'] / 1024
                        st.write(f"💾 {velkost_kb:.1f} KB")
                    with col4:
                        if st.button("🗑️", key=f"delete_media_{idx}"):
                            if supabase:
                                try:
                                    supabase.storage.from_("parobci-media").remove([media_item['nazov']])
                                    st.success(f"Súbor '{media_item['nazov']}' vymazaný!")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Chyba pri vymazávaní: {e}")
            else:
                st.info("Galéria je zatiaľ prázdna.")

        with t4:
            with st.form("add_manual"):
                st.subheader("➕ Manuálne pridať akciu")
                d = st.date_input("Dátum akcie", value=datetime.today())
                t_time = st.time_input("Čas začiatku", value=datetime.now().time())
                m = st.text_input("Meno a priezvisko / Názov akcie")
                tel_cislo = st.text_input("Telefónne číslo")
                em_adresa = st.text_input("E-mail")
                dohodnuta_cena = st.text_input("Dohodnutá cena (napr. 500.00 €)", value="0.00 €")
                det = st.text_area("Presná adresa konania (mesto/sála) a iné detaily")

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
                            "stav": "schvalene",
                            "klient_potvrdil_cenu": True
                        }
                        if supabase:
                            try:
                                supabase.table("kalendar").insert(nova_akcia).execute()
                                st.session_state['db_data'] = nacti_data()
                                st.success("Akcia bola úspešne pridaná do kalendára!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Chyba pridania na Supabase: {e}")

        with t5:
            st.subheader("⭐ Správa recenzií")
            recenzie = nacti_recenzie()

            if not recenzie:
                st.info("Zatiaľ nie sú žiadne recenzie.")
            else:
                st.write(f"**Celkovo recenzií:** {len(recenzie)}")
                for idx, rec in enumerate(recenzie):
                    with st.expander(f"⭐ {rec.get('meno', 'Anonymný')} - {hvezdicky_html(rec.get('hvezdicky', 5))}"):
                        st.write(f"**Meno:** {rec.get('meno', 'Anonymný')}")
                        st.write(f"**Hodnotenie:** {hvezdicky_html(rec.get('hvezdicky', 5))}")
                        st.write(f"**Komentár:** {rec.get('text', '')}")
                        st.write(f"**Dátum:** {rec.get('created_at', '')[:10]}")

                        if st.button("🗑️ Vymazať", key=f"del_rec_{idx}"):
                            if supabase:
                                try:
                                    supabase.table("recenzie").delete().eq("id", rec['id']).execute()
                                    st.success("Recenzia vymazaná!")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Chyba pri vymazávaní: {e}")

st.markdown('''
<div style="text-align:center; margin-top:50px; color:#ccc; line-height: 1.6;">
    <b>Podpora</b><br>
    <b>Tel. číslo:</b> 0944 757 122<br>
    <b>E-mail:</b> parobciovcanske@gmail.com
</div>
''', unsafe_allow_html=True)
