import smtplib
import logging
import threading
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from ai.config import (
    MAIL_USERNAME, MAIL_PASSWORD,
    MAIL_FROM, MAIL_SERVER, MAIL_PORT
)

log = logging.getLogger(__name__)


def send_email_background(to_email, subject, body):
    # runs in background thread — non blocking
    def _send():
        try:
            msg = MIMEMultipart()
            msg["From"]    = MAIL_FROM
            msg["To"]      = to_email
            msg["Subject"] = subject
            msg.attach(MIMEText(body, "html"))

            server = smtplib.SMTP(MAIL_SERVER, int(MAIL_PORT))
            server.starttls()
            server.login(MAIL_USERNAME, MAIL_PASSWORD)
            server.sendmail(MAIL_FROM, to_email, msg.as_string())
            server.quit()
            log.info(f"✅ OTP email sent to {to_email}")
        except Exception as e:
            log.error(f"❌ Email failed: {e}")

    thread = threading.Thread(target=_send)
    thread.daemon = True
    thread.start()


def send_otp_email(to_email, otp):
    subject = "NyayaAI — Your OTP Code"
    body    = f"""
    <html><body>
    <h2>⚖️ NyayaAI — OTP Verification</h2>
    <p>Your OTP code is:</p>
    <h1 style="color:#4CAF50; letter-spacing:5px">{otp}</h1>
    <p>This OTP is valid for <b>10 minutes</b>.</p>
    <p>If you did not request this, please ignore.</p>
    </body></html>
    """
    send_email_background(to_email, subject, body)
