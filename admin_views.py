import streamlit as st
from config import LOGIN_MENO, LOGIN_HESLO


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
    else:
        with col_logout:
            st.write("")
            if st.button("Odhlásiť sa", key="logout_btn"):
                st.session_state["auth"] = False
                st.rerun()

        st.success("✅ Prihlásený admin režim funguje.")
        st.info("Sem teraz vlož celý pôvodný admin blok z tvojej appky, alebo ti ho v ďalšej správe rozsekám komplet.")
