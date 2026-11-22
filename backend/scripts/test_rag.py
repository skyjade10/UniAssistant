from app.rag.engine import RAGEngine

engine = RAGEngine()

questions = [
    "Where is ZUT located?",
    "List the undergraduate degree programmes offered by ZUT."
]

for question in questions:

    print("\n" + "=" * 60)
    print("QUESTION:", question)
    print("=" * 60)

    result = engine.ask(question)

    print("\nANSWER:")
    print(result["answer"])

    print("\nSOURCES:")

    for source in result["sources"]:
        print(
            source["id"],
            source["title"],
            "Page:", source["page_number"],
            "URL:", source["url"]
        )