# ============================================
# NyayaAI — User Schemas
# Pydantic models for all auth endpoints
# Defines exact format of API input/output
# ============================================

from pydantic import BaseModel, EmailStr
from typing import Optional


class RegisterRequest(BaseModel):
    # step 1 — basic registration
    email    : EmailStr
    password : str


class VerifyOTPRequest(BaseModel):
    # step 2 — verify email OTP
    email : EmailStr
    otp   : str


class UserInfoRequest(BaseModel):
    # step 3 — fill basic info after verification
    email : EmailStr
    name  : str
    age   : Optional[int] = None
    city  : Optional[str] = None
    state : Optional[str] = None


class LoginRequest(BaseModel):
    email    : EmailStr
    password : str


class ForgotPasswordRequest(BaseModel):
    email : EmailStr


class ResetPasswordRequest(BaseModel):
    email        : EmailStr
    otp          : str
    new_password : str


class AuthResponse(BaseModel):
    message      : str
    otp          : Optional[str] = None
    access_token : Optional[str] = None
    user_id      : Optional[str] = None
    name         : Optional[str] = None
