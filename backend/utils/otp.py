# ============================================
# NyayaAI — OTP Utility
# Generates 6 digit OTP
# Sets expiry time — 10 minutes
# Verifies OTP against stored value
# ============================================

import random
import string
from datetime import datetime, timedelta


def generate_otp():
    # generates 6 digit numeric OTP
    return ''.join(random.choices(string.digits, k=6))


def get_otp_expiry():
    # OTP valid for 10 minutes from now
    return datetime.utcnow() + timedelta(minutes=10)


def verify_otp(stored_otp, stored_expiry, input_otp):
    # returns True if OTP matches and not expired
    if not stored_otp or not stored_expiry:
        return False
    if datetime.utcnow() > stored_expiry:
        return False
    return stored_otp == input_otp
