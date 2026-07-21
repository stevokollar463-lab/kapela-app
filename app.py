import streamlit as st
from styles import apply_style
from public_views import (
    process_confirmation_from_query,
    render_rezervacia,
    render_cennik,
    render_onas,
    render_galeria,
    render_recenzie_page,
)
from admin_views import render_admin
from database import nacti_data

st.set_page_config(
    page_title="Ovčanske Parobci",
    page_icon="🎻",
    layout="centered",
    initial_sidebar_state="collapsed"
)

apply_style()
process_confirmation_from_query()

menu = st.radio(
    "NAVIGÁCIA",
    ["🎸 Rezervácia", "💰 Cenník", "ℹ️ O nás", "📸 Galéria", "⭐ Recenzie", "🔐 Administrácia"],
    horizontal=True,
    label_visibility="collapsed"
)

st.markdown("<br>", unsafe_allow_html=True)

if "db_data" not in st.session_state:
    st.session_state["db_data"] = nacti_data()

if menu == "🎸 Rezervácia":
    render_rezervacia()
elif menu == "💰 Cenník":
    render_cennik()
elif menu == "ℹ️ O nás":
    render_onas()
elif menu == "📸 Galéria":
    render_galeria()
elif menu == "⭐ Recenzie":
    render_recenzie_page()
else:
    render_admin()

st.markdown('''
<div style="text-align:center; margin-top:50px; color:#ccc; line-height: 1.6;">
    <b>Podpora</b><br>
    <b>Tel. číslo:</b> 0944 757 122<br>
    <b>E-mail:</b> parobciovcanske@gmail.com
</div>
''', unsafe_allow_html=True)
