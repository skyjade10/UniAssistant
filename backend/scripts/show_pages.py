import json

path = "storage/documents/documents.jsonl"
wanted = ("Degree - ZUT", "Diploma - ZUT", "Certificate - ZUT", "Masters - ZUT")

with open(path, "r", encoding="utf-8") as file:
    for line in file:
        if not line.strip():
            continue
        doc = json.loads(line)
        title = doc["metadata"].get("title", "")
        if title in wanted:
            print("=" * 60)
            print(title, "| length:", len(doc["content"]), "characters")
            print(doc["content"][:1000])