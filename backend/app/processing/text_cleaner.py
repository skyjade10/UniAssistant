
import re

def clean_text(text):
    """Clean extracted document text."""

    # Replace multiple spaces and tabs.
    text = re.sub(r"[ \t]+", " ", text)

    # Replace excessive blank lines.
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Remove whitespace at the beginning and end.
    text = text.strip()

    return text