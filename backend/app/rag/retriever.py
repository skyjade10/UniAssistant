
from app.embeddings.embedding_service import EmbeddingService
from app.vectorstore.chroma_store import ChromaStore
from app.rag.query_expander import expand_query

class Retriever:

    def __init__(self):

        self.embedding_service = EmbeddingService()
        self.store = ChromaStore()

    
    def retrieve(self, question, top_k=5):

        expanded_question = expand_query(question)

        question_embedding = (
            self.embedding_service.generate_embedding(expanded_question)
        )

        results = self.store.search(
            question_embedding,
            top_k=top_k * 3
        )

        documents = results["documents"][0]
        metadatas = results["metadatas"][0]
        distances = results["distances"][0]

        retrieved_documents = []
        seen_chunks = set()

        for document, metadata, distance in zip(
            documents,
            metadatas,
            distances
        ):

            source_url = metadata.get("source_url")

            # Prevent duplicate chunks from the same source.
            if document in seen_chunks:
                continue

            seen_chunks.add(document)

            retrieved_documents.append({
                "content": document,
                "metadata": metadata,
                "distance": float(distance)
            })

            if len(retrieved_documents) >= top_k:
                break

        return retrieved_documents