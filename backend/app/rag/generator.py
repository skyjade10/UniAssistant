
import os
import re

from dotenv import load_dotenv
from google import genai

load_dotenv()

class AnswerGenerator:

    def __init__(self):

        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError("GEMINI_API_KEY is missing.")

        self.model = os.getenv(
            "GEMINI_MODEL",
            "gemini-2.5-flash"
        )

        self.client = genai.Client(
            api_key=api_key
        )

    def generate_answer(self, question, documents):
        #raise RuntimeError("Simulated Gemini API failure")

        if not documents:
            return {
                "answer": (
                    "I couldn't find enough information "
                    "in the university's knowledge base "
                    "to answer that question."
                ),
                "sources": []
            }

        context_parts = []
        sources = []

        for index, document in enumerate(documents):

            source_id = f"S{index + 1}"

            metadata = document["metadata"]

            context_parts.append(
                f"""
                    SOURCE: [{source_id}]
                    TITLE: {metadata.get("title", "Unknown")}
                    URL: {metadata.get("source_url", "Not available")}
                    PAGE: {metadata.get("page_number", "Not applicable")}

                    CONTENT:
                    {document["content"]}
                    """
            )

            sources.append({
                "id": source_id,
                "title": metadata.get("title", "Unknown"),
                "url": metadata.get("source_url"),
                "page_number": metadata.get("page_number")
            })

        context = "\n\n".join(context_parts)

        prompt = f"""
            You are ZUT AI, an assistant for
            Zambia University College of Technology (ZUT).

            Answer the user's question using ONLY the
            university information supplied in the context.

            RULES:
            1. Answer naturally, like a helpful university front-desk assistant.
            2. Use the supplied university information to answer questions.
            3. Never say "Based on the context", "According to the
            retrieved documents", or similar technical phrases.
            4. Do not mention retrieval, embeddings, databases, documents
            supplied to you, or internal system operations.
            5. Give direct answers first, followed by useful details.
            6. Do not invent university information.
            7. If information is unavailable, politely explain that
            you don't have that information and suggest contacting
            the relevant university office.
            8. Keep answers conversational, clear and concise.
            9. Do not include source IDs, citation markers, URLs or
            page numbers in the answer.
            10. Do not expose internal technical information.
            

            ACADEMIC PROGRAMME QUESTIONS:

            - Prioritize official programme catalogues and application forms.
            - Retrieve and consider all relevant programme information.
            - Combine information from multiple retrieved chunks when necessary.
            - Distinguish degree, diploma and professional programmes.
            - Distinguish full-time, evening and distance-learning modes.
            - Do not present a partial list as a complete list.
            - Do not use news articles as the sole authority for a complete
            programme directory.
            - If the retrieved context is insufficient, clearly say so.

            SOURCE PRIORITY:
            1. Official programme catalogues and application forms.
            2. Official academic programme pages.
            3. Official admission documents.
            4. Official news articles.

            When answering questions about academic programmes,
            prioritize official programme catalogues and application forms.

            Do not treat news articles as complete programme directories.

            If the retrieved context contains only partial programme
            information, explicitly state that the list may be incomplete.

            Never invent or infer programmes.

            UNIVERSITY INFORMATION:

            {context}

            USER QUESTION:

            {question}

            ANSWER:
            """

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt
        )

        answer = response.text

        if not answer:
            raise RuntimeError(
                "Gemini returned an empty response."
            )

        # Extract source IDs cited in the generated answer.
        cited_ids = set(
            re.findall(r"\[S\d+\]", answer)
        )

        # Keep only sources referenced in the answer.
        cited_sources = [
            source for source in sources
            if f"[{source['id']}]" in cited_ids
        ]

        print("\nDEBUG - GEMINI ANSWER:")
        print(answer)

        print("\nDEBUG - ALL SOURCES:")
        print(sources)

        print("\nDEBUG - CITED IDS:")
        print(cited_ids)

        print("\nDEBUG - FILTERED SOURCES:")
        print(cited_sources)

        return {
            "answer": answer,
            "sources": cited_sources
        }