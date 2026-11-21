#Establish whether the information exists in the knowledge base.
import json

file_path = "storage/documents/documents.jsonl"

with open(file_path, "r", encoding="utf-8") as file:
    for line in file:
        document = json.loads(line)

        title = document.get("title", "")
        url = document.get("source_url", "")
        content = document.get("content", "")

        if any(word in (title + " " + url + " " + content).lower()
               for word in ["programme", "program", "degree", "diploma"]):

            print("\nTITLE:", title)
            print("URL:", url)
            print("CONTENT:", content[:1000])
            print("-" * 60)