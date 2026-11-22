
import chromadb

from pathlib import Path

DB_PATH = Path("storage/chroma_db")

COLLECTION_NAME = "zut_knowledge"

class ChromaStore:

    def __init__(self):

        DB_PATH.mkdir(parents=True, exist_ok=True)

        self.client = chromadb.PersistentClient(
            path=str(DB_PATH)
        )

        self.collection = self.client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={
                "hnsw:space": "cosine"
            }
        )

    def add_documents(self, chunks, embeddings, metadatas):

        ids = [
            f"chunk_{i}"
            for i in range(len(chunks))
        ]

        self.collection.upsert(
            ids=ids,
            documents=chunks,
            embeddings=embeddings.tolist(),
            metadatas=metadatas
        )

        return len(ids)

    def search(self, query_embedding, top_k=4):

        results = self.collection.query(
            query_embeddings=[
                query_embedding.tolist()
            ],
            n_results=top_k
        )

        return results

    def count(self):

        return self.collection.count()

    def reset(self):

        self.client.delete_collection(
            name=COLLECTION_NAME
        )

        self.collection = self.client.create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"}
        )


    def get_all_documents(self):

        results = self.collection.get(
            include=["documents", "metadatas"]
        )

        return results