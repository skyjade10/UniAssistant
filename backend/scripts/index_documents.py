
import json

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

        for chunk in document_chunks:

            chunks.append(chunk)

            metadatas.append(
                document["metadata"]
            )

    print("Generating embeddings...")

    embedding_service = EmbeddingService()

    embeddings = embedding_service.generate_embeddings(
        chunks
    )

    print("Saving to ChromaDB...")

    store = ChromaStore()

    store.reset()

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