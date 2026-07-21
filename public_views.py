import streamlit as st
import secrets
import urllib.parse
from datetime import datetime, timedelta

from config import (
    CENA_OSLAVA_HODINA,
    CENA_SPRIEVOD_ZAKLAD,
    CENA_SPRIEVOD_POLHODINA,
    CENA_STOLY_HODINA,
    CENA_APARATURA,
    CENA_ZA_KM,
    APP_BASE_URL,
)
from database import supabase, nacti_data, nacti_media, nacti_recenzie
from notifications import posli_upozornenie
from email_service import (
    posli_email_zakaznikovi_s_potvrdenim,
    posli_email_adminovi_o_potvrdeni,
    posli_email_o_potvrdeni_zakaznikovi,
)
from utils import zobraz_kalendar_obsadenosti, hvezdicky_html
from components import zobraz_footer_tlacidla


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


def render_rezervacia():
    st.session_state["page_id"] = "rezervacia"
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
            popis_hudby = f"Svadobný sprievod (2 hod. + {polhodiny_navyse}x polhodina navyše)" if polhodiny_navyse > 0 else "Svadobný sprievod (základ do 2 hod.)"

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

    st.info("💡 Vypočítaná cena vám príde na e-mail na potvrdenie.")

    if "db_data" not in st.session_state:
        st.session_state["db_data"] = nacti_data()

    with st.expander("📅 Zobraziť kalendár obsadenosti"):
        dnes = datetime.now().date()
        col_m1, col_m2 = st.columns(2)

        with col_m1:
            vybrany_rok = st.number_input("Rok", min_value=dnes.year, max_value=dnes.year + 3, value=dnes.year, step=1)

        with col_m2:
            vybrany_mesiac = st.selectbox("Mesiac", options=list(range(1, 13)), index=dnes.month - 1, format_func=lambda m: f"{m:02d}")

        kal_html = zobraz_kalendar_obsadenosti(st.session_state["db_data"], int(vybrany_rok), int(vybrany_mesiac))
        st.markdown(kal_html, unsafe_allow_html=True)

    with st.form("main_booking"):
        st.subheader("📩 Rezervačný dopyt")

        col1, col2 = st.columns(2)
        with col1:
            datum = st.date_input("Dátum akcie", min_value=datetime.now().date())
        with col2:
            cas = st.time_input("Čas začiatku")

        meno = st.text_input("Meno a priezvisko")
        tel = st.text_input("Telefónne číslo")
        email = st.text_input("E-mail")
        mesto_detaily = st.text_area("Presná adresa konania (mesto/sála) a iné detaily")

        if st.form_submit_button("ODOSLAŤ REZERVÁCIU S TOUTO CENOU"):
            db = nacti_data()

            if any(a["datum"] == str(datum) for a in db if a.get("stav") == "schvalene"):
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
                            st.session_state["db_data"] = nacti_data()
                            posli_upozornenie(f"Nový dopyt: {datum}\n{meno} ({tel})\nTyp: {typ_akcie}\nMiesto: {mesto_detaily}\nCena: {vypocitana_cena_txt}")
                            posli_email_zakaznikovi_s_potvrdenim(
                                email, meno, str(datum), cas.strftime("%H:%M"),
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


def render_cennik():
    st.session_state["page_id"] = "cennik"
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
                <tr><td style="padding: 12px; font-weight: bold;">🎂 Rodinná oslava / Jubileum</td><td style="padding: 12px; color: #d4af37; font-weight: bold;">{CENA_OSLAVA_HODINA} € / hodina</td><td style="padding: 12px; color: #ccc; font-size: 0.9rem;">Živé hranie na oslavách.</td></tr>
                <tr><td style="padding: 12px; font-weight: bold;">👰 Svadobný sprievod a odobierka</td><td style="padding: 12px; color: #d4af37; font-weight: bold;">{CENA_SPRIEVOD_ZAKLAD} € základ</td><td style="padding: 12px; color: #ccc; font-size: 0.9rem;">Do 2 hodín. Každá ďalšia polhodina +{CENA_SPRIEVOD_POLHODINA} €.</td></tr>
                <tr><td style="padding: 12px; font-weight: bold;">🍻 Hranie pomedzi stoly / Posedenie</td><td style="padding: 12px; color: #d4af37; font-weight: bold;">{CENA_STOLY_HODINA} € / hodina</td><td style="padding: 12px; color: #ccc; font-size: 0.9rem;">Komorné akustické hranie naživo.</td></tr>
                <tr><td style="padding: 12px; font-weight: bold;">🎤 Profesionálna zvuková aparatúra</td><td style="padding: 12px; color: #d4af37; font-weight: bold;">+{CENA_APARATURA} € jednorazovo</td><td style="padding: 12px; color: #ccc; font-size: 0.9rem;">Pre väčšie sály/vonku.</td></tr>
                <tr><td style="padding: 12px; font-weight: bold;">🚗 Doprava (z obce Ovčie)</td><td style="padding: 12px; color: #d4af37; font-weight: bold;">{CENA_ZA_KM:.2f} € / km</td><td style="padding: 12px; color: #ccc; font-size: 0.9rem;">Počíta sa cesta tam aj späť.</td></tr>
            </table>
        </div>
    """, unsafe_allow_html=True)
    zobraz_footer_tlacidla()


def render_onas():
    st.session_state["page_id"] = "onas"
    st.title("ℹ️ O nás")
    st.markdown("""
        <div class="o-nas-box">
            <h3 style="color: #d4af37; text-align: center;">🎻 Sme Ovčanske Parobci</h3>
            <div class="o-nas-text">
                <p>Sme ľudová kapela založená v roku <strong>2020</strong>, ktorá sa špecializuje na vytváranie nezabudnuteľných zážitkov na najrôznejších podujatiach.</p>
                <p><strong>Čo robíme:</strong></p>
                <ul style="color: #ccc;">
                    <li>🎂 Jubileá a oslavy narodenín</li>
                    <li>👰 Svadobné sprievody a sprevody novomanželov</li>
                    <li>🎉 Vystúpenia na rodinných a firemných akciách</li>
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
    st.markdown("""<div style="text-align:center; margin-bottom:10px; color:#ccc;">Obec Ovčie, Slovensko</div>""", unsafe_allow_html=True)
    st.components.v1.iframe("https://www.google.com/maps?q=Ov%C4%8Die,+Slovensko&output=embed", height=400, scrolling=False)
    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
    zobraz_footer_tlacidla()


def render_galeria():
    st.session_state["page_id"] = "galeria"
    st.title("📸 Galéria a Videá")
    media = nacti_media()

    if media["videa"]:
        st.subheader("🎥 Videá z našich akcií")
        col_v1, col_v2 = st.columns(2)
        for idx, video_url in enumerate(media["videa"]):
            with (col_v1 if idx % 2 == 0 else col_v2):
                st.video(video_url)

    st.subheader("🖼️ Fotogaléria")
    if media["fotky"]:
        col_img1, col_img2 = st.columns(2)
        for idx, f in enumerate(media["fotky"]):
            with (col_img1 if idx % 2 == 0 else col_img2):
                st.image(f, use_container_width=True)
    else:
        st.info("📸 Galéria je zatiaľ prázdna. Fotky budú pridané čoskoro.")

    zobraz_footer_tlacidla()


def render_recenzie_page():
    st.session_state["page_id"] = "recenzie"
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
    else:
        st.info("Zatiaľ tu nie sú žiadne recenzie. Buď prvý a nechaj svoj ohlas! 😊")

    zobraz_footer_tlacidla()
