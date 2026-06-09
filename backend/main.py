from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.database.db import init_db
from backend.routes.chat import router as chat_router
from backend.routes.auth import router as auth_router
from ai.config import APP_NAME, APP_VERSION, validate_config
import logging

logging.basicConfig(
    level  = logging.INFO,
    format = "%(asctime)s — %(levelname)s — %(message)s"
)
log = logging.getLogger(__name__)

app = FastAPI(
    title       = f"{APP_NAME} API",
    description = "Cybercrime Awareness Chatbot API",
    version     = APP_VERSION
)

app.add_middleware(
    CORSMiddleware,
    allow_origins     = ["*"],
    allow_credentials = True,
    allow_methods     = ["*"],
    allow_headers     = ["*"]
)

# register routers
app.include_router(auth_router)
app.include_router(chat_router)


@app.on_event("startup")
async def startup():
    validate_config()
    init_db()
    log.info(f"NyayaAI API started — v{APP_VERSION}")


@app.get("/")
def root():
    return {
        "app"    : APP_NAME,
        "version": APP_VERSION,
        "status" : "running"
    }
