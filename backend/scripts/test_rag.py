
from app.rag.engine import RAGEngine


def main():

    engine = RAGEngine()

    question = input("Ask UniAssist: ")

    result = engine.ask(question)

    print("\nUNIASSIST RESPONSE")
    print("------------------")

    print(result["answer"])

    print("\nSOURCES")
    print("-------")

    for source in result["sources"]:

        print("\nSource:", source["id"])
        print("Title:", source["title"])
        print("URL:", source["url"])
        print("Page:", source["page_number"])


if __name__ == "__main__":
    main()
