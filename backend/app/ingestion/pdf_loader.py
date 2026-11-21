
import requests
from urllib.parse import urlparse

import pymupdf as fitz

def load_pdf_bytes(pdf_bytes, filename, source_url=None):
    """Extract text from each page of a PDF."""

    if not pdf_bytes.startswith(b"%PDF-"):
        raise ValueError("The uploaded file is not a valid PDF.")

    documents = []

    try:
        pdf = fitz.open(
            stream=pdf_bytes,
            filetype="pdf"
        )

        if pdf.is_encrypted:
            raise ValueError("Encrypted PDFs are not supported.")

        for page_index, page in enumerate(pdf):

            text = page.get_text("text").strip()

            # Ignore pages without extractable text.
            if not text:
                continue

            documents.append({
                "content": text,

                "metadata": {
                    "title": filename,
                    "source_type": "pdf",
                    "source_url": source_url,
                    "page_number": page_index + 1
                }
            })

        pdf.close()

    except Exception as error:
        raise ValueError(
            f"Could not process PDF: {error}"
        ) from error

    return documents


ALLOWED_HOSTS = {
    "zut.ac.zm",
    "www.zut.ac.zm"
}

MAX_PDF_SIZE = 15 * 1024 * 1024  # 15 MB

def load_pdf_url(url):
    """Download and extract an approved ZUT website PDF."""

    parsed = urlparse(url)

    if parsed.hostname not in ALLOWED_HOSTS:
        raise ValueError("PDF URL is outside the approved domain.")

    if parsed.scheme != "https":
        raise ValueError("PDF downloads must use HTTPS.")

    response = requests.get(
        url,
        timeout=30,
        stream=True,
        headers={"User-Agent": "UniAssistAI/1.0"}
    )

    response.raise_for_status()

    if urlparse(response.url).hostname not in ALLOWED_HOSTS:
        raise ValueError("PDF redirected outside the approved domain.")

    content_length = response.headers.get("Content-Length")

    if content_length and int(content_length) > MAX_PDF_SIZE:
        raise ValueError("PDF exceeds the 15 MB size limit.")

    chunks = []
    total_size = 0

    for chunk in response.iter_content(chunk_size=8192):
        if not chunk:
            continue

        total_size += len(chunk)

        if total_size > MAX_PDF_SIZE:
            raise ValueError("PDF exceeds the 15 MB size limit.")

        chunks.append(chunk)

    pdf_bytes = b"".join(chunks)

    filename = urlparse(url).path.split("/")[-1] or "document.pdf"

    return load_pdf_bytes(
        pdf_bytes,
        filename,
        source_url=url
    )