
import logging

from fastapi import APIRouter, HTTPException
from app.schemas.chat_schema import ChatRequest, ChatResponse
from app.rag.engine import RAGEngine

router = APIRouter(prefix="/api", tags=["Chat"])

logger = logging.getLogger(__name__)

rag_engine = RAGEngine()


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):

    try:
        result = rag_engine.ask(request.question)

        return result

    except Exception:
        logger.exception("Chat API error")

        raise HTTPException(
            status_code=500,
            detail="Unable to process your question. Please try again later."
        )
