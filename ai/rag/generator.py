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

# shown when no relevant chunks found in knowledge base
OUT_OF_SCOPE_MESSAGE = """I don't have specific information about this topic in my knowledge base.

For cybercrime related help:
📞 Helpline: 1930
🌐 Portal: www.cybercrime.gov.in
📱 Follow: @cyberdost on social media"""


def format_context(chunks):
    # combines all retrieved chunks into single context string
    # each chunk separated clearly so LLM can distinguish
    context_parts = []

    for i, chunk in enumerate(chunks):
        context_parts.append(
            f"[Source {i+1}: {chunk['source']}]\n"
            f"{chunk['text']}"
        )

    return "\n\n".join(context_parts)


def build_prompt(user_question, context):
    # strict prompt — prevents hallucination
    # tells Groq to only use provided context
    return f"""You are NyayaAI, a cybercrime awareness assistant for Indian citizens.
Answer the user's question using ONLY the context provided below.

STRICT RULES:
1. Only use information from the context below
2. Do NOT make up any information
3. If context does not have enough information — say so clearly
4. Keep answer clear and concise — 3 to 5 sentences maximum
5. Do not use phrases like "according to the context" or "the document says"
6. Answer in a helpful and professional tone

CONTEXT:
{context}

USER QUESTION:
{user_question}

ANSWER:"""


def generate_answer(user_question, chunks):

    # check if question is a greeting or simple conversation
    # handle these directly without searching knowledge base
    greetings = [
        "hello", "hi", "hey", "namaste", "hii", "helo",
        "good morning", "good evening", "good afternoon",
        "how are you", "what's up", "sup", "greetings"
    ]

    # if question is a greeting — respond friendly
    if any(g in user_question.lower() for g in greetings):
        return {
            "answer"  : "Hello! I am NyayaAI, your cybercrime awareness assistant. I can help you with information about digital arrest scams, banking fraud, illegal loan apps, how to report cybercrime, and much more. What would you like to know?",
            "source"  : None,
            "category": None,
            "found"   : True
        }

    # if no relevant chunks found — return out of scope message
    if not chunks:
        log.info("⚠️ No chunks — returning out of scope message")
        return {
            "answer"  : OUT_OF_SCOPE_MESSAGE,
            "source"  : None,
            "category": None,
            "found"   : False
        }

    # combine chunks into context for LLM
    context = format_context(chunks)

    # build strict prompt with context and question
    prompt = build_prompt(user_question, context)

    # send to Groq and get response
    response = client.chat.completions.create(
        model       = GROQ_MODEL,
        messages    = [
            {
                "role"   : "system",
                "content": "You are NyayaAI, a helpful cybercrime awareness assistant."
            },
            {
                "role"   : "user",
                "content": prompt
            }
        ],
        temperature = 0.3,
        max_tokens  = 500
    )

    # extract answer text from Groq response
    answer = response.choices[0].message.content.strip()

    # use metadata from most relevant chunk for display
    best_chunk = chunks[0]

    log.info(f"✅ Answer generated for: {user_question}")

    return {
        "answer"  : answer,
        "source"  : best_chunk["source"],
        "category": best_chunk["category"],
        "found"   : True
    }
