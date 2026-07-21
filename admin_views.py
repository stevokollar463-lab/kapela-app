import streamlit as st
from datetime import datetime

from config import LOGIN_MENO, LOGIN_HESLO
from database import supabase, nacti_data, nacti_recenzie, nacti_vsetky_media
from email_service import posli_email_o_zamietnuti, posli_email_o_zruseni_akcie
from utils import hvezdicky_html


def render_admin():
    st.session_state["page_id"] = "admin"

    col_title, col_logout = st.columns([3, 1])
    with col_title:
        st.title("🔐 Administrácia")

    if "auth" not in st.session_state:
        st.session_state["auth"] = False

    if not st.session_state["auth"]:
        with st.form("login"):
            u = st.text_input("Meno")
            h = st.text_input("Heslo", type="password")

            if st.form_submit_button("Vstúpiť"):
                if u == LOGIN_MENO and h == LOGIN_HESLO:
                    st.session_state["auth"] = True
                    st.rerun()
                else:
                    st.error("❌ Nesprávne prihlasovacie údaje!")
        return

    with col_logout:
        st.write("")
        if st.button("Odhlásiť sa", key="logout_btn"):
            st.session_state["auth"] = False
            st.rerun()

    t1, t2, t3, t4, t5 = st.tabs([
        "📩 Nové dopyty",
        "📅 Kalendár",
        "📁 Správa médií",
        "➕ Pridať udalosť",
        "⭐ Recenzie"
    ])

    db = nacti_data()

    with t1:
        cakajuce = [a for a in db if a.get("stav") == "cakajuce"]

        if not cakajuce:
            st.info("Žiadne nové dopyty.")

        for i, a in enumerate(cakajuce):
            info_mesto = a.get("detaily", "Neuvedené")
            kalkulacia = a.get("vypocitana_cena", "Nenapočítaná")

            with st.expander(f"DOPYT: {a['datum']} - {a.get('meno', 'Neznámy')}"):
                st.write(f"📞 **Kontakt:** {a.get('tel', '---')} | 📧 {a.get('email', '---')}")
                st.write(f"🕒 **Čas:** {a.get('cas', '---')}")
                st.write(f"💰 **Cena:** {kalkulacia}")

                if a.get("klient_potvrdil_cenu", False):
                    st.success("✅ Klient POTVRDIL cenu")
                else:
                    st.warning("⌛ Klient ešte NEPOTVRDIL cenu")

                st.markdown(
                    f"""<div class="admin-detail-box"><b>Miesto a detaily:</b><br>{info_mesto}</div>""",
                    unsafe_allow_html=True
                )

                c1, c2, c3 = st.columns(3)

                if c1.button("✅ Schváliť", key=f"ok{i}"):
                    if not a.get("klient_potvrdil_cenu", False):
                        st.error("Klient ešte nepotvrdil cenu. Najprv musí potvrdiť cez e-mail.")
                    else:
                        if supabase:
                            try:
                                supabase.table("kalendar").update({"stav": "schvalene"}).eq("id", a["id"]).execute()
                                st.session_state["db_data"] = nacti_data()
                                st.success("Dopyt schválený!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Nepodarilo sa schváliť v Supabase: {e}")

                if c2.button("❌ Zamietnuť", key=f"no{i}"):
                    if supabase:
                        try:
                            supabase.table("kalendar").update({"stav": "zamietnute"}).eq("id", a["id"]).execute()

                            if a.get("email"):
                                posli_email_o_zamietnuti(
                                    a.get("email"),
                                    a.get("meno", "zákazník"),
                                    a.get("datum", "")
                                )

                            st.session_state["db_data"] = nacti_data()
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
                        novy_datum = st.text_input("Dátum", value=a.get("datum", ""))
                        novy_cas = st.text_input("Čas", value=a.get("cas", ""))
                        nove_meno = st.text_input("Meno", value=a.get("meno", ""))
                        novy_tel = st.text_input("Telefón", value=a.get("tel", ""))
                        novy_email = st.text_input("E-mail", value=a.get("email", ""))
                        nove_detaily = st.text_area("Miesto/Poznámka", value=info_mesto)

                        if st.form_submit_button("Uložiť zmeny"):
                            upravene = {
                                "datum": novy_datum,
                                "cas": novy_cas,
                                "meno": nove_meno,
                                "tel": novy_tel,
                                "email": novy_email,
                                "detaily": nove_detaily
                            }

                            if supabase:
                                try:
                                    supabase.table("kalendar").update(upravene).eq("id", a["id"]).execute()
                                    st.session_state["db_data"] = nacti_data()
                                    st.session_state[edit_key] = False
                                    st.success("Zmeny uložené!")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Chyba úpravy Supabase: {e}")

    with t2:
        schvalene = [a for a in db if a.get("stav") == "schvalene"]
        schvalene.sort(key=lambda x: x["datum"])

        if not schvalene:
            st.info("Kalendár je prázdny.")

        for i, a in enumerate(schvalene):
            info_mesto = a.get("detaily", "Neuvedené")
            kalkulacia = a.get("vypocitana_cena", "Nenapočítaná")

            with st.expander(f"📅 {a['datum']} - {a.get('meno', 'Akcia')}"):
                st.write(f"📞 {a.get('tel', '')} | 🕒 {a.get('cas', '')}")
                st.write(f"💰 **Orientačná kalkulácia:** {kalkulacia}")
                st.markdown(
                    f"""<div class="admin-detail-box"><b>Miesto/Poznámka:</b><br>{info_mesto}</div>""",
                    unsafe_allow_html=True
                )

                c1, c2 = st.columns(2)

                if c1.button("❌ Zrušiť akciu", key=f"del{i}"):
                    if supabase:
                        try:
                            supabase.table("kalendar").update({"stav": "zrusene"}).eq("id", a["id"]).execute()

                            if a.get("email"):
                                posli_email_o_zruseni_akcie(
                                    a.get("email"),
                                    a.get("meno", "zákazník"),
                                    a.get("datum", "")
                                )

                            st.session_state["db_data"] = nacti_data()
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
                        novy_datum = st.text_input("Dátum", value=a.get("datum", ""))
                        novy_cas = st.text_input("Čas", value=a.get("cas", ""))
                        nove_meno = st.text_input("Meno / Názov", value=a.get("meno", ""))
                        novy_tel = st.text_input("Telefón", value=a.get("tel", ""))
                        novy_email = st.text_input("E-mail", value=a.get("email", ""))
                        nove_detaily = st.text_area("Miesto/Poznámka", value=info_mesto)

                        if st.form_submit_button("Uložiť zmeny"):
                            upravene = {
                                "datum": novy_datum,
                                "cas": novy_cas,
                                "meno": nove_meno,
                                "tel": novy_tel,
                                "email": novy_email,
                                "detaily": nove_detaily
                            }

                            if supabase:
                                try:
                                    supabase.table("kalendar").update(upravene).eq("id", a["id"]).execute()
                                    st.session_state["db_data"] = nacti_data()
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
                    if len(media_item["nazov"]) > 40:
                        st.write(f"📄 **{media_item['nazov'][:40]}...**")
                    else:
                        st.write(f"📄 **{media_item['nazov']}**")

                with col2:
                    st.write(f"🏷️ {media_item['typ']}")

                with col3:
                    velkost_kb = media_item["velkost"] / 1024
                    st.write(f"💾 {velkost_kb:.1f} KB")

                with col4:
                    if st.button("🗑️", key=f"delete_media_{idx}"):
                        if supabase:
                            try:
                                supabase.storage.from_("parobci-media").remove([media_item["nazov"]])
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
                        "cas": t_time.strftime("%H:%M"),
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
                            st.session_state["db_data"] = nacti_data()
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
                                supabase.table("recenzie").delete().eq("id", rec["id"]).execute()
                                st.success("Recenzia vymazaná!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Chyba pri vymazávaní: {e}")
