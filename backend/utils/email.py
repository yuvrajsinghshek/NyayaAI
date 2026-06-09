# ============================================
# NyayaAI — Email Utility
# Sends OTP email using Gmail SMTP
# Used for registration and forgot password
# ============================================

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from ai.config import (
    MAIL_USERNAME,
    MAIL_PASSWORD,
    MAIL_FROM,
    MAIL_SERVER,
    MAIL_PORT
)
import logging

log = logging.getLogger(__name__)


def send_otp_email(to_email, otp, purpose="registration"):
    # purpose = registration or reset_password
    if purpose == "registration":
        subject = "NyayaAI — Email Verification OTP"
        body    = f"""
Hello!

Welcome to NyayaAI — Your Cybercrime Awareness Assistant.

Your OTP for email verification is:

{otp}

This OTP is valid for 10 minutes only.
Do not share this OTP with anyone.

Stay safe online!
Team NyayaAI
"""
    else:
        subject = "NyayaAI — Password Reset OTP"
        body    = f"""
Hello!

We received a request to reset your NyayaAI password.

Your OTP for password reset is:

{otp}

This OTP is valid for 10 minutes only.
If you did not request this, please ignore this email.

Stay safe online!
Team NyayaAI
"""

    try:
        # create email message
        msg = MIMEMultipart()
        msg['From']    = MAIL_FROM
        msg['To']      = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        # connect to Gmail SMTP and send
        server = smtplib.SMTP(MAIL_SERVER, MAIL_PORT)
        server.starttls()
        server.login(MAIL_USERNAME, MAIL_PASSWORD)
        server.sendmail(MAIL_FROM, to_email, msg.as_string())
        server.quit()

        log.info(f"✅ OTP email sent to {to_email}")
        return True

    except Exception as e:
        log.error(f"❌ Email send failed: {e}")
        return False
