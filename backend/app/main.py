import logging

from fastapi import FastAPI
from app.api.chat import router as chat_router
from app.api.admin import router as admin_router
from fastapi.middleware.cors import CORSMiddleware

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)

logger = logging.getLogger(__name__)
logger.info("RAG timing logs enabled")


app = FastAPI(
    title = "ZUT Ai assistant",
    description = "A RAG-powered AI assistant for ZUT students",
    version = "1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500"
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=[
        "Content-Type",
        "Authorization"
    ],
)

app.include_router(chat_router)
app.include_router(admin_router)

@app.get("/")
def home():
    return {
        "message": "Welcome to ZUT Ai",
        "status": "running"
    }

@app.get("/api/health")
def health():
    return {
        "status": "healthy"
    }