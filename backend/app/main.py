import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.chat import router as chat_router
from app.api.admin import router as admin_router

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)

logger = logging.getLogger(__name__)
logger.info("RAG timing logs enabled")


app = FastAPI(
    title="ZUT Ai assistant",
    description="A RAG-powered AI assistant for ZUT students",
    version="1.0.0",
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


@app.get("/api/health")
def health():
    return {
        "status": "healthy"
    }


# __file__ is app/main.py. 
# .parents[0] is app/
# .parents[1] is the root directory containing both app/ and frontend/
FRONTEND_DIR = Path(__file__).resolve().parents[1] / "frontend"

app.mount(
    "/assets",
    StaticFiles(directory=FRONTEND_DIR, html=True),
    name="assets",
)
app.mount(
    "/admin",
    StaticFiles(directory=FRONTEND_DIR / "admin", html=True),
    name="admin",
)
app.mount(
    "/",
    StaticFiles(directory=FRONTEND_DIR / "chatbot", html=True),
    name="chatbot",
)

if __name__ == "__main__":
    import uvicorn

    # Default to 0.0.0.0 so the application is universally bindable across cloud providers
    host = os.getenv("HOST", "0.0.0.0")

    try:
        # Defaulting to 10000 to match Render's base service deployment requirements
        port = int(os.getenv("PORT", "10000"))
    except ValueError as error:
        raise RuntimeError("PORT must be a valid integer.") from error

    if not 1 <= port <= 65535:
        raise RuntimeError("PORT must be between 1 and 65535.")

    reload_enabled = os.getenv("UVICORN_RELOAD", "false").lower() in {
        "1",
        "true",
        "yes",
        "on",
    }

    uvicorn.run(
        app,
        host=host,
        port=port,
        reload=reload_enabled,
    )
