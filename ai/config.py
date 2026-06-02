# ============================================
# NyayaAI — Central Configuration
# All settings are in one place
# If any value needs to change — only come here
# ============================================

import os
from pathlib import Path
from dotenv import load_dotenv

# load_dotenv reads the .env file
# and makes all keys available via os.getenv()
load_dotenv()

# ── Base Paths ────────────────────────────────────────
# Path(__file__) gives current file location
# .parent.parent goes up 2 folders to reach project root
BASE_DIR   = Path(__file__).parent.parent

# build full paths to data folders using BASE_DIR
# these paths are used in ingest pipeline
PDF_DIR    = BASE_DIR / "ai" / "data" / "pdfs"
FAQ_DIR    = BASE_DIR / "ai" / "data" / "faqs"
CHROMA_DIR = BASE_DIR / os.getenv("CHROMA_DB_PATH", "ai/data/chroma_db")

# ── Groq Settings ─────────────────────────────────────
# os.getenv reads value from .env file
# second argument is default value if key not found
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL   = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

# ── Embeddings Settings ───────────────────────────────
# this model converts text into vectors
# vectors are stored in ChromaDB for similarity search
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

# ── Chunking Settings ─────────────────────────────────
# controls how PDF text is split before storing in ChromaDB
CHUNK_SIZE    = 400  # max words per chunk sent to knowledge base
CHUNK_OVERLAP = 50   # words repeated between chunks to keep context

# ── RAG Settings ──────────────────────────────────────
# how many chunks to retrieve from ChromaDB per user query
# more chunks = more context but slower response
TOP_K_RESULTS = int(os.getenv("TOP_K_RESULTS", 3))

# ── ChromaDB Settings ─────────────────────────────────
# collection is like a table in ChromaDB
# all chunks are stored under this collection name
COLLECTION_NAME = "nyayaai_knowledge"

# ── Source Mapping ────────────────────────────────────
# maps short file key to full readable source name
# used in ingest pipeline to track where each chunk came from
SOURCE_MAP = {
    "TAU_397"  : "TAU-397 Monthly Underground Banking Report May 2026",
    "ADV_003"  : "Advisory TAU-ADV-003 Digital Arrest March 2025",
    "NCRP_FAQ" : "NCRP FAQ - cybercrime.gov.in"
}

# ── App Settings ──────────────────────────────────────
# used in frontend to display app name and version
APP_NAME    = os.getenv("APP_NAME", "NyayaAI")
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")

# ── Validation ────────────────────────────────────────
# called at startup to check all required keys are present
# raises error immediately if anything is missing
# better to fail early than fail silently later
def validate_config():
    errors = []

    # GROQ_API_KEY is required — without it RAG cannot generate answers
    if not GROQ_API_KEY:
        errors.append("GROQ_API_KEY missing — add it in .env file")

    # if any errors found — raise them all at once
    if errors:
        raise ValueError("Config Error:\n" + "\n".join(errors))

    print(f"✅ Config loaded — {APP_NAME} v{APP_VERSION}")
