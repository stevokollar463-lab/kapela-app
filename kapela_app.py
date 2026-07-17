import streamlit as st
import datetime
import uuid
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests

# Nastavenie stránky Streamlit
st.set_page_config(
    page_title="Ovčánske Parobci - Rezervačný Systém",
    page_icon="🎸",
    layout="wide"
)

# --- POMOCNÉ FUNKCIE (SPOJENIE S ROZHRANIAMI) ---

# 1. Pripojenie k Supabase
def get_supabase_client():
    try:
        from supabase import create_client
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        return create_client(url, key)
    except Exception as e:
        st.error(f"Chyba pri pripájaní k Supabase: {e}")
        return None

supabase = get_supabase_client()

# 2. Odoslanie upozornenia cez Pushbullet
def odoslat_pushbullet(titulok, sprava):
    try:
        api_key = st.secrets.get("PB_API_KEY")
        if api_key:
            headers = {
                "Access-Token": api_key,
                "Content-Type": "application/json"
            }
            data = {
                "type": "note",
                "title": titulok,
                "body": sprava
            }
            response = requests.post("https://api.pushbullet.com/v2/pushes", headers=headers, json=data)
            return response.status_code == 200
    except Exception as e:
        print(f"Pushbullet chyba: {e}")
    return False

# 3. Odoslanie e-mailu cez Gmail
def odoslat_email(prijemca, predmet, text_spravy):
    try:
        sender_email = st.secrets.get("sender_email")
        sender_password = st.secrets.get("sender_password")
        
        if not sender_email or not sender_password:
            return False
            
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = prijemca
        msg['Subject'] = predmet
        
        msg.attach(MIMEText(text_spravy, 'plain', 'utf-8'))
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, prijemca, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"Chyba pri odosielaní emailu: {e}")
        return False

# --- LOGIKA VÝPOČTU CENY (Príklad) ---
def vypocitaj_cenu(datum, adresa):
    # Základná cena za hranie, ktorú si môžeš kedykoľvek upraviť
    zaklad = 450
    return zaklad

# --- DIZAJN A ROZHRANIE ---

st.title("🎸 Rezervačný systém - Ovčánske Parobci")
st.write("Vitajte na našom rezervačnom portáli. Tu si môžete overiť termín a nezáväzne objednať naše vystúpenie.")

# Hlavné menu (Zákaznícka zóna vs. Administrácia)
menu = st.sidebar.radio("Navigácia", ["Rezervácia vystúpenia", "Administrácia pre kapelu"])

# ==========================================
# 1. SEKČNÁ ČASŤ: REZERVÁCIA (PRE ZÁKAZNÍKA)
# ==========================================
if menu == "Rezervácia vystúpenia":
    st.header("📅 Vytvoriť nezáväzný dopyt")
    
    with st.form("rezervacny_formular"):
        st.subheader("Základné informácie o akcii")
        
        col1, col2 = st.columns(2)
        with col1:
            meno = st.text_input("Meno a priezvisko (alebo názov firmy/organizácie)*", placeholder="Ján Mrkvička")
            datum = st.date_input("Dátum konania akcie*", min_value=datetime.date.today())
            cas = st.text_input("Predpokladaný čas začiatku (napr. 18:00)", placeholder="18:00")
            
        with col2:
            tel = st.text_input("Telefónne číslo*", placeholder="+421 9xx xxx xxx")
            email = st.text_input("E-mailová adresa*", placeholder="vasiak@gmail.com")
            adresa = st.text_input("Presná adresa konania akcie (Názov podniku, ulica, mesto)*", placeholder="Prešov Sídlisko 3, Hostinec Konáreň")
            
        detaily = st.text_area("Detaily o akcii (Svadba, životné jubileum, festival, požiadavky na ozvučenie...)", placeholder="Napíšte nám bližšie podrobnosti...")
        
        odoslat = st.form_submit_button("Odoslať nezáväzný dopyt")
        
        if odoslat:
            if not meno or not tel or not email or not adresa or not datum:
                st.error("❌ Prosím, vyplňte všetky povinné polia označené hviezdičkou (*).")
            elif supabase is None:
                st.error("❌ Systém nie je momentálne prepojený s databázou. Kontaktujte nás telefonicky.")
            else:
                # Výpočet ceny
                cena_hodnota = vypocitaj_cenu(datum, adresa)
                cena_text = f"{cena_hodnota} €"
                
                # Generovanie unikátneho ID pre dopyt
                dopyt_id = str(uuid.uuid4())[:8]
                
                # Príprava dát pre Supabase
                novy_dopyt = {
                    "id": dopyt_id,
                    "datum": str(datum),
                    "cas": cas,
                    "meno": meno,
                    "tel": tel,
                    "email": email,
                    "adresa": adresa,
                    "detaily": detaily,
                    "vypocitana_cena": cena_text,
                    "stav": "cakajuce"
                }
                
                try:
                    # Uloženie do Supabase
                    supabase.table("kalendar").insert(novy_dopyt).execute()
                    
                    st.success("🎉 Dopyt bol úspešne odoslaný! Na e-mail sme vám poslali potvrdenie. Čoskoro vás budeme kontaktovať.")
                    st.balloons()
                    
                    # 1. PUSHBULLET UPOZORNENIE PRE KAPELU
                    pb_titulok = f"🎸 Nový dopyt: {meno}"
                    pb_telo = f"Dátum: {datum}\nČas: {cas}\nMiesto: {adresa}\nTel: {tel}\nCena: {cena_text}"
                    odoslat_pushbullet(pb_titulok, pb_telo)
                    
                    # 2. EMAIL PRE KAPELU
                    kapela_email = st.secrets.get("sender_email")
                    if kapela_email:
                        mail_kapela = f"Ahoj,\n\nmáš nový nezáväzný dopyt na webe!\n\n" \
                                      f"Klient: {meno}\n" \
                                      f"Dátum: {datum}\n" \
                                      f"Čas: {cas}\n" \
                                      f"Miesto/Adresa: {adresa}\n" \
                                      f"Tel: {tel}\n" \
                                      f"Email: {email}\n" \
                                      f"Detaily: {detaily}\n" \
                                      f"Predbežná cena: {cena_text}\n\n" \
                                      f"Pre správu objednávok sa prihlás do administrácie webu."
                        odoslat_email(kapela_email, f"Nový dopyt: {meno} - {datum}", mail_kapela)
                    
                    # 3. EMAIL PRE ZÁKAZNÍKA
                    mail_zakaznik = f"Dobrý deň, pán/pani {meno},\n\n" \
                                    f"ďakujeme za váš nezáväzný dopyt pre kapelu Ovčánske Parobci.\n\n" \
                                    f"Zhrnutie dopytu:\n" \
                                    f"Termín: {datum} o {cas or 'neuvedený čas'}\n" \
                                    f"Miesto: {adresa}\n" \
                                    f"Predbežná cena: {cena_text}\n\n" \
                                    f"Váš dopyt momentálne spracovávame a čoskoro vás budeme kontaktovať pre overenie detailov a potvrdenie termínu.\n\n" \
                                    f"S pozdravom,\n" \
                                    f"Ovčánske Parobci\n" \
                                    f"parobciovcanske@gmail.com"
                    odoslat_email(email, "Potvrdenie nezáväzného dopytu - Ovčánske Parobci", mail_zakaznik)
                    
                except Exception as e:
                    st.error(f"⚠️ Nepodarilo sa uložiť dáta do databázy, kontaktujte nás telefonicky. Chyba: {e}")

# ==========================================
# 2. SEKČNÁ ČASŤ: ADMINISTRÁCIA (PRE KAPELU)
# ==========================================
elif menu == "Administrácia pre kapelu":
    st.header("🔒 Prihlásenie do administrácie")
    
    # Overenie hesla a mena
    spravne_meno = st.secrets.get("ADMIN_USER", "admin")
    spravne_heslo = st.secrets.get("ADMIN_PASS", "admin123")
    
    vst_meno = st.sidebar.text_input("Užívateľské meno")
    vst_heslo = st.sidebar.text_input("Heslo", type="password")
    
    if vst_meno == spravne_meno and vst_heslo == spravne_heslo:
        st.success("Úspešne si sa prihlásil!")
        st.sidebar.markdown("---")
        st.sidebar.write("Prihlásený ako: **ovcanskeparobci**")
        
        # --- MANUÁLNE PRIDANIE REZERVÁCIE ---
        with st.expander("➕ Pridať objednávku manuálne (telefonická/osobná dohoda)"):
            with st.form("manualny_formular", clear_on_submit=True):
                col1, col2 = st.columns(2)
                with col1:
                    m_meno = st.text_input("Meno klienta / Názov akcie*")
                    m_datum = st.date_input("Dátum akcie")
                    m_cas = st.text_input("Čas začiatku (napr. 18:00)", placeholder="18:00")
                    m_cena = st.text_input("Dohodnutá cena (€)", placeholder="450 €")
                with col2:
                    m_tel = st.text_input("Telefónne číslo")
                    m_email = st.text_input("E-mail")
                    m_adresa = st.text_input("Presná adresa konania (napr. Prešov Sídlisko 3, Konáreň)")
                    
                m_detaily = st.text_area("Poznámky / Detaily k akcii")
                m_submit = st.form_submit_button("Uložiť akciu do kalendára")
                
                if m_submit:
                    if not m_meno:
                        st.error("Meno alebo názov akcie je povinný údaj!")
                    elif supabase is None:
                        st.error("Chyba: Databáza nie je pripojená!")
                    else:
                        manual_id = f"man_{uuid.uuid4().hex[:8]}"
                        
                        manualne_data = {
                            "id": manual_id,
                            "datum": str(m_datum),
                            "cas": m_cas,
                            "meno": m_meno,
                            "tel": m_tel,
                            "email": m_email,
                            "adresa": m_adresa,
                            "detaily": m_detaily,
                            "vypocitana_cena": m_cena,
                            "stav": "schvalene"  # Manuálne zadaná akcia je rovno schválená
                        }
                        
                        try:
                            supabase.table("kalendar").insert(manualne_data).execute()
                            st.success(f"Akcia '{m_meno}' úspešne pridaná priamo do kalendára!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Chyba pri ukladaní manuálnej akcie: {e}")
                            
        st.markdown("---")
        st.subheader("📋 Zoznam všetkých rezervácií")
        
        # Načítanie rezervácií zo Supabase
        if supabase:
            try:
                odpoved = supabase.table("kalendar").select("*").order("datum", desc=False).execute()
                rezervacie = odpoved.data
                
                if not rezervacie:
                    st.info("V databáze zatiaľ nie sú žiadne dopyty.")
                else:
                    # Filtre stavu pre prehľadnosť
                    filter_stav = st.selectbox("Filtrovať podľa stavu:", ["Všetky", "Iba čakajúce na schválenie", "Iba schválené / zazmluvnené"])
                    
                    for rez in rezervacie:
                        stav = rez.get("stav", "cakajuce")
                        
                        # Aplikovanie filtrov
                        if filter_stav == "Iba čakajúce na schválenie" and stav != "cakajuce":
                            continue
                        if filter_stav == "Iba schválené / zazmluvnené" and stav != "schvalene":
                            continue
                        
                        ikona = "⏳ Čakajúce" if stav == "cakajuce" else "✅ Schválené"
                        
                        # Vykreslenie peknej ohraničenej karty s dopytom
                        with st.container(border=True):
                            col_info, col_akcie = st.columns([3, 1])
                            
                            with col_info:
                                st.markdown(f"### {ikona} - {rez['meno']}")
                                st.markdown(f"📅 **Dátum:** {rez['datum']} | 🕒 **Čas:** {rez['cas'] or 'Neuvedený'}")
                                
                                c1, c2 = st.columns(2)
                                with c1:
                                    st.write(f"📞 **Tel:** {rez['tel'] or 'Neuvedené'}")
                                    st.write(f"✉️ **E-mail:** {rez['email'] or 'Neuvedené'}")
                                with c2:
                                    st.write(f"📍 **Presná Adresa:** {rez['adresa'] or 'Neuvedená'}")
                                    st.write(f"💰 **Cena:** {rez['vypocitana_cena'] or 'Neuvedená'}")
                                    
                                if rez['detaily']:
                                    st.info(f"📝 **Poznámka / Detaily:** {rez['detaily']}")
                                    
                            with col_akcie:
                                st.write("")
                                st.write("")
                                if stav == "cakajuce":
                                    if st.button("Schváliť rezerváciu", key=f"schval_{rez['id']}"):
                                        try:
                                            supabase.table("kalendar").update({"stav": "schvalene"}).eq("id", rez["id"]).execute()
                                            
                                            # Odoslanie potvrdzujúceho emailu zákazníkovi
                                            if rez['email']:
                                                mail_potvrdenie = f"Dobrý deň, pán/pani {rez['meno']},\n\n" \
                                                                  f"s radosťou vám oznamujeme, že váš termín {rez['datum']} na akciu v {rez['adresa']} bol schválený a pevne rezervovaný v našom kalendári!\n\n" \
                                                                  f"Tešíme sa na spoločné hranie!\n\n" \
                                                                  f"S pozdravom,\n" \
                                                                  f"Ovčánske Parobci"
                                                odoslat_email(rez['email'], "REZERVOVANÉ! Váš termín bol potvrdený - Ovčánske Parobci", mail_potvrdenie)
                                                
                                            st.success("Rezervácia schválená a e-mail odoslaný!")
                                            st.rerun()
                                        except Exception as e:
                                            st.error(f"Chyba pri schvaľovaní: {e}")
                                            
                                if st.button("Vymazať / Odmietnuť", key=f"zmaz_{rez['id']}"):
                                    try:
                                        supabase.table("kalendar").delete().eq("id", rez["id"]).execute()
                                        st.warning("Objednávka bola vymazaná!")
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"Chyba pri mazaní: {e}")
                                        
            except Exception as e:
                st.error(f"Nepodarilo sa načítať dáta zo Supabase: {e}")
        else:
            st.error("Chyba spojenia s databázou.")
            
    else:
        if vst_meno or vst_heslo:
            st.sidebar.error("❌ Nesprávne meno alebo heslo.")
        st.info("Zadajte prihlasovacie údaje v ľavom paneli na vstup do administrácie.")
