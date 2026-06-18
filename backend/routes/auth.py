from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database.db import get_db
from backend.models.user import User, UserInfo
from backend.schemas.user import (
    RegisterRequest,
    VerifyOTPRequest,
    UserInfoRequest,
    LoginRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    AuthResponse
)
from backend.utils.auth import (
    hash_password,
    verify_password,
    create_access_token
)
from backend.utils.otp import generate_otp, get_otp_expiry, verify_otp
import logging
from datetime import datetime, timedelta

log    = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=AuthResponse)
def register(request: RegisterRequest,
             db: Session = Depends(get_db)):

    existing = db.query(User)\
        .filter(User.email == request.email).first()

    if existing and existing.is_verified:
        raise HTTPException(
            status_code = 400,
            detail      = "Email already registered"
        )

    otp    = generate_otp()
    expiry = get_otp_expiry()

    if existing and not existing.is_verified:
        existing.otp        = otp
        existing.otp_expiry = expiry
        existing.password   = hash_password(request.password)
        db.commit()
        return AuthResponse(message="OTP sent", otp=otp)

    user = User(
        email       = request.email,
        password    = hash_password(request.password),
        is_verified = False,
        otp         = otp,
        otp_expiry  = expiry
    )
    db.add(user)
    db.commit()

    return AuthResponse(message="OTP sent", otp=otp)


@router.post("/verify-otp", response_model=AuthResponse)
def verify_email_otp(request: VerifyOTPRequest,
                     db: Session = Depends(get_db)):

    user = db.query(User)\
        .filter(User.email == request.email).first()

    if not user:
        raise HTTPException(
            status_code = 404,
            detail      = "User not found"
        )

    if not verify_otp(user.otp, user.otp_expiry, request.otp):
        raise HTTPException(
            status_code = 400,
            detail      = "Invalid or expired OTP"
        )

    user.is_verified = True
    user.otp         = None
    user.otp_expiry  = None
    db.commit()

    return AuthResponse(
        message = "Email verified! Please fill your info."
    )


@router.post("/user-info", response_model=AuthResponse)
def save_user_info(request: UserInfoRequest,
                   db: Session = Depends(get_db)):

    user = db.query(User)\
        .filter(User.email == request.email,
                User.is_verified == True).first()

    if not user:
        raise HTTPException(
            status_code = 404,
            detail      = "User not found or not verified"
        )

    existing_info = db.query(UserInfo)\
        .filter(UserInfo.user_id == user.id).first()

    if existing_info:
        existing_info.name  = request.name
        existing_info.age   = request.age
        existing_info.city  = request.city
        existing_info.state = request.state
    else:
        info = UserInfo(
            user_id = user.id,
            name    = request.name,
            age     = request.age,
            city    = request.city,
            state   = request.state
        )
        db.add(info)

    db.commit()

    token = create_access_token({"user_id": user.id})

    return AuthResponse(
        message      = "Registration complete!",
        access_token = token,
        user_id      = user.id,
        name         = request.name
    )


@router.post("/login", response_model=AuthResponse)
def login(request: LoginRequest,
          db: Session = Depends(get_db)):

    user = db.query(User)\
        .filter(User.email == request.email).first()

    if not user:
        raise HTTPException(
            status_code = 400,
            detail      = "Invalid email or password"
        )

    if not user.is_verified:
        raise HTTPException(
            status_code = 400,
            detail      = "Please verify your email first"
        )

    if not verify_password(request.password, user.password):
        raise HTTPException(
            status_code = 400,
            detail      = "Invalid email or password"
        )

    name  = user.info.name if user.info else "User"
    token = create_access_token({"user_id": user.id})

    return AuthResponse(
        message      = f"Welcome back, {name}!",
        access_token = token,
        user_id      = user.id,
        name         = name
    )


@router.post("/forgot-password", response_model=AuthResponse)
def forgot_password(request: ForgotPasswordRequest,
                    db: Session = Depends(get_db)):

    user = db.query(User)\
        .filter(User.email == request.email).first()

    otp = ""
    if user:
        otp    = generate_otp()
        expiry = get_otp_expiry()

        user.otp        = otp
        user.otp_expiry = expiry
        db.commit()

    return AuthResponse(message="OTP sent", otp=otp)


@router.post("/reset-password", response_model=AuthResponse)
def reset_password(request: ResetPasswordRequest,
                   db: Session = Depends(get_db)):

    user = db.query(User)\
        .filter(User.email == request.email).first()

    if not user:
        raise HTTPException(
            status_code = 404,
            detail      = "User not found"
        )

    if not verify_otp(user.otp, user.otp_expiry, request.otp):
        raise HTTPException(
            status_code = 400,
            detail      = "Invalid or expired OTP"
        )

    user.password   = hash_password(request.new_password)
    user.otp        = None
    user.otp_expiry = None
    db.commit()

    return AuthResponse(message="Password reset successfully!")
