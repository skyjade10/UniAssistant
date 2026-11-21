
from app.ingestion.website_loader import crawl_website
from app.ingestion.pdf_loader import load_pdf_url

SEED_URLS = [
    "https://zut.ac.zm/",
    "https://zut.ac.zm/all-news-stories",
    "https://zut.ac.zm/programs/2/Degree"
]

def main():

    result = crawl_website(SEED_URLS)

    website_documents = result["documents"]
    pdf_urls = result["pdf_urls"]

    print("\nWEBSITE COLLECTION")
    print("------------------")

    print("Pages collected:", len(website_documents))
    print("PDF links discovered:", len(pdf_urls))

    for document in website_documents[:5]:
        print("\nTitle:", document["metadata"]["title"])
        print("URL:", document["metadata"]["source_url"])
        print("Characters:", len(document["content"]))

    print("\nPDF COLLECTION")
    print("--------------")

    for url in pdf_urls:

        try:
            documents = load_pdf_url(url)

            print(
                f"Collected {len(documents)} pages from {url}"
            )

        except Exception as error:
            print(f"Could not process {url}: {error}")

if __name__ == "__main__":
    main()