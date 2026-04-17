import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
from pushbullet import Pushbullet

# --- KONFIGURÁCIA ---
DB_FILE = "kalendar_kapely.json"
PB_API_KEY = "o.Ir4LWAKm78pwEhpKkAf6WZY9uZPNCkSm"
LOGIN_MENO = "ovcanskeparobci"
LOGIN_HESLO = "OvcanskeParobci123"

# Priamy link na vašu fotku z ImgBB
KAPELA_FOTO_URL = "https://i.ibb.co/KzBTbwLR/image-2ec9e6.jpg" 

# --- BRUTÁLNY DIZAJN (CSS) ---
def apply_style():
    st.markdown(f"""
        <style>
        /* Hlavné pozadie a písmo */
        .stApp {{ background-color: #0e1117; color: #ffffff; }}
        [data-testid="stSidebar"] {{ background-color: #161b22; border-right: 2px solid #d4af37; }}
        
        /* Zlaté nadpisy */
        h1, h2, h3 {{ 
            color: #d4af37 !important; 
            font-family: 'Playfair Display', serif; 
            text-transform: uppercase; 
            letter-spacing: 2px; 
            text-align: center;
        }}
        
        /* Štýlové tlačidlá */
        .stButton>button {{ 
            background-color: #d4af37 !important; 
            color: black !important; 
            border-radius: 20px !important; 
            border: none !important; 
            font-weight: bold !important; 
            transition: 0.3s; 
            width: 100%;
        }}
        .stButton>button:hover {{ 
            transform: scale(1.02); 
            box-shadow: 0px 0px 15px #d4af37; 
        }}
        
        /* Päta stránky */
        .footer-text {{ 
            text-align: center; 
            color: #808080; 
            font-size: 0.85rem; 
            margin-top: 50px; 
            padding: 20px; 
            border-top: 1px solid #333; 
        }}
        
        /* Obrázky so zlatým rámom */
        .stImage>img {{ 
            border-radius: 15px; 
            border: 3px solid #d4af37; 
            box-shadow: 0px 10px 30px rgba(0,0,0,0.5);
        }}
        
        /* Úprava formulárov */
        .stForm {{
            border: 1px solid #333 !important;
            border-radius: 15px;
            padding: 20px;
        }}
        </style>
    """, unsafe_allow_html=True)

# --- FUNKCIE PRE DÁTA ---
def nacti_data():
    if not os.path.exists(DB_FILE): return []
    try:
        with open(DB_FILE, "r") as f: return json.load(f)
    except: return []

def uloz_data(data):
    with open(DB_FILE, "w") as f: json.dump(data, f, indent=4)

def posli_upozornenie(text):
    try:
        pb = Pushbullet(PB_API_KEY)
        pb.push_note("🎸 OVČANSKE PAROBCI", text)
        return True
    except: return False

def footer():
    st.markdown(f"""
        <div class="footer-text">
            V prípade technických problémov kontaktujte správcu:<br>
            📞 <b>0944 757 122</b> | ✉️ <b>kollarstevo55@gmail.com</b>
        </div>
    """, unsafe_allow_html=True)

# --- KONFIGURÁCIA STRÁNKY ---
st.set_page_config(page_title="Ovčanske Parobci | Rezervácie", page_icon="🎻", layout="centered")
apply_style()

# --- SIDEBAR (Bočný panel) ---
st.sidebar.image(KAPELA_FOTO_URL, use_container_width=True)
st.sidebar.markdown("<h3 style='text-align: center;'>MENU</h3>", unsafe_allow_html=True)
menu_moznost = st.sidebar.radio("", ["🎸 Chceme vás na akciu", "🔐 Vstup pre kapelu"])

# --- 1. VEREJNÁ ČASŤ (Web pre ľudí) ---
if menu_moznost == "🎸 Chceme vás na akciu":
    st.image(KAPELA_FOTO_URL, use_container_width=True)
    st.title("🎻 Ovčanske Parobci")
    st.markdown("<h3 style='text-align: center;'>Zaručená ľudová zábava pre každého</h3>", unsafe_allow_html=True)
    
    st.write("Máte pred sebou dôležitú životnú udalosť? Svadbu, jubileum alebo oslavu? Ovčanske Parobci sa postarajú o to, aby sa o vašej akcii hovorilo ešte dlho!")
    
    st.divider()
    
    st.subheader("📩 Zistiť dostupnosť termínu")
    
    with st.form("form_rezervacia"):
        d = st.date_input("Kedy sa bude žúrovať?", min_value=datetime.now())
        c = st.time_input("Približný čas začiatku")
        m = st.text_input("Vaše meno a telefónne číslo")
        p = st.text_area("O akú akciu ide? (miesto, typ akcie, počet hostí...)")
        
        submit = st.form_submit_button("ODOSLAŤ NEZÁVÄZNÝ DOPYT")
        
        if submit:
            data = nacti_data()
            if any(a['datum'] == str(d) for a in data):
                st.error(f"Prepáčte, termín {d} už máme obsadený. Skúste si prosím vybrať iný dátum.")
            elif not m:
                st.warning("Prosím, napíšte nám vaše kontaktné údaje.")
            else:
                text_notif = f"NOVÝ DOPYT!\nKedy: {d} o {c}\nKontakt: {m}\nDetaily: {p}"
                if posli_upozornenie(text_notif):
                    st.balloons()
                    st.success("Vaša požiadavka bola úspešne odoslaná! Čoskoro sa vám ozveme. ✅")

# --- 2. ADMIN ČASŤ (Správa pre kapelu) ---
else:
    st.title("🔐 Sekcia pre členov")
    
    if 'auth' not in st.session_state: st.session_state['auth'] = False

    if not st.session_state['auth']:
        st.info("Pre prístup k správe kalendára sa prihláste.")
        v_meno = st.text_input("Užívateľ")
        v_heslo = st.text_input("Heslo", type="password")
        if st.button("PRIHLÁSIŤ SA"):
            if v_meno == LOGIN_MENO and v_heslo == LOGIN_HESLO:
                st.session_state['auth'] = True
                st.rerun()
            else: st.error("Nesprávne meno alebo heslo!")
    else:
        st.sidebar.success("Ste prihlásený")
        if st.sidebar.button("ODHLÁSIŤ SA"):
            st.session_state['auth'] = False
            st.rerun()

        t1, t2 = st.tabs(["➕ Pridať novú akciu", "📅 Plánované termíny"])
        
        with t1:
            with st.form("add_form"):
                d_in = st.date_input("Dátum akcie")
                c_in = st.time_input("Čas")
                p_in = st.text_input("Názov / Miesto konania")
                if st.form_submit_button("ULOŽIŤ DO KALENDÁRA"):
                    data = nacti_data()
                    data.append({
                        "id": str(datetime.now().timestamp()), 
                        "datum": str(d_in), 
                        "cas": str(c_in), 
                        "poznamka": p_in
                    })
                    uloz_data(data)
                    st.success("Akcia bola úspešne zapísaná!")

        with t2:
            data = nacti_data()
            if data:
                data.sort(key=lambda x: x['datum'])
                for idx, a in enumerate(data):
                    with st.expander(f"📅 {a['datum']} - {a['poznamka']}"):
                        new_date = st.date_input("Dátum", value=datetime.strptime(a['datum'], '%Y-%m-%d'), key=f"date_{idx}")
                        new_time = st.text_input("Čas", value=a['cas'], key=f"time_{idx}")
                        new_note = st.text_input("Miesto/Názov", value=a['poznamka'], key=f"note_{idx}")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("💾 Uložiť zmeny", key=f"save_{idx}"):
                                data[idx]['datum'] = str(new_date)
                                data[idx]['cas'] = new_time
                                data[idx]['poznamka'] = new_note
                                uloz_data(data)
                                st.success("Zmenené!")
                                st.rerun()
                        with col2:
                            if st.button("🗑️ Vymazať", key=f"del_{idx}"):
                                data.pop(idx)
                                uloz_data(data)
                                st.rerun()
                
                st.divider()
                if st.button("🗑️ VYMAZAŤ CELÝ KALENDÁR"):
                    uloz_data([])
                    st.rerun()
            else:
                st.write("Zatiaľ nemáte žiadne naplánované akcie.")

footer()
