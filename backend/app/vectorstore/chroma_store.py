import chromadb
import uuid

from pathlib import Path


DB_PATH = Path("storage/chroma_db")
COLLECTION_NAME = "zut_knowledge"
_CLIENTS = {}


class ChromaStore:

    def __init__(self):

        DB_PATH.mkdir(parents=True, exist_ok=True)
        cache_key = str(DB_PATH.resolve())

        if cache_key not in _CLIENTS:
            _CLIENTS[cache_key] = chromadb.PersistentClient(path=cache_key)

        self.client = _CLIENTS[cache_key]

        self.collection = self.client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"}
        )

    def add_documents(self, chunks, embeddings, metadatas):
        """Add chunks with unique IDs and document metadata."""

        if not (len(chunks) == len(embeddings) == len(metadatas)):
            raise ValueError("Chunks, embeddings and metadata lengths must match.")

        if not chunks:
            return 0

        ids = []
        clean_metadatas = []

        for metadata in metadatas:

            metadata = dict(metadata)

            if not metadata.get("document_id"):
                raise ValueError("Every chunk must have a document_id.")

            # ChromaDB metadata cannot contain None values.
            metadata = {
                key: value
                for key, value in metadata.items()
                if value is not None
            }

            clean_metadatas.append(metadata)
            ids.append(str(uuid.uuid4()))

        self.collection.upsert(
            ids=ids,
            documents=chunks,
            embeddings=embeddings.tolist(),
            metadatas=clean_metadatas
        )

        return len(ids)

    def delete_document(self, document_id):
        """Delete every indexed chunk belonging to a document."""

        results = self.collection.get(
            where={"document_id": document_id},
            include=[]
        )

        ids = results.get("ids", [])

        if ids:
            self.collection.delete(ids=ids)

        return len(ids)

    def search(self, query_embedding, top_k=4):

        if self.count() == 0:
            return {
                "ids": [[]],
                "documents": [[]],
                "metadatas": [[]],
                "distances": [[]]
            }

        return self.collection.query(
            query_embeddings=[
                query_embedding.tolist()
            ],
            n_results=min(top_k, self.count())
        )

    def count(self):
        return self.collection.count()

    def reset(self):
        """Delete and recreate the entire collection."""

        self.client.delete_collection(
            name=COLLECTION_NAME
        )

        self.collection = self.client.create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"}
        )

    def get_all_documents(self):

        return self.collection.get(
            include=["documents", "metadatas"]
        )

    def get_document_ids(self):
        """Return unique document IDs currently indexed."""

        results = self.collection.get(
            include=["metadatas"]
        )

        return sorted({
            metadata["document_id"]
            for metadata in results["metadatas"]
            if metadata and metadata.get("document_id")
        })

    def get_document_chunks(self, document_id):

        return self.collection.get(
            where={"document_id": document_id},
            include=["documents", "metadatas"]
        )
