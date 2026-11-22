from collections import Counter
from app.vectorstore.chroma_store import ChromaStore

store = ChromaStore()
data = store.get_all_documents()

print("Total chunks:", len(data["documents"]))

titles = Counter(
    (m or {}).get("title", "Unknown") for m in data["metadatas"]
)
for title, count in titles.most_common():
    print(count, "chunks ->", title)