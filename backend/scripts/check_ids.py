import json

path = "storage/documents/documents.jsonl"

with open(path, "r", encoding="utf-8") as file:
    for number, line in enumerate(file, start=1):
        if not line.strip():
            continue
        doc = json.loads(line)
        metadata = doc.get("metadata", {})
        has_id = bool(metadata.get("document_id"))
        print(number, "OK     " if has_id else "MISSING", metadata.get("title"))
        if number == 1:
            print("   metadata keys:", list(metadata.keys()))