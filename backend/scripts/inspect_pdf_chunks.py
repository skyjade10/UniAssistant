from app.vectorstore.chroma_store import ChromaStore

store = ChromaStore()

results = store.collection.get(
    where={"source_type": "pdf"},
    include=["documents", "metadatas"]
)

for i, document in enumerate(results["documents"]):

    metadata = results["metadatas"][i]

    print(f"\n--- PDF CHUNK {i + 1} ---")
    print("Page:", metadata.get("page_number"))
    print("Title:", metadata.get("title"))
    print("Content:", document[:1000])