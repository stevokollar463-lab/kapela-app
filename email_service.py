import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import streamlit as st
from config import SENDER_EMAIL, SENDER_PASSWORD, ADMIN_NOTIFY_EMAIL


def send_email(to_email, subject, plain_body, html_body=None):
    if not to_email or "@" not in to_email or not SENDER_PASSWORD:
        return False

    try:
        msg = MIMEMultipart("alternative")
        msg["From"] = SENDER_EMAIL
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(plain_body, "plain", "utf-8"))

        if html_body:
            msg.attach(MIMEText(html_body, "html", "utf-8"))

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, to_email, msg.as_string())

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
