
import json

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

    total_chunks = 0

    for document in documents:

        text = clean_text(document["content"])

        chunks = split_text(text)

        total_chunks += len(chunks)

    print("DOCUMENT PROCESSING TEST")
    print("------------------------")
    print("Documents:", len(documents))
    print("Chunks:", total_chunks)

    if documents:

        sample = documents[0]

        sample_text = clean_text(sample["content"])
        sample_chunks = split_text(sample_text)

        print("\nSAMPLE CHUNK:")
        print(sample_chunks[0][:500])

if __name__ == "__main__":
    main()