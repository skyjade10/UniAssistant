
def split_text(text, chunk_size=2000, overlap=400):
    """Split text while preferring paragraph boundaries."""

    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("Invalid overlap")

    paragraphs = [
        paragraph.strip()
        for paragraph in text.split("\n")
        if paragraph.strip()
    ]

    chunks = []
    current_chunk = ""

    for paragraph in paragraphs:

        # Handle paragraphs larger than the chunk size.
        if len(paragraph) > chunk_size:

            if current_chunk:
                chunks.append(current_chunk)
                current_chunk = ""

            start = 0

            while start < len(paragraph):

                end = start + chunk_size

                chunks.append(paragraph[start:end])

                start += chunk_size - overlap

            continue

        candidate = (
            current_chunk + "\n" + paragraph
            if current_chunk
            else paragraph
        )

        if len(candidate) <= chunk_size:
            current_chunk = candidate

        else:
            if current_chunk:
                chunks.append(current_chunk)

            current_chunk = paragraph

    if current_chunk:
        chunks.append(current_chunk)

    return chunks