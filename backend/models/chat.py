# ============================================
# NyayaAI — Conversation Model
# Updated to include user_id
# Links each message to a user
# ============================================

from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from backend.database.db import Base
import uuid


def generate_uuid():
    return str(uuid.uuid4())


class Conversation(Base):
    __tablename__ = "conversations"

    id           = Column(String, primary_key=True, default=generate_uuid)
    user_id      = Column(String, ForeignKey("users.id"), nullable=True)
    session_id   = Column(String, nullable=False, index=True)
    user_message = Column(Text, nullable=False)
    bot_response = Column(Text, nullable=False)
    category     = Column(String, nullable=True)
    source       = Column(String, nullable=True)
    answer_found = Column(String, nullable=True)
    created_at   = Column(DateTime, server_default=func.now())

    # relationship with user
    user = relationship("User", back_populates="chats")
