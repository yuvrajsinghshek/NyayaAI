# ============================================
# NyayaAI — Chat Schemas
# Pydantic models for request and response
# FastAPI uses these for validation
# Defines exact format of API input/output
# ============================================

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ChatRequest(BaseModel):
    # what frontend sends to API
    session_id : str       # unique session identifier
    message    : str       # user ka question


class ChatResponse(BaseModel):
    # what API sends back to frontend
    session_id : str
    answer     : str
    category   : Optional[str] = None
    source     : Optional[str] = None
    found      : bool = True


class ConversationHistory(BaseModel):
    # single message in chat history
    user_message : str
    bot_response : str
    category     : Optional[str] = None
    source       : Optional[str] = None
    created_at   : datetime

    class Config:
        # allows SQLAlchemy model to be converted
        # to Pydantic model directly
        from_attributes = True


class HistoryResponse(BaseModel):
    # list of all messages in a session
    session_id    : str
    conversations : list[ConversationHistory]
