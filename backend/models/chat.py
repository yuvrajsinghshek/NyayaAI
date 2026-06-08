# ============================================
# NyayaAI — Chat Database Model
# Defines conversations table in PostgreSQL
# Each row = one message exchange
# Stores question, answer, category, source
# ============================================

from sqlalchemy import Column, String, Text, DateTime, Integer
from sqlalchemy.sql import func
from backend.database.db import Base
import uuid


def generate_uuid():
    # generates unique id for each message
    return str(uuid.uuid4())


class Conversation(Base):
    # table name in PostgreSQL
    __tablename__ = "conversations"

    # unique id for each message — auto generated
    id = Column(
        String,
        primary_key = True,
        default     = generate_uuid
    )

    # session id groups messages of one chat session
    # same user ke saare messages ek session_id share karte hain
    session_id = Column(String, nullable=False, index=True)

    # user ka question
    user_message = Column(Text, nullable=False)

    # bot ka answer
    bot_response = Column(Text, nullable=False)

    # category detected by RAG pipeline
    category = Column(String, nullable=True)

    # source PDF or FAQ name
    source = Column(String, nullable=True)

    # was answer found in knowledge base or out of scope
    answer_found = Column(String, nullable=True)

    # timestamp — automatically set when record created
    created_at = Column(
        DateTime,
        server_default = func.now(),
        nullable       = False
    )
