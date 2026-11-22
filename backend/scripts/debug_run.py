from app.rag.retriever import Retriever

question = "what can i study at zut"

retriever = Retriever()

# Your existing debug method: shows semantic, keyword and hybrid rankings
retriever.debug_retrieval(question)

# Shows the actual chunks that would be sent to Gemini
docs = retriever.retrieve(question, top_k=4)

print("\n========== CHUNKS SENT TO GEMINI ==========")
for i, doc in enumerate(docs, start=1):
    print(f"\n--- Chunk {i} ---")
    print("Title:", doc["metadata"].get("title"))
    print("Length:", len(doc["content"]), "characters")
    print("First 500 characters:")
    print(doc["content"][:500])