
from app.rag.retriever import Retriever
from app.rag.generator import AnswerGenerator

class RAGEngine:

    def __init__(self):

        self.retriever = Retriever()
        self.generator = AnswerGenerator()

    def ask(self, question):

        # Step 1: Retrieve relevant documents.
        documents = self.retriever.retrieve(
            question,
            top_k=4
        )

        # Step 2: Check whether we have useful results.
        if not documents:
            return {
                "answer": (
                    "I couldn't find enough information "
                    "in the ZUT knowledge base."
                ),
                "sources": []
            }

        # Step 3: Generate an answer.
        result = self.generator.generate_answer(
            question,
            documents
        )

        return result