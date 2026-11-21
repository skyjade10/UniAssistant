
import time
import requests

from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, urldefrag
from urllib.robotparser import RobotFileParser

BASE_URL = "https://zut.ac.zm"

ALLOWED_HOSTS = {
    "zut.ac.zm",
    "www.zut.ac.zm"
}

USER_AGENT = "UniAssistAI/1.0 (University information assistant)"

HEADERS = {
    "User-Agent": USER_AGENT
}

MAX_PAGES = 30
REQUEST_DELAY = 1.5

def get_robots_parser():
    """Read the website's robots.txt rules."""

    robots_url = urljoin(BASE_URL, "/robots.txt")

    response = requests.get(
        robots_url,
        headers=HEADERS,
        timeout=15
    )

    if response.status_code == 404:
        # No robots.txt file exists.
        return None

    response.raise_for_status()

    parser = RobotFileParser()
    parser.set_url(robots_url)
    parser.parse(response.text.splitlines())

    return parser

def is_allowed_url(url):
    """Only allow URLs belonging to the ZUT website."""

    parsed = urlparse(url)

    if parsed.scheme not in ("http", "https"):
        return False

    if parsed.hostname not in ALLOWED_HOSTS:
        return False

    return True

def extract_page_content(html, url):
    """Extract useful text and links from a web page."""

    soup = BeautifulSoup(html, "html.parser")

    title = (
        soup.title.get_text(strip=True)
        if soup.title
        else url
    )

    # Remove elements that usually contain navigation
    # or non-content information.
    for element in soup.select(
        "script, style, nav, footer, header, "
        "aside, form, noscript, iframe"
    ):
        element.decompose()

    main = soup.find("main") or soup.find("article") or soup.body

    if main is None:
        return None

    text = main.get_text(separator="\n", strip=True)

    links = []

    for anchor in soup.find_all("a", href=True):
        link = urljoin(url, anchor["href"])
        link, _ = urldefrag(link)

        if is_allowed_url(link):
            links.append(link)

    return {
        "content": text,
        "metadata": {
            "title": title,
            "source_type": "website",
            "source_url": url,
            "page_number": None
        },
        "links": links
    }

def crawl_website(seed_urls):
    """Collect approved website pages and discover PDF links."""

    robots = get_robots_parser()

    visited = set()
    queue = list(seed_urls)

    documents = []
    pdf_urls = set()

    session = requests.Session()
    session.headers.update(HEADERS)

    while queue and len(visited) < MAX_PAGES:

        url = queue.pop(0)
        url, _ = urldefrag(url)

        if url in visited:
            continue

        if not is_allowed_url(url):
            continue

        if robots and not robots.can_fetch(USER_AGENT, url):
            print(f"Blocked by robots.txt: {url}")
            continue

        try:
            print(f"Collecting: {url}")

            response = session.get(
                url,
                timeout=20,
                allow_redirects=True
            )

            response.raise_for_status()

            final_url = response.url

            if not is_allowed_url(final_url):
                continue

            content_type = response.headers.get(
                "Content-Type", ""
            ).lower()

            # Ignore non-HTML resources.
            if "text/html" not in content_type:
                continue

            visited.add(final_url)

            page = extract_page_content(
                response.text,
                final_url
            )

            if page is None:
                continue

            if page["content"].strip():
                documents.append({
                    "content": page["content"],
                    "metadata": page["metadata"]
                })

            for link in page["links"]:

                if link.lower().split("?")[0].endswith(".pdf"):
                    pdf_urls.add(link)

                elif link not in visited and link not in queue:
                    queue.append(link)

            time.sleep(REQUEST_DELAY)

        except requests.RequestException as error:
            print(f"Failed to collect {url}: {error}")

    return {
        "documents": documents,
        "pdf_urls": sorted(pdf_urls)
    }