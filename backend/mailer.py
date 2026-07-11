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


def send_activation_email(recipient_email, full_name, activation_token):
    activation_url = f"{Config.ACTIVATION_BASE_URL}/#/activate/{activation_token}"
    subject = "Activate your Portfolios for Weirdos account"
    text_body = (
        f"Hi {full_name},\n\n"
        "Thanks for signing up for Portfolios for Weirdos.\n"
        "Please activate your account by clicking the link below:\n\n"
        f"{activation_url}\n\n"
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
              <p style="color:#cbd5e1;line-height:1.6;">Thanks for signing up. Click the button below to activate your account and start building your portfolio.</p>
              <div style="text-align:center;margin:28px 0;">
                <a href="{activation_url}" style="display:inline-block;padding:14px 24px;background:#6ee7b7;color:#0f172a;border-radius:999px;font-weight:800;text-decoration:none;">Activate account</a>
              </div>
              <p style="color:#94a3b8;line-height:1.6;">If the button does not work, copy and paste this link into your browser:<br><a href="{activation_url}" style="color:#67e8f9;word-break:break-all;">{activation_url}</a></p>
              <p style="color:#94a3b8;line-height:1.6;">If you did not request this, no action is needed.</p>
              <p style="margin-top:32px;color:#cbd5e1;">Cheers,<br>The Portfolios for Weirdos team</p>
            </div>
          </body>
        </html>
    """
    return send_email(subject, recipient_email, text_body, html_body)
