from pydantic import BaseModel, Field
from typing import List, Optional


class ChatRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=2,
        max_length=1000
    )


class Source(BaseModel):
    id: str
    title: str
    url: Optional[str] = None
    page_number: Optional[int] = None


class ChatResponse(BaseModel):
    answer: str
    sources: List[Source]