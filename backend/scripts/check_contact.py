
import json

from pathlib import Path

file_path = Path("storage/documents/documents.jsonl")

with open(file_path, "r", encoding="utf-8") as file:
    for line in file:
        document = json.loads(line)

        metadata = document.get("metadata", {})
        content = document.get("content", "")

        url = metadata.get("source_url", "")

        if "contact" in url.lower() or "northrise" in content.lower():
            print("\nFOUND DOCUMENT")
            print("URL:", url)
            print("TITLE:", metadata.get("title"))
            print("CONTENT:", content[:2000])
