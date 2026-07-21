import streamlit as st
from datetime import datetime
from database import supabase
from config import (
    CENA_OSLAVA_HODINA,
    CENA_SPRIEVOD_ZAKLAD,
    CENA_STOLY_HODINA,
    CENA_ZA_KM,
)
from utils import hvezdicky_html


def render_faq_section():
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


def render_kontakt_section():
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


def render_recenzia_form():
    page_id = st.session_state.get("page_id", "main")

    st.markdown('<div class="expandable-section">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">⭐ Zanechaj svoj ohlas</div>', unsafe_allow_html=True)

    typ_mena = st.radio(
        "Ako sa chceš reprezentovať?",
        ["❌ Anonymne", "✅ Pod mojim menom"],
        horizontal=True,
        key=f"radio_rec_{page_id}"
    )

    meno_input = ""
    if typ_mena == "✅ Pod mojim menom":
        meno_input = st.text_input(
            "Tvoje meno",
            placeholder="Napíš svoje meno...",
            key=f"input_meno_{page_id}"
        )

    with st.form(f"nova_recenzia_{page_id}"):
        hvezdicky = st.slider(
            "Ako hodnotíš našu kapelu? (1-5 hviezd)",
            min_value=1,
            max_value=5,
            value=5,
            key=f"slider_rec_{page_id}"
        )

        text = st.text_area(
            "Tvoj komentár",
            placeholder="Napíš nám tvoj názor na naše vystúpenie...",
            height=120,
            key=f"textarea_rec_{page_id}"
        )

        if st.form_submit_button("🚀 ODOSLAŤ RECENZIU", key=f"submit_rec_{page_id}"):
            if not text or len(text.strip()) < 5:
                st.warning("⚠️ Napíš prosím aspoň pár slov do komentára!")
            elif typ_mena == "✅ Pod mojim menom" and not meno_input.strip():
                st.warning("⚠️ Ak chceš recenziu pod menom, vyplň prosím svoje meno.")
            else:
                meno = meno_input.strip() if typ_mena == "✅ Pod mojim menom" else "Anonymný"

                nova_recenzia = {
                    "id": str(datetime.now().timestamp()),
                    "meno": meno,
                    "hvezdicky": hvezdicky,
                    "text": text.strip(),
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
                            st.error("Chyba: Recenzia sa nepodarila uložiť.")
                    except Exception as e:
                        st.error(f"Chyba: {e}")
                else:
                    st.error("Chyba: Databáza Supabase nie je pripojená!")

    st.markdown('</div>', unsafe_allow_html=True)


def zobraz_footer_tlacidla():
    page_id = st.session_state.get("page_id", "main")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("❓ FAQ", key=f"btn_faq_{page_id}", use_container_width=True):
            st.session_state[f"expand_faq_{page_id}"] = not st.session_state.get(f"expand_faq_{page_id}", False)
            st.rerun()

    with col2:
        if st.button("⭐ RECENZIE", key=f"btn_rec_{page_id}", use_container_width=True):
            st.session_state[f"expand_rec_{page_id}"] = not st.session_state.get(f"expand_rec_{page_id}", False)
            st.rerun()

    with col3:
        if st.button("📞 KONTAKT", key=f"btn_kon_{page_id}", use_container_width=True):
            st.session_state[f"expand_kon_{page_id}"] = not st.session_state.get(f"expand_kon_{page_id}", False)
            st.rerun()

    if st.session_state.get(f"expand_faq_{page_id}", False):
        render_faq_section()

    if st.session_state.get(f"expand_rec_{page_id}", False):
        render_recenzia_form()

    if st.session_state.get(f"expand_kon_{page_id}", False):
        render_kontakt_section()
