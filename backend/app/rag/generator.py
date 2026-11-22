import os
import re
import time
import logging

from dotenv import load_dotenv
from google import genai

load_dotenv()
logger = logging.getLogger(__name__)


class AnswerGenerator:

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY is missing.")

        self.model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        self.client = genai.Client(api_key=api_key)

    def _build_prompt(self, question, documents):
        context_start = time.perf_counter()
        context_parts = []
        sources = []
        remaining_chars = 8000

        for index, document in enumerate(documents[:4]):
            source_id = f"S{index + 1}"
            metadata = document.get("metadata", {})
            content = str(document.get("content", ""))

            if len(content) > remaining_chars:
                content = content[:remaining_chars].rsplit(" ", 1)[0] + "..."

            context_part = f"""
                SOURCE: [{source_id}]
                TITLE: {metadata.get('title', 'Unknown')}
                URL: {metadata.get('source_url', 'Not available')}
                PAGE: {metadata.get('page_number', 'Not applicable')}
                CONTENT:
                {content}
                """
            context_parts.append(context_part)
            remaining_chars -= len(content)

            sources.append({
                "id": source_id,
                "title": metadata.get("title", "Unknown"),
                "url": metadata.get("source_url"),
                "page_number": metadata.get("page_number")
            })

            if remaining_chars <= 0:
                break

        context = "\n\n".join(context_parts)
        prompt = f"""
            You are ZUT AI, an assistant for Zambia University College of Technology (ZUT).
            Answer the user's question using ONLY the university information supplied below.
            Keep the answer direct, conversational, clear and concise. Do not invent information.
            If information is unavailable, say so and suggest contacting the relevant university office.
            Do not include source IDs, citations, URLs, page numbers, or internal technical information.
            Do not start with a greeting unless the user greeted you.

            UNIVERSITY INFORMATION:
            {context}

            USER QUESTION:
            {question}

            ANSWER:
            """
        logger.info("RAG_TIMING component=context_preparation elapsed_ms=%.2f", (time.perf_counter() - context_start) * 1000)
        return prompt, sources

    def generate_answer(self, question, documents):
        if not documents:
            return {
                "answer": "I couldn't find enough information in the university's knowledge base to answer that question.",
                "sources": []
            }

        prompt, sources = self._build_prompt(question, documents)

        generation_start = time.perf_counter()
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt
        )
        generation_ms = (time.perf_counter() - generation_start) * 1000
        logger.info("RAG_TIMING component=gemini_generation elapsed_ms=%.2f", generation_ms)

        answer = response.text
        if not answer:
            raise RuntimeError("Gemini returned an empty response.")

        cited_ids = set(re.findall(r"\[S\d+\]", answer))
        cited_sources = [
            source for source in sources
            if f"[{source['id']}]" in cited_ids
        ]

        return {"answer": answer, "sources": cited_sources}

    async def generate_answer_stream(self, question, documents):
        if not documents:
            yield "I couldn't find enough information in the university's knowledge base to answer that question."
            return

        prompt = self._build_prompt(question, documents)[0]
        generation_start = time.perf_counter()
        first_chunk = True

        stream = await self.client.aio.models.generate_content_stream(
            model=self.model,
            contents=prompt
        )

        async for chunk in stream:
            if chunk.text:
                if first_chunk:
                    first_chunk_ms = (time.perf_counter() - generation_start) * 1000
                    logger.info("RAG_TIMING component=gemini_first_chunk elapsed_ms=%.2f", first_chunk_ms)
                    first_chunk = False
                yield chunk.text

        logger.info(
            "RAG_TIMING component=gemini_generation elapsed_ms=%.2f",
            (time.perf_counter() - generation_start) * 1000
        )