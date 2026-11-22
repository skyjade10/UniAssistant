import json
from collections import Counter

path = "storage/documents/documents.jsonl"

titles = Counter()
total = 0

with open(path, "r", encoding="utf-8") as file:
    for line in file:
        if not line.strip():
            continue
        doc = json.loads(line)
        total += 1
        titles[doc.get("metadata", {}).get("title", "Unknown")] += 1

print("Total documents:", total)
for title, count in titles.most_common(15):
    print(count, "->", title)