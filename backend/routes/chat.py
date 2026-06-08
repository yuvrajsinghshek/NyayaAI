from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database.db import get_db
from backend.models.chat import Conversation
from backend.schemas.chat import (
    ChatRequest,
    ChatResponse,
    HistoryResponse,
    ConversationHistory
)
from ai.rag.retriever import retrieve_chunks
from ai.rag.generator import generate_answer
import logging

log = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/", response_model=ChatResponse)
def chat(request: ChatRequest, db: Session = Depends(get_db)):

    # fetch last 3 messages for context
    history = db.query(Conversation)\
        .filter(Conversation.session_id == request.session_id)\
        .order_by(Conversation.created_at.desc())\
        .limit(3)\
        .all()

    # build chat history string for generator
    chat_history = ""
    if history:
        history_reversed = list(reversed(history))
        for h in history_reversed:
            chat_history += f"User: {h.user_message}\n"
            chat_history += f"Assistant: {h.bot_response}\n"

    # enrich query with context for retriever
    enriched_query = request.message
    if chat_history:
        enriched_query = (
            f"Previous context:\n{chat_history}\n"
            f"Current question: {request.message}"
        )

    # retrieve chunks using enriched query
    chunks = retrieve_chunks(enriched_query)

    # generate answer with chat history for context
    result = generate_answer(
        request.message,
        chunks,
        chat_history
    )

    # save to PostgreSQL
    conversation = Conversation(
        session_id   = request.session_id,
        user_message = request.message,
        bot_response = result["answer"],
        category     = result.get("category"),
        source       = result.get("source"),
        answer_found = str(result.get("found", False))
    )
    db.add(conversation)
    db.commit()

    return ChatResponse(
        session_id = request.session_id,
        answer     = result["answer"],
        category   = result.get("category"),
        source     = result.get("source"),
        found      = result.get("found", False)
    )


@router.get("/history/{session_id}",
            response_model=HistoryResponse)
def get_history(session_id: str,
                db: Session = Depends(get_db)):
    conversations = db.query(Conversation)\
        .filter(Conversation.session_id == session_id)\
        .order_by(Conversation.created_at.asc())\
        .all()

    return HistoryResponse(
        session_id    = session_id,
        conversations = conversations
    )


@router.delete("/history/{session_id}")
def clear_history(session_id: str,
                  db: Session = Depends(get_db)):
    db.query(Conversation)\
        .filter(Conversation.session_id == session_id)\
        .delete()
    db.commit()
    return {"message": f"History cleared for {session_id}"}
