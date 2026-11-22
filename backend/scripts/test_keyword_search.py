import chromadb

client = chromadb.PersistentClient(
    path="storage/chroma_db"
)

collection = client.get_collection("zut_knowledge")

results = collection.get(
    include=["documents", "metadatas"]
)

keywords = [
    "undergraduate",
    "programmes",
    "full-time degree programmes",
    "bachelor"
]

matches = []

for document, metadata in zip(
    results["documents"],
    results["metadatas"]
):
    text = document.lower()

    score = sum(
        1 for keyword in keywords
        if keyword in text
    )

    if score > 0:
        matches.append((score, metadata, document))

matches.sort(
    key=lambda item: item[0],
    reverse=True
)

for score, metadata, document in matches[:10]:
    print("\n" + "=" * 60)
    print("Score:", score)
    print("Metadata:", metadata)
    print("Content:", document[:1000])