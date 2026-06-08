# ============================================
# NyayaAI — Chat Routes
# FastAPI endpoints for chat functionality
# POST /chat     — send message get answer
# GET  /history  — get chat history
# DELETE /history — clear chat history
# ============================================

from fastapi import APIRouter, Depends, HTTPException
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

# APIRouter groups related endpoints together
router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/", response_model=ChatResponse)
def chat(request: ChatRequest, db: Session = Depends(get_db)):
    # main chat endpoint
    # receives user message and session_id
    # fetches last 3 messages for context
    # runs RAG pipeline
    # saves to database
    # returns answer

    # fetch last 3 messages of this session for context
    # used to understand follow up questions
    history = db.query(Conversation)\
        .filter(Conversation.session_id == request.session_id)\
        .order_by(Conversation.created_at.desc())\
        .limit(3)\
        .all()

    # build context string from chat history
    # helps RAG understand follow up questions
    chat_context = ""
    if history:
        history_reversed = list(reversed(history))
        for h in history_reversed:
            chat_context += f"User: {h.user_message}\n"
            chat_context += f"Assistant: {h.bot_response}\n"

    # combine chat history with current question
    # this helps retriever find relevant chunks
    # even for vague follow up questions
    enriched_query = request.message
    if chat_context:
        enriched_query = (
            f"Previous conversation:\n{chat_context}\n"
            f"Current question: {request.message}"
        )

    # retrieve relevant chunks from ChromaDB
    chunks = retrieve_chunks(enriched_query)

    # generate answer using Groq
    result = generate_answer(request.message, chunks)

    # save conversation to PostgreSQL
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

    log.info(f"✅ Chat saved — session: {request.session_id}")

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
    # returns full chat history for a session
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
    # deletes all messages of a session
    db.query(Conversation)\
        .filter(Conversation.session_id == session_id)\
        .delete()
    db.commit()

    return {"message": f"History cleared for {session_id}"}
