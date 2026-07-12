import smtplib
from email.message import EmailMessage

from config import Config


def send_email(subject, recipient, text_body, html_body=None):
    if not Config.SMTP_HOST or not Config.SMTP_FROM:
        print(f"[EMAIL] {subject} -> {recipient}\n{text_body}")
        return False

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = Config.SMTP_FROM
    message["To"] = recipient
    message.set_content(text_body)

    if html_body:
        message.add_alternative(html_body, subtype="html")

    try:
        if Config.SMTP_USE_SSL:
            server = smtplib.SMTP_SSL(Config.SMTP_HOST, Config.SMTP_PORT)
        else:
            server = smtplib.SMTP(Config.SMTP_HOST, Config.SMTP_PORT)
            server.ehlo()
            if Config.SMTP_STARTTLS:
                server.starttls()
                server.ehlo()

        if Config.SMTP_USER and Config.SMTP_PASSWORD:
            server.login(Config.SMTP_USER, Config.SMTP_PASSWORD)

        server.send_message(message)
        server.quit()
        return True
    except Exception as exc:
        print(f"[EMAIL ERROR] {exc}")
        return False


def send_activation_email(recipient_email, full_name, activation_code):
    activation_page = f"{Config.ACTIVATION_BASE_URL}/#/activate"
    subject = "Your Portfolios for Weirdos activation code"
    text_body = (
        f"Hi {full_name},\n\n"
        "Thanks for signing up for Portfolios for Weirdos.\n"
        "Use the one-time activation code below to verify your account:\n\n"
        f"{activation_code}\n\n"
        f"Open this page to enter the code: {activation_page}\n\n"
        "If you did not create this account, you can ignore this email.\n\n"
        "Cheers,\n"
        "The Portfolios for Weirdos team"
    )
    html_body = f"""
        <html>
          <body style="font-family:Arial,Helvetica,sans-serif;color:#e5e7eb;background:#111318;padding:24px;">
            <div style="max-width:600px;margin:0 auto;background:#171b22;border:1px solid rgba(148,163,184,0.14);border-radius:18px;padding:28px;">
              <h2 style="margin-top:0;color:#f8fafc;">Activate your Portfolios for Weirdos account</h2>
              <p style="color:#cbd5e1;">Hello {full_name},</p>
              <p style="color:#cbd5e1;line-height:1.6;">Thanks for signing up. Use the one-time code below to activate your account:</p>
              <div style="font-size:24px;font-weight:700;color:#0f172a;background:#e2e8f0;padding:18px 24px;border-radius:16px;text-align:center;margin:24px 0;">
                {activation_code}
              </div>
              <p style="color:#cbd5e1;line-height:1.6;">Open this page and enter the code to activate your account:<br><a href="{activation_page}" style="color:#67e8f9;word-break:break-all;">{activation_page}</a></p>
              <p style="color:#94a3b8;line-height:1.6;">If you did not request this, no action is needed.</p>
              <p style="margin-top:32px;color:#cbd5e1;">Cheers,<br>The Portfolios for Weirdos team</p>
            </div>
          </body>
        </html>
    """
    return send_email(subject, recipient_email, text_body, html_body)
