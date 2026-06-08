# ============================================
# NyayaAI — Database Connection
# Creates SQLAlchemy engine and session
# Connects to PostgreSQL using config.py
# All database operations use this session
# ============================================

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from ai.config import DATABASE_URL
import logging

log = logging.getLogger(__name__)

# create SQLAlchemy engine
# engine manages actual connection to PostgreSQL
engine = create_engine(
    DATABASE_URL,
    echo=False  # set True to see SQL queries in terminal
)

# SessionLocal is a factory for database sessions
# each request gets its own session
SessionLocal = sessionmaker(
    autocommit = False,
    autoflush  = False,
    bind       = engine
)

# Base class for all database models
# all models will inherit from this
Base = declarative_base()


def get_db():
    # dependency function — used in FastAPI routes
    # creates a new session for each request
    # closes session after request is done
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    # creates all tables in PostgreSQL
    # called once at startup
    # safe to call multiple times — 
    # only creates tables if they dont exist
    try:
        Base.metadata.create_all(bind=engine)
        log.info("✅ Database tables created successfully")
    except Exception as e:
        log.error(f"❌ Database connection failed: {e}")
        raise e
