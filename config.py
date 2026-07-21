
import streamlit as st

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
    raise RuntimeError(f"Chýba secret: {e.args[0]}")

KAPELA_FOTO_URL = "https://i.postimg.cc/T1Pkgjnw/1000027016.jpg"

CENA_OSLAVA_HODINA = 120
CENA_SPRIEVOD_ZAKLAD = 250
CENA_SPRIEVOD_POLHODINA = 50
CENA_STOLY_HODINA = 120
CENA_APARATURA = 100
CENA_ZA_KM = 0.50
