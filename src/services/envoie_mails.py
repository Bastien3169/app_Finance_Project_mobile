import smtplib
from email.message import EmailMessage

# ---- Variables simples pour test ----
SMTP_EMAIL = "jolie.mountain@gmail.com"
SMTP_PASS = "oxwp quqm exbt bgjx"  # mot de passe spécifique application
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465

def envoie_password_reset_email(to_email, token):
    reset_link = f"http://localhost:8550/reset-password?token={token}"

    msg = EmailMessage()
    msg['Subject'] = "Réinitialisation de votre mot de passe"
    msg['From'] = SMTP_EMAIL
    msg['To'] = to_email
    msg.set_content(
        f"Pour réinitialiser votre mot de passe, clique sur ce lien : {reset_link}\n"
        f"Ce lien expire dans 1 heure."
    )

    with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as smtp:
        smtp.login(SMTP_EMAIL, SMTP_PASS)
        smtp.send_message(msg)
