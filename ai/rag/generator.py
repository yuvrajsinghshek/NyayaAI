from groq import Groq
from ai.config import GROQ_API_KEY, GROQ_MODEL
import logging

log = logging.getLogger(__name__)

client = Groq(api_key=GROQ_API_KEY)

OUT_OF_SCOPE_MESSAGE = """I don't have specific information about this topic in my knowledge base.

For cybercrime related help:
📞 Helpline: 1930
🌐 Portal: www.cybercrime.gov.in
📱 Follow: @cyberdost on social media"""

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
    # detect if text is english, hindi or hinglish
    # count hindi unicode characters
    hindi_chars = sum(1 for c in text if '\u0900' <= c <= '\u097F')
    total_chars = len(text.replace(" ", ""))
    
    if total_chars == 0:
        return "english"
    
    hindi_ratio = hindi_chars / total_chars
    
    # check if mixed english and hindi words
    words         = text.lower().split()
    english_words = [w for w in words if w.isascii()]
    
    if hindi_ratio > 0.3:
        # mostly hindi script
        return "hindi"
    elif hindi_ratio > 0 and len(english_words) > 0:
        # mix of hindi and english
        return "hinglish"
    else:
        # all english/roman script
        # check for hinglish by common hindi words in roman
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
    # detect language for strict instruction
    lang = detect_language(user_question)
    
    if lang == "hindi":
        lang_instruction = "RESPOND IN HINDI ONLY using Devanagari script."
    elif lang == "hinglish":
        lang_instruction = "RESPOND IN HINGLISH ONLY — mix Hindi and English words in Roman script like the user."
    else:
        lang_instruction = "RESPOND IN ENGLISH ONLY. Do not use any Hindi words."

    return f"""You are NyayaAI, a cybercrime awareness assistant for Indian citizens.
Answer the user question using ONLY the context provided below.
Use previous conversation to understand follow-up questions.

LANGUAGE RULE — THIS IS MANDATORY:
{lang_instruction}

STRICT RULES:
1. Only use information from the context below
2. Do NOT make up any information
3. If context does not have enough info say so clearly
4. Keep answer clear — 3 to 5 sentences maximum
5. Do not say according to the context or the document says
6. Use previous conversation for follow-up questions
{history_section}
CONTEXT:
{context}

USER QUESTION:
{user_question}

ANSWER:"""


def generate_answer(user_question, chunks, 
                    chat_history="", user_name=None):
    # handle greetings — use name only for greetings
    if is_greeting(user_question):
        if user_name:
            greeting = f"Hello, {user_name}! I am NyayaAI, your cybercrime awareness assistant. I can help you with information about digital arrest scams, banking fraud, illegal loan apps, how to report cybercrime, and much more. What would you like to know?"
        else:
            greeting = "Hello! I am NyayaAI, your cybercrime awareness assistant. I can help you with information about digital arrest scams, banking fraud, illegal loan apps, how to report cybercrime, and much more. What would you like to know?"
        
        return {
            "answer"  : greeting,
            "source"  : None,
            "category": None,
            "found"   : True
        }

    if not chunks:
        result = client.chat.completions.create(
            model    = GROQ_MODEL,
            messages = [
                {
                    "role"   : "system",
                    "content": "You are NyayaAI, a cybercrime awareness assistant for Indian citizens."
                },
                {
                    "role"   : "user",
                    "content": user_question
                }
            ],
            temperature = 0.7,
            max_tokens  = 500
        )
        return {
            "answer"  : result.choices[0].message.content,
            "source"  : None,
            "category": "General",
            "found"   : True
        }

    context = format_context(chunks)
    prompt  = build_prompt(user_question, context, chat_history)

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

    answer     = response.choices[0].message.content.strip()
    best_chunk = chunks[0]

    return {
        "answer"  : answer,
        "source"  : best_chunk["source"],
        "category": best_chunk["category"],
        "found"   : True
    }
