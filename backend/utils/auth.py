# ============================================
# NyayaAI — Auth Utility
# Password hashing and verification
# JWT token generation and verification
# ============================================

from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from ai.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
import logging

log = logging.getLogger(__name__)

# bcrypt context for password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password):
    # converts plain password to hashed version
    # stored in database — never store plain password
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    # verifies plain password against stored hash
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data):
    # creates JWT token with user data
    # token expires after configured minutes
    to_encode = data.copy()
    expire    = datetime.utcnow() + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token):
    # decodes JWT token and returns user data
    # returns None if token invalid or expired
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
