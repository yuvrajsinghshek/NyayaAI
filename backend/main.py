# ============================================
# NyayaAI — FastAPI Main Application
# Entry point for backend API
# Run with: uvicorn backend.main:app --reload
# API docs at: http://localhost:8000/docs
# ============================================

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.database.db import init_db
from backend.routes.chat import router as chat_router
from ai.config import APP_NAME, APP_VERSION, validate_config
import logging

# setup logging
logging.basicConfig(
    level  = logging.INFO,
    format = "%(asctime)s — %(levelname)s — %(message)s"
)
log = logging.getLogger(__name__)

# create FastAPI app instance
app = FastAPI(
    title       = f"{APP_NAME} API",
    description = "Cybercrime Awareness Chatbot API",
    version     = APP_VERSION
)

# CORS middleware — allows frontend to call API
# origins list mein frontend URL add karo
app.add_middleware(
    CORSMiddleware,
    allow_origins     = ["*"],  # production mein specific URL daalo
    allow_credentials = True,
    allow_methods     = ["*"],
    allow_headers     = ["*"]
)

# include chat router — registers all chat endpoints
app.include_router(chat_router)


@app.on_event("startup")
async def startup():
    # runs when server starts
    # validates config and creates database tables
    validate_config()
    init_db()
    log.info(f"🚀 {APP_NAME} API started — v{APP_VERSION}")


@app.get("/")
def root():
    # health check endpoint
    # confirms API is running
    return {
        "app"    : APP_NAME,
        "version": APP_VERSION,
        "status" : "running"
    }
