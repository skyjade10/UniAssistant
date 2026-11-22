import json
import hashlib

from app.processing.text_cleaner import clean_text
from app.processing.text_splitter import split_text

from app.embeddings.embedding_service import EmbeddingService
from app.vectorstore.chroma_store import ChromaStore

INPUT_FILE = "storage/documents/documents.jsonl"

def main():

    with open(INPUT_FILE, "r", encoding="utf-8") as file:

        documents = [
            json.loads(line)
            for line in file
            if line.strip()
        ]

    chunks = []
    metadatas = []

    for document in documents:

        text = clean_text(document["content"])

        document_chunks = split_text(text)

        metadata = dict(document["metadata"])
        key = metadata.get("source_url") or metadata.get("title", "unknown")
        metadata["document_id"] = hashlib.sha1(key.encode("utf-8")).hexdigest()[:16]

        for chunk in document_chunks:

            chunks.append(chunk)
            metadatas.append(metadata)

    print("Generating embeddings...")

    embedding_service = EmbeddingService()

    embeddings = embedding_service.generate_embeddings(
        chunks
    )

    print("Saving to ChromaDB...")

    store = ChromaStore()

    # Refresh only the website/PDF documents being re-indexed.  This keeps
    # uploaded admin documents and all other existing Chroma records intact.
    document_ids = sorted({
        metadata["document_id"]
        for metadata in metadatas
        if metadata.get("document_id")
    })

    for document_id in document_ids:
        store.delete_document(document_id)

    total = store.add_documents(
        chunks,
        embeddings,
        metadatas
    )

    print("\nINDEXING COMPLETE")
    print("-----------------")
    print("Documents:", len(documents))
    print("Chunks:", len(chunks))
    print("Stored:", total)
    print("Database count:", store.count())

if __name__ == "__main__":
    main()