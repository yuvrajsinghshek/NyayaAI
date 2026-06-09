# ============================================
# NyayaAI — User Models
# 3 tables:
# 1. users       — login credentials
# 2. user_info   — name age city state
# 3. chat_summary — chat wise summary
# ============================================

from sqlalchemy import (
    Column, String, Integer,
    DateTime, Boolean, Text, ForeignKey
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from backend.database.db import Base
import uuid


def generate_uuid():
    return str(uuid.uuid4())


class User(Base):
    # table 1 — login credentials
    __tablename__ = "users"

    id         = Column(String, primary_key=True, default=generate_uuid)
    email      = Column(String, unique=True, nullable=False, index=True)
    password   = Column(String, nullable=False)  # hashed password
    is_verified = Column(Boolean, default=False)  # email verified?
    otp        = Column(String, nullable=True)    # current OTP
    otp_expiry = Column(DateTime, nullable=True)  # OTP expiry time
    created_at = Column(DateTime, server_default=func.now())

    # relationship with user_info
    info    = relationship("UserInfo", back_populates="user", uselist=False)
    # relationship with conversations
    chats   = relationship("Conversation", back_populates="user")
    # relationship with chat summaries
    summaries = relationship("ChatSummary", back_populates="user")


class UserInfo(Base):
    # table 2 — basic user info
    # chatbot uses this to personalize responses
    __tablename__ = "user_info"

    id       = Column(String, primary_key=True, default=generate_uuid)
    user_id  = Column(String, ForeignKey("users.id"), nullable=False)
    name     = Column(String, nullable=False)
    age      = Column(Integer, nullable=True)
    city     = Column(String, nullable=True)
    state    = Column(String, nullable=True)

    user = relationship("User", back_populates="info")


class ChatSummary(Base):
    # table 3 — chat wise summary
    # 3-4 line summary of each chat session
    __tablename__ = "chat_summary"

    id         = Column(String, primary_key=True, default=generate_uuid)
    user_id    = Column(String, ForeignKey("users.id"), nullable=False)
    session_id = Column(String, nullable=False, index=True)
    summary    = Column(Text, nullable=True)   # 3-4 line summary
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    user = relationship("User", back_populates="summaries")
