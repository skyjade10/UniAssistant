
import json

from app.embeddings.embedding_service import EmbeddingService
from app.processing.text_cleaner import clean_text
from app.processing.text_splitter import split_text

INPUT_FILE = "storage/documents/documents.jsonl"

def main():

    with open(INPUT_FILE, "r", encoding="utf-8") as file:
        documents = [
            json.loads(line)
            for line in file
            if line.strip()
        ]

    chunks = []

    for document in documents:

        text = clean_text(document["content"])

        document_chunks = split_text(text)

        chunks.extend(document_chunks)

    embedding_service = EmbeddingService()

    embeddings = embedding_service.generate_embeddings(
        chunks
    )

    print("EMBEDDING TEST")
    print("--------------")
    print("Chunks:", len(chunks))
    print("Embeddings:", len(embeddings))
    print("Vector dimensions:", embeddings.shape[1])

    print("\nFirst embedding:")
    print(embeddings[0][:10])

if __name__ == "__main__":
    main()