from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database.db import get_db
from backend.models.chat import Conversation
from backend.models.user import UserInfo, ChatSummary
from backend.schemas.chat import (
    ChatRequest,
    ChatResponse,
    HistoryResponse,
    ConversationHistory
)
from ai.rag.retriever import retrieve_chunks
from ai.rag.generator import generate_answer
from groq import Groq
from ai.config import GROQ_API_KEY, GROQ_MODEL
import logging

log    = logging.getLogger(__name__)
router = APIRouter(prefix="/chat", tags=["chat"])
client = Groq(api_key=GROQ_API_KEY)


def generate_chat_summary(conversations):
    # generates 3-4 line summary of entire chat
    # called when user opens new chat or closes session

    if not conversations:
        return None

    # build conversation text for summarization
    chat_text = ""
    for conv in conversations:
        chat_text += f"User: {conv.user_message}\n"
        chat_text += f"Assistant: {conv.bot_response}\n\n"

    try:
        response = client.chat.completions.create(
            model    = GROQ_MODEL,
            messages = [
                {
                    "role"   : "system",
                    "content": "You are a helpful assistant that summarizes conversations."
                },
                {
                    "role"   : "user",
                    "content": f"""Summarize this cybercrime awareness chat in 3-4 lines.
Focus on: what topics were discussed, what help was provided.
Keep it concise and informative.

CONVERSATION:
{chat_text}

SUMMARY:"""
                }
            ],
            temperature = 0.3,
            max_tokens  = 150
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        log.error(f"Summary generation failed: {e}")
        return None


@router.post("/", response_model=ChatResponse)
def chat(request: ChatRequest, db: Session = Depends(get_db)):

    # get user name for personalization
    user_name = None
    if request.user_id:
        user_info = db.query(UserInfo)\
            .filter(UserInfo.user_id == request.user_id)\
            .first()
        if user_info:
            user_name = user_info.name

    # fetch last 3 messages for context
    history = db.query(Conversation)\
        .filter(Conversation.session_id == request.session_id)\
        .order_by(Conversation.created_at.desc())\
        .limit(3)\
        .all()

    # build chat history string
    chat_history = ""
    if history:
        history_reversed = list(reversed(history))
        for h in history_reversed:
            chat_history += f"User: {h.user_message}\n"
            chat_history += f"Assistant: {h.bot_response}\n"

    # enrich query with context
    enriched_query = request.message
    if chat_history:
        enriched_query = (
            f"Previous context:\n{chat_history}\n"
            f"Current question: {request.message}"
        )

    # retrieve and generate
    try:
        chunks = retrieve_chunks(enriched_query)
    except Exception as e:
        log.error(f"ChromaDB error: {e}")
        chunks = []
    result = generate_answer(
        request.message,
        chunks,
        chat_history,
        user_name
    )

    # save conversation
    conversation = Conversation(
        session_id   = request.session_id,
        user_id      = request.user_id,
        user_message = request.message,
        bot_response = result["answer"],
        category     = result.get("category"),
        source       = result.get("source"),
        answer_found = str(result.get("found", False))
    )
    db.add(conversation)
    db.commit()

    log.info(f"Chat saved — session: {request.session_id}")

    return ChatResponse(
        session_id = request.session_id,
        answer     = result["answer"],
        category   = result.get("category"),
        source     = result.get("source"),
        found      = result.get("found", False)
    )


@router.post("/summary/{session_id}")
def save_summary(session_id: str,
                 user_id: str,
                 db: Session = Depends(get_db)):
    # generates and saves summary for a chat session
    # called when user opens new chat

    # check if summary already exists
    existing = db.query(ChatSummary)\
        .filter(ChatSummary.session_id == session_id)\
        .first()

    if existing:
        return {"message": "Summary already exists"}

    # get all conversations of this session
    conversations = db.query(Conversation)\
        .filter(Conversation.session_id == session_id)\
        .order_by(Conversation.created_at.asc())\
        .all()

    if not conversations:
        return {"message": "No conversations found"}

    # generate summary using Groq
    summary = generate_chat_summary(conversations)

    if summary:
        chat_summary = ChatSummary(
            user_id    = user_id,
            session_id = session_id,
            summary    = summary
        )
        db.add(chat_summary)
        db.commit()
        log.info(f"Summary saved for session: {session_id}")
        return {"message": "Summary saved", "summary": summary}

    return {"message": "Summary generation failed"}


@router.get("/summaries/{user_id}")
def get_summaries(user_id: str,
                  db: Session = Depends(get_db)):
    # returns all chat summaries for a user
    summaries = db.query(ChatSummary)\
        .filter(ChatSummary.user_id == user_id)\
        .order_by(ChatSummary.created_at.desc())\
        .all()

    return {
        "summaries": [
            {
                "session_id": s.session_id,
                "summary"   : s.summary,
                "created_at": str(s.created_at)
            }
            for s in summaries
        ]
    }


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
