
from app.embeddings.embedding_service import EmbeddingService
from app.vectorstore.chroma_store import ChromaStore

def main():

    store = ChromaStore()
    embedding_service = EmbeddingService()

    question = "What undergraduate degree programmes are listed in the ZUT application form?"

    embedding = embedding_service.generate_embedding(question)

    print("Collection count:", store.count())

    results = store.search(embedding, top_k=10)

    print("\nSEARCH RESULTS")

    for i, document in enumerate(results["documents"][0]):

        print(f"\n--- RESULT {i + 1} ---")
        print("Content:", document[:500])

        print("Metadata:", results["metadatas"][0][i])

        print("Distance:", results["distances"][0][i])

if __name__ == "__main__":
    main()