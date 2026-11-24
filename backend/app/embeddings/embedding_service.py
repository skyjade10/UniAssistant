_MODEL = None


class EmbeddingService:

    def __init__(self):
        global _MODEL

        if _MODEL is None:
            from sentence_transformers import SentenceTransformer

            _MODEL = SentenceTransformer(
                "all-MiniLM-L6-v2"
            )

        self.model = _MODEL

    def generate_embeddings(self, texts):
        """Convert multiple text chunks into vectors."""

        embeddings = self.model.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=True
        )

        return embeddings

    def generate_embedding(self, text):
        """Convert one text into a vector."""

        embedding = self.model.encode(
            text,
            convert_to_numpy=True,
            normalize_embeddings=True
        )

        return embedding