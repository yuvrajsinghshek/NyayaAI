from groq import Groq
from ai.config import GROQ_API_KEY, GROQ_MODEL
import logging

log = logging.getLogger(__name__)

client = Groq(api_key=GROQ_API_KEY)

GREETINGS = {
    "hello", "hi", "hey", "hii", "helo",
    "namaste", "namaskar", "greetings",
    "good morning", "good evening",
    "good afternoon", "good night",
    "how are you", "whats up", "sup"
}


def is_greeting(text):
    normalized = text.lower().strip()
    normalized = normalized.replace("?", "").replace("!", "").strip()
    return normalized in GREETINGS


def format_context(chunks):
    context_parts = []
    for i, chunk in enumerate(chunks):
        context_parts.append(
            f"[Source {i+1}: {chunk['source']}]\n"
            f"{chunk['text']}"
        )
    return "\n\n".join(context_parts)


def detect_language(text):
    hindi_chars = sum(1 for c in text if '\u0900' <= c <= '\u097F')
    total_chars = len(text.replace(" ", ""))

    if total_chars == 0:
        return "english"

    hindi_ratio = hindi_chars / total_chars
    words         = text.lower().split()
    english_words = [w for w in words if w.isascii()]

    if hindi_ratio > 0.3:
        return "hindi"
    elif hindi_ratio > 0 and len(english_words) > 0:
        return "hinglish"
    else:
        hinglish_words = [
            "kya", "hai", "mujhe", "aap", "yeh", "toh",
            "bata", "karo", "mere", "iske", "uske", "wala",
            "nahi", "haan", "theek", "accha", "matlab",
            "kyun", "kaise", "kaun", "kab", "kahan"
        ]
        if any(w in words for w in hinglish_words):
            return "hinglish"
        return "english"


def build_prompt(user_question, context, chat_history=""):
    history_section = ""
    if chat_history:
        history_section = f"""
PREVIOUS CONVERSATION:
{chat_history}
"""
    lang = detect_language(user_question)

    if lang == "hindi":
        lang_instruction = "RESPOND IN HINDI ONLY using Devanagari script."
    elif lang == "hinglish":
        lang_instruction = "RESPOND IN HINGLISH ONLY — mix Hindi and English words in Roman script like the user."
    else:
        lang_instruction = "RESPOND IN ENGLISH ONLY. Do not use any Hindi words."

    return f"""You are NyayaAI, a cybercrime and road safety awareness assistant for Indian citizens.
Answer ONLY using the context provided below.
Use previous conversation to understand follow-up questions.

LANGUAGE RULE — MANDATORY:
{lang_instruction}

STRICT RULES:
1. ONLY use information from the context below.
2. ONLY answer questions related to cybercrime, road safety, and traffic rules. Do NOT answer anything else.
3. Do NOT make up any information.
4. If context does not have enough info — say you don't have information and suggest visiting cybercrime.gov.in or morth.nic.in.
5. Format your answers clearly using bullet points to make them helpful and easy to read.
6. Keep answer clear and concise.
7. Do not say "according to the context".
8. Use previous conversation for follow-up questions.
{history_section}
CONTEXT:
{context}

USER QUESTION:
{user_question}

ANSWER:"""


def generate_answer(user_question, chunks,
                    chat_history="", user_name=None):

    # handle greetings dynamically via LLM
    if is_greeting(user_question):
        user_context = f"The user's name is {user_name}." if user_name else "You don't know the user's name yet."
        sys_prompt = f"You are NyayaAI, a friendly legal assistant for Indian citizens. {user_context} The user is greeting you. Respond politely and naturally like a chatbot. Keep it short (1-2 sentences). Ask how you can help them with Cybercrime or Road Safety today."
        
        greeting_resp = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": user_question}
            ],
            temperature=0.6,
            max_tokens=150
        )
        return {
            "answer"  : greeting_resp.choices[0].message.content.strip(),
            "source"  : "NyayaAI System",
            "category": "Greeting",
            "found"   : True
        }

    # no chunks found — out of scope
    if not chunks:
        return {
            "answer"  : "I don't have specific information about this topic in my knowledge base. I only answer questions related to Cybercrime and Road Safety/Traffic Rules.\n\nHere are some helpful resources:\n\n🔐 **Cybercrime:**\n📞 Helpline: 1930\n🌐 www.cybercrime.gov.in\n📱 @cyberdost\n\n🚦 **Road Safety & Traffic:**\n📞 Emergency: 112\n🌐 www.morth.nic.in",
            "source"  : None,
            "category": None,
            "found"   : False
        }

    context = format_context(chunks)
    prompt  = build_prompt(user_question, context, chat_history)

    response = client.chat.completions.create(
        model       = GROQ_MODEL,
        messages    = [
            {
                "role"   : "system",
                "content": "You are NyayaAI, a cybercrime and road safety awareness assistant for Indian citizens. Only answer questions related to cybercrime and road safety/traffic rules."
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

    return {
        "answer"  : answer,
        "source"  : best_chunk["source"],
        "category": best_chunk["category"],
        "found"   : True
    }
