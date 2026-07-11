import smtplib
from email.message import EmailMessage

from config import Config


def send_email(subject, recipient, body):
    if not Config.SMTP_HOST or not Config.SMTP_FROM:
        print(f"[EMAIL] {subject} -> {recipient}\n{body}")
        return False

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = Config.SMTP_FROM
    message["To"] = recipient
    message.set_content(body)

    if Config.SMTP_USE_SSL:
        server = smtplib.SMTP_SSL(Config.SMTP_HOST, Config.SMTP_PORT)
    else:
        server = smtplib.SMTP(Config.SMTP_HOST, Config.SMTP_PORT)
        if Config.SMTP_STARTTLS:
            server.starttls()

    if Config.SMTP_USER and Config.SMTP_PASSWORD:
        server.login(Config.SMTP_USER, Config.SMTP_PASSWORD)

    server.send_message(message)
    server.quit()
    return True


def send_activation_email(recipient_email, full_name, activation_token):
    activation_url = f"{Config.ACTIVATION_BASE_URL}/#/activate/{activation_token}"
    subject = "Activate your Portfolios for Weirdos account"
    body = (
        f"Hi {full_name},\n\n"
        "Thanks for signing up for Portfolios for Weirdos.\n"
        "Please activate your account by visiting the link below:\n\n"
        f"{activation_url}\n\n"
        "If you did not create this account, you can ignore this email.\n\n"
        "Cheers,\n"
        "The Portfolios for Weirdos team"
    )
    return send_email(subject, recipient_email, body)
