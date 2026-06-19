# ============================================
# NyayaAI — Central Configuration
# All settings in one place
# If any value needs to change — only come here
# ============================================

import os
from pathlib import Path
from dotenv import load_dotenv

# load_dotenv reads .env file
# makes all keys available via os.getenv()
load_dotenv()

# ── Base Paths ────────────────────────────────────────
# Path(__file__) gives current file location
# .parent.parent goes up 2 folders to reach project root
BASE_DIR   = Path(__file__).parent.parent

# full paths to data folders
PDF_DIR    = BASE_DIR / "ai" / "data" / "pdfs"
FAQ_DIR    = BASE_DIR / "ai" / "data" / "faqs"
CHROMA_DIR = BASE_DIR / os.getenv("CHROMA_DB_PATH",
                                   "ai/data/chroma_db")

# ── Groq Settings ─────────────────────────────────────
# os.getenv reads value from .env file
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL   = os.getenv("GROQ_MODEL",
                          "llama-3.3-70b-versatile")

# ── Embeddings Settings ───────────────────────────────
# this model converts text into vectors
# vectors stored in ChromaDB for similarity search
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL",
                             "all-MiniLM-L6-v2")

# ── Chunking Settings ─────────────────────────────────
# controls how PDF text is split before storing
CHUNK_SIZE    = 400  # max words per chunk
CHUNK_OVERLAP = 50   # words repeated between chunks

# ── RAG Settings ──────────────────────────────────────
# how many chunks to retrieve per user query
TOP_K_RESULTS = int(os.getenv("TOP_K_RESULTS", 3))

# ── ChromaDB Settings ─────────────────────────────────
# collection is like a table in ChromaDB
COLLECTION_NAME = "nyayaai_knowledge"

# ── Categories ────────────────────────────────────────
# fixed list of topics for the knowledge base
# every chunk belongs to one of these categories
# used in chunker.py for category detection
# used in frontend for filtering
CATEGORIES = [
    "Digital Arrest Scam",
    "Scam Modus Operandi",
    "Cybercrime Prevention Tips",
    "NCRP Portal Usage",
    "Complaint Filing Process",
    "Evidence and Legal Process",
    "Money Mule Operations",
    "Underground Banking Trends",
    "USDT Crypto Laundering",
    "Illegal Loan Apps",
    "Banking Fraud Indicators",
    "Regulatory Recommendations"
]

# ── Source Mapping ────────────────────────────────────
# short key → full readable source name
# add new entry here when new PDF or FAQ is added
SOURCE_MAP = {
    "TAU_397"      : "TAU-397 Monthly Underground Banking Report May 2026",
    "ADV_003"      : "Advisory TAU-ADV-003 Digital Arrest March 2025",
    "NCRP_FAQ"     : "NCRP FAQ - cybercrime.gov.in",
    "I4C_FAQ"      : "I4C Cybercrime Advisories",
    "ROAD_ACC_FAQ" : "Road Accident FAQ - India",
    "TRAFFIC_FAQ"  : "Traffic Rules FAQ - India",
    "ADSI_2024"    : "ADSI 2024 Chapter 1A - Traffic",
    "MVA_1988"     : "Motor Vehicles Act 1988",
    "CMVR_1989"    : "Central Motor Vehicles Rules 1989",
    "MVA_2019"     : "Motor Vehicles Amendment Act 2019"
}

# ── App Settings ──────────────────────────────────────
APP_NAME    = os.getenv("APP_NAME", "NyayaAI")
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")

# ── Database Settings ─────────────────────────
# PostgreSQL connection string
# reads from .env file
DB_HOST     = os.getenv("DB_HOST", "localhost")
DB_PORT     = os.getenv("DB_PORT", "5432")
DB_NAME     = os.getenv("DB_NAME", "nyayaai_db")
DB_USER     = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

# full database URL for SQLAlchemy
# use Railway DATABASE_URL if available
# fallback to individual vars for local
DATABASE_URL = os.getenv("DATABASE_URL", None)

if not DATABASE_URL:
    DATABASE_URL = (
        f"postgresql://{DB_USER}:{DB_PASSWORD}"
        f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

# Railway uses postgres:// fix to postgresql://
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace(
        "postgres://", "postgresql://", 1
    )

# ── JWT Settings ──────────────────────────────────────
SECRET_KEY                  = os.getenv("SECRET_KEY", "nyayaai_secret")
ALGORITHM                   = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 10080))

# ── Email Settings ────────────────────────────────────
MAIL_USERNAME = os.getenv("MAIL_USERNAME", "")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "")
MAIL_FROM     = os.getenv("MAIL_FROM", "")
MAIL_SERVER   = os.getenv("MAIL_SERVER", "smtp.gmail.com")
MAIL_PORT     = int(os.getenv("MAIL_PORT", 587))

# ── Validation ────────────────────────────────────────
# called at startup to check all required keys present
# fails early rather than failing silently later
def validate_config():
    errors = []

    if not GROQ_API_KEY:
        errors.append(
            "GROQ_API_KEY missing — add it in .env file"
        )

    if errors:
        raise ValueError(
            "Config Error:\n" + "\n".join(errors)
        )

    print(f"✅ Config loaded — {APP_NAME} v{APP_VERSION}")
