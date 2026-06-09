# ============================================
# NyayaAI — Auth Routes
# POST /auth/register     — register new user
# POST /auth/verify-otp   — verify email OTP
# POST /auth/user-info    — save basic info
# POST /auth/login        — login user
# POST /auth/forgot-password — send reset OTP
# POST /auth/reset-password  — reset password
# ============================================

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
from backend.utils.otp import (
    generate_otp,
    get_otp_expiry,
    verify_otp
)
from backend.utils.email import send_otp_email
import logging

log    = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=AuthResponse)
def register(request: RegisterRequest,
             db: Session = Depends(get_db)):
    # check if email already registered
    existing = db.query(User)\
        .filter(User.email == request.email).first()
    if existing:
        raise HTTPException(
            status_code = 400,
            detail      = "Email already registered"
        )

    # generate OTP and send email
    otp    = generate_otp()
    expiry = get_otp_expiry()

    # create new user — not verified yet
    user = User(
        email      = request.email,
        password   = hash_password(request.password),
        is_verified = False,
        otp        = otp,
        otp_expiry = expiry
    )
    db.add(user)
    db.commit()

    # send OTP email
    send_otp_email(request.email, otp, "registration")

    return AuthResponse(
        message = "OTP sent to your email. Please verify."
    )


@router.post("/verify-otp", response_model=AuthResponse)
def verify_email_otp(request: VerifyOTPRequest,
                     db: Session = Depends(get_db)):
    # find user by email
    user = db.query(User)\
        .filter(User.email == request.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # verify OTP
    if not verify_otp(user.otp, user.otp_expiry, request.otp):
        raise HTTPException(
            status_code = 400,
            detail      = "Invalid or expired OTP"
        )

    # mark user as verified
    user.is_verified = True
    user.otp         = None
    user.otp_expiry  = None
    db.commit()

    return AuthResponse(
        message = "Email verified successfully. Please fill your info."
    )


@router.post("/user-info", response_model=AuthResponse)
def save_user_info(request: UserInfoRequest,
                   db: Session = Depends(get_db)):
    # find verified user
    user = db.query(User)\
        .filter(User.email == request.email,
                User.is_verified == True).first()
    if not user:
        raise HTTPException(
            status_code = 404,
            detail      = "User not found or not verified"
        )

    # save user info
    info = UserInfo(
        user_id = user.id,
        name    = request.name,
        age     = request.age,
        city    = request.city,
        state   = request.state
    )
    db.add(info)
    db.commit()

    # create JWT token
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
    # find user
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

    # get user name from info table
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

    # always return success — security best practice
    # dont reveal if email exists or not
    if user:
        otp    = generate_otp()
        expiry = get_otp_expiry()

        user.otp        = otp
        user.otp_expiry = expiry
        db.commit()

        send_otp_email(request.email, otp, "reset_password")

    return AuthResponse(
        message = "If email exists, OTP has been sent."
    )


@router.post("/reset-password", response_model=AuthResponse)
def reset_password(request: ResetPasswordRequest,
                   db: Session = Depends(get_db)):
    user = db.query(User)\
        .filter(User.email == request.email).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not verify_otp(user.otp, user.otp_expiry, request.otp):
        raise HTTPException(
            status_code = 400,
            detail      = "Invalid or expired OTP"
        )

    # update password
    user.password   = hash_password(request.new_password)
    user.otp        = None
    user.otp_expiry = None
    db.commit()

    return AuthResponse(message = "Password reset successfully!")
