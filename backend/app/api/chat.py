import asyncio
import logging
from functools import lru_cache

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.schemas.chat_schema import ChatRequest, ChatResponse

router = APIRouter(prefix="/api", tags=["Chat"])

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def get_rag_engine():
    from app.rag.engine import RAGEngine

    return RAGEngine()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        rag_engine = get_rag_engine()
        return await asyncio.to_thread(rag_engine.ask, request.question)
    except Exception:
        logger.exception("Chat API error")
        raise HTTPException(
            status_code=500,
            detail="Unable to process your question. Please try again later."
        )


@router.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    try:
        rag_engine = get_rag_engine()
        return StreamingResponse(
            rag_engine.ask_stream(request.question),
            media_type="text/plain; charset=utf-8"
        )
    except Exception:
        logger.exception("Chat stream API error")
        raise HTTPException(
            status_code=500,
            detail="Unable to process your question. Please try again later."
        )
