import asyncio

from app.rag.retriever import Retriever
from app.rag.generator import AnswerGenerator


class RAGEngine:

    def __init__(self):
        self.retriever = Retriever()
        self.generator = AnswerGenerator()

    def ask(self, question):
        documents = self.retriever.retrieve(question, top_k=4)

        if not documents:
            return {
                "answer": "I couldn't find enough information in the ZUT knowledge base.",
                "sources": []
            }

        return self.generator.generate_answer(question, documents)

    async def ask_stream(self, question):
        documents = await asyncio.to_thread(
            self.retriever.retrieve,
            question,
            4
        )

        if not documents:
            yield "I couldn't find enough information in the ZUT knowledge base."
            return

        async for chunk in self.generator.generate_answer_stream(question, documents):
            yield chunk