# ============================================
# NyayaAI — Generator
# Takes retrieved chunks and user question
# Sends both to Groq LLM
# Returns formatted answer with source info
# Handles out of scope questions gracefully
# ============================================

from groq import Groq
from ai.config import GROQ_API_KEY, GROQ_MODEL
import logging

log = logging.getLogger(__name__)

# initialize Groq client once at module level
client = Groq(api_key=GROQ_API_KEY)

# shown when no relevant chunks found
OUT_OF_SCOPE_MESSAGE = """I don't have specific information about this topic in my knowledge base.

For cybercrime related help:
📞 Helpline: 1930
🌐 Portal: www.cybercrime.gov.in
📱 Follow: @cyberdost on social media"""

# exact greeting words only — no partial matching
# using set of complete words to avoid 
# matching "hi" inside words like "his", "this"
GREETINGS = {
    "hello", "hi", "hey", "hii", "helo",
    "namaste", "namaskar", "greetings",
    "good morning", "good evening",
    "good afternoon", "good night",
    "how are you", "whats up", "sup"
}


def is_greeting(text):
    # normalize text — lowercase and strip
    normalized = text.lower().strip()
    # remove punctuation for matching
    normalized = normalized.replace("?", "").replace("!", "").strip()
    # check exact match only — prevents partial matches
    return normalized in GREETINGS


def format_context(chunks):
    # combines retrieved chunks into single context string
    # each chunk separated clearly
    context_parts = []
    for i, chunk in enumerate(chunks):
        context_parts.append(
            f"[Source {i+1}: {chunk['source']}]\n"
            f"{chunk['text']}"
        )
    return "\n\n".join(context_parts)


def build_prompt(user_question, context, chat_history=""):
    # strict prompt — prevents hallucination
    # includes chat history for context awareness
    history_section = ""
    if chat_history:
        history_section = f"""
PREVIOUS CONVERSATION:
{chat_history}
"""

    return f"""You are NyayaAI, a cybercrime awareness assistant for Indian citizens.
Answer the user's question using ONLY the context provided below.
Use the previous conversation to understand follow-up questions.

STRICT RULES:
1. Only use information from the context below
2. Do NOT make up any information
3. If context does not have enough info — say so clearly
4. Keep answer clear — 3 to 5 sentences maximum
5. Do not say "according to the context" or "the document says"
6. Answer in a helpful and professional tone
7. If question refers to previous conversation use that context
{history_section}
CONTEXT:
{context}

USER QUESTION:
{user_question}

ANSWER:"""


def generate_answer(user_question, chunks, chat_history=""):
    # handle greetings directly — no RAG needed
    if is_greeting(user_question):
        return {
            "answer"  : "Hello! I am NyayaAI, your cybercrime awareness assistant. I can help you with information about digital arrest scams, banking fraud, illegal loan apps, how to report cybercrime, and much more. What would you like to know?",
            "source"  : None,
            "category": None,
            "found"   : True
        }

    # if no relevant chunks — return out of scope
    if not chunks:
        log.info(f"⚠️ No chunks found for: {user_question}")
        return {
            "answer"  : OUT_OF_SCOPE_MESSAGE,
            "source"  : None,
            "category": None,
            "found"   : False
        }

    # combine chunks into context
    context = format_context(chunks)

    # build prompt with context and chat history
    prompt = build_prompt(user_question, context, chat_history)

    # send to Groq
    response = client.chat.completions.create(
        model       = GROQ_MODEL,
        messages    = [
            {
                "role"   : "system",
                "content": "You are NyayaAI, a helpful cybercrime awareness assistant for Indian citizens."
            },
            {
                "role"   : "user",
                "content": prompt
            }
        ],
        temperature = 0.3,
        max_tokens  = 500
    )

    answer     = response.choices[0].message.content.strip()
    best_chunk = chunks[0]

    log.info(f"✅ Answer generated for: {user_question}")

    return {
        "answer"  : answer,
        "source"  : best_chunk["source"],
        "category": best_chunk["category"],
        "found"   : True
    }
