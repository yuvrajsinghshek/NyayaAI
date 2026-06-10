# ============================================
# NyayaAI — Auth Utility
# Password hashing using werkzeug
# JWT token generation and verification
# ============================================

from werkzeug.security import generate_password_hash, check_password_hash
from jose import JWTError, jwt
from datetime import datetime, timedelta
from ai.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
import logging

log = logging.getLogger(__name__)


def hash_password(password):
    # converts plain password to hashed version
    # using werkzeug — compatible with Python 3.14
    return generate_password_hash(password)


def verify_password(plain_password, hashed_password):
    # verifies plain password against stored hash
    return check_password_hash(hashed_password, plain_password)


def create_access_token(data):
    # creates JWT token with user data
    to_encode = data.copy()
    expire    = datetime.utcnow() + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token):
    # decodes JWT token and returns user data
    try:
        payload = jwt.decode(
            token, SECRET_KEY, algorithms=[ALGORITHM]
        )
        return payload
    except JWTError:
        return None
