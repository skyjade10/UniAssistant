
import json

from pathlib import Path

from app.ingestion.website_loader import crawl_website
from app.ingestion.pdf_loader import load_pdf_url

STORAGE_DIR = Path("storage/documents")

SEED_URLS = [
    "https://zut.ac.zm/",
    "https://zut.ac.zm/all-news-stories",
    "https://zut.ac.zm/programs/2/Degree",
    "https://zut.ac.zm/admission-requirements",
    "https://zut.ac.zm/faqs",
    "https://zut.ac.zm/about-us",
    "https://zut.ac.zm/contact"
]

def save_documents(documents):
    """Save extracted documents as JSON Lines."""

    STORAGE_DIR.mkdir(parents=True, exist_ok=True)

    output_file = STORAGE_DIR / "documents.jsonl"

    with output_file.open("w", encoding="utf-8") as file:

        for document in documents:
            file.write(
                json.dumps(document, ensure_ascii=False) + "\n"
            )

    return output_file

def ingest_website():
    """Collect website pages and their linked PDFs."""

    result = crawl_website(SEED_URLS)

    documents = result["documents"]

    for pdf_url in result["pdf_urls"]:

        try:
            pdf_documents = load_pdf_url(pdf_url)

            documents.extend(pdf_documents)

        except Exception as error:
            print(f"PDF ingestion failed: {error}")

    output_file = save_documents(documents)

    return {
        "total_documents": len(documents),
        "output_file": str(output_file)
    }

if __name__ == "__main__":

    result = ingest_website()

    print("\nINGESTION COMPLETE")
    print("------------------")
    print("Documents:", result["total_documents"])
    print("Saved to:", result["output_file"])