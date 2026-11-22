import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))
    
from app.vectorstore.chroma_store import ChromaStore
from app.embeddings.embedding_service import EmbeddingService

store = ChromaStore()
embedding_service = EmbeddingService()

query = "Kalewa Road Northrise Ndola physical address"
query_embedding = embedding_service.generate_embedding(query)

results = store.search(query_embedding, top_k=10)

documents = results["documents"][0]
metadatas = results["metadatas"][0]
distances = results["distances"][0]

pdf_found = False

for i, (content, metadata, distance) in enumerate(
    zip(documents, metadatas, distances), start=1
):
    title = metadata.get("title", "Unknown")
    url = metadata.get("source_url", "Unknown")
    page = metadata.get("page_number")

    print(f"\nRESULT {i}")
    print("TITLE:", title)
    print("URL:", url)
    print("PAGE:", page)
    print("DISTANCE:", round(distance, 4))

    if "APPLICATION FORM" in title.upper():
        pdf_found = True
        print("PDF CONTENT:", content[:1500])

print("\nPDF FOUND IN TOP 10:", pdf_found)
