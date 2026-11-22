import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.rag.retriever import Retriever
from app.rag.query_expander import expand_query

retriever = Retriever()

retriever.debug_retrieval("Where is ZUT located?")
print("end of debug")
results = retriever.retrieve(
    "What is the physical address and location of ZUT?",
    top_k=5
)

for i, doc in enumerate(results, 1):
    print(f"\nSOURCEz {i}")
    print("METADATA:", doc["metadata"])
    print("CONTENT:", doc["content"][:1000])

question = "List the undergraduate degree programmes offered by ZUT"

expanded_question = expand_query(question)

results = retriever.retrieve(question, top_k=10)

for rank, result in enumerate(results, start=1):

    print(f"\nRank: {rank}")
    print("Title:", result["metadata"].get("title"))
    print("Page:", result["metadata"].get("page_number"))
    print("RRF Score:", result["rrf_score"])
    print("Keyword Score:", result.get("keyword_score"))
    print("Distance:", result.get("distance"))
    print("Content:", result["content"][:500])

print("\nORIGINAL QUESTION:")
print(question)

print("\nEXPANDED QUESTION:")
print(expanded_question)

# Test semantic retrieval independently
semantic_results = retriever.semantic_retrieve(
    expanded_question,
    top_k=10
)

print("\n" + "=" * 60)
print("SEMANTIC RESULTS")

for rank, result in enumerate(semantic_results, 1):
    metadata = result["metadata"]

    print(f"\nRank: {rank}")
    print("Title:", metadata.get("title"))
    print("Page:", metadata.get("page_number"))
    print("Distance:", result["distance"])
    print("Content:", result["content"][:250])

# Test keyword retrieval independently
keyword_results = retriever.keyword_retrieve(
    question,
    top_k=10
)

print("\n" + "=" * 60)
print("KEYWORD RESULTS")

for rank, result in enumerate(keyword_results, 1):
    metadata = result["metadata"]

    print(f"\nRank: {rank}")
    print("Title:", metadata.get("title"))
    print("Page:", metadata.get("page_number"))
    print("Keyword score:", result["keyword_score"])
    print("Content:", result["content"][:250])
