import asyncio
import logging

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.schemas.chat_schema import ChatRequest, ChatResponse
from app.rag.engine import RAGEngine

router = APIRouter(prefix="/api", tags=["Chat"])

logger = logging.getLogger(__name__)

rag_engine = RAGEngine()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
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
