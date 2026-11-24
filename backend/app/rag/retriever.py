import re
import math
import time
import logging

from collections import Counter

from app.rag.query_expander import expand_query

logger = logging.getLogger(__name__)

class Retriever:

    def __init__(self):
        self._embedding_service = None
        self._store = None

        self.stop_words = {
            "the", "is", "are", "a", "an",
            "of", "in", "on", "to", "for",
            "what", "which", "who", "how",
            "does", "do", "list", "give",
            "me", "please", "and", "by",
            "offered", "provide", "show", "zut"
        }

    @property
    def embedding_service(self):
        if self._embedding_service is None:
            from app.embeddings.embedding_service import EmbeddingService

            self._embedding_service = EmbeddingService()
        return self._embedding_service

    @property
    def store(self):
        if self._store is None:
            from app.vectorstore.chroma_store import ChromaStore

            self._store = ChromaStore()
        return self._store

    # ----------------------------------
    # TOKENIZATION
    # ----------------------------------

    def tokenize(self, text):
        return re.findall(
            r"\b[a-zA-Z0-9]+\b",
            text.lower()
        )

    def filter_query_words(self, question):
        return [
            word
            for word in self.tokenize(question)
            if word not in self.stop_words
        ]

    # ----------------------------------
    # SEMANTIC RETRIEVAL
    # ----------------------------------

    def semantic_retrieve(self, question, top_k=10, question_embedding=None):

        if question_embedding is None:
            embedding_start = time.perf_counter()
            question_embedding = self.embedding_service.generate_embedding(question)
            logger.info("RAG_TIMING component=embedding_generation elapsed_ms=%.2f", (time.perf_counter() - embedding_start) * 1000)

        results = self.store.search(
            question_embedding,
            top_k=top_k
        )

        retrieved = []

        for doc_id, document, metadata, distance in zip(
            results["ids"][0],
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0]
        ):

            retrieved.append({
                "id": doc_id,
                "content": document,
                "metadata": metadata or {},
                "distance": float(distance)
            })

        return retrieved

    # ----------------------------------
    # KEYWORD RETRIEVAL - BM25
    # ----------------------------------

    def keyword_retrieve(self, question, top_k=10):

        results = self.store.get_all_documents()

        documents = results["documents"]
        metadatas = results["metadatas"]
        ids = results["ids"]

        query_words = self.filter_query_words(question)

        if not query_words or not documents:
            return []

        query_terms = set(query_words)

        tokenized_documents = [
            self.tokenize(document)
            for document in documents
        ]

        document_count = len(documents)

        document_lengths = [
            len(tokens)
            for tokens in tokenized_documents
        ]

        average_length = (
            sum(document_lengths) / document_count
            if document_count else 0
        )

        # Calculate how many documents contain each term.
        document_frequency = Counter()

        for tokens in tokenized_documents:
            for word in set(tokens):
                document_frequency[word] += 1

        # Extract useful phrases from the question.
        phrases = []

        for size in range(2, min(5, len(query_words) + 1)):

            for i in range(len(query_words) - size + 1):

                phrase = " ".join(
                    query_words[i:i + size]
                )

                phrases.append(phrase)

        matches = []

        k1 = 1.5
        b = 0.75

        for doc_id, document, metadata, tokens, doc_length in zip(
            ids,
            documents,
            metadatas,
            tokenized_documents,
            document_lengths
        ):

            frequencies = Counter(tokens)

            score = 0.0

            # BM25 scoring
            for term in query_terms:

                term_frequency = frequencies[term]

                if term_frequency == 0:
                    continue

                df = document_frequency[term]

                idf = math.log(
                    1 + (
                        document_count - df + 0.5
                    ) / (
                        df + 0.5
                    )
                )

                denominator = term_frequency + k1 * (
                    1 - b + b * (
                        doc_length / average_length
                    )
                ) if average_length else 1

                score += idf * (
                    term_frequency * (k1 + 1)
                ) / denominator

            # Reward exact phrases from the user's question.
            text = document.lower()

            for phrase in phrases:

                if phrase in text:
                    score += 2.0

            # Small boost when the document title matches
            # the question's important terms.
            metadata = metadata or {}

            title = metadata.get("title", "").lower()

            title_words = set(self.tokenize(title))

            title_matches = query_terms.intersection(
                title_words
            )

            score += len(title_matches) * 0.5

            if score <= 0:
                continue

            matches.append({
                "id": doc_id,
                "content": document,
                "metadata": metadata,
                "keyword_score": score
            })

        matches.sort(
            key=lambda item: item["keyword_score"],
            reverse=True
        )

        return matches[:top_k]

    # ----------------------------------
    # RECIPROCAL RANK FUSION
    # ----------------------------------

    def reciprocal_rank_fusion(
        self,
        semantic_results,
        keyword_results,
        top_k=5,
        k=60
    ):

        fused = {}

        result_lists = [
            (semantic_results, 1.0),
            (keyword_results, 2.0)
        ]

        for result_list, weight in result_lists:

            for rank, result in enumerate(
                result_list,
                start=1
            ):

                doc_id = result["id"]

                if doc_id not in fused:

                    fused[doc_id] = {
                        **result,
                        "rrf_score": 0.0
                    }

                fused[doc_id]["rrf_score"] += (
                    weight / (k + rank)
                )

                # Preserve keyword score if the same document
                # also appeared in semantic results.
                if "keyword_score" in result:
                    fused[doc_id]["keyword_score"] = (
                        result["keyword_score"]
                    )

                if "distance" in result:
                    fused[doc_id]["distance"] = (
                        result["distance"]
                    )

        ranked_results = sorted(
            fused.values(),
            key=lambda item: item["rrf_score"],
            reverse=True
        )

        return ranked_results[:top_k]

    # ----------------------------------
    # MAIN RETRIEVAL
    # ----------------------------------

    def retrieve(self, question, top_k=5):

        query_start = time.perf_counter()
        expanded_question = expand_query(question)
        logger.info("RAG_TIMING component=query_processing elapsed_ms=%.2f", (time.perf_counter() - query_start) * 1000)

        embedding_start = time.perf_counter()
        question_embedding = self.embedding_service.generate_embedding(expanded_question)
        logger.info("RAG_TIMING component=embedding_generation elapsed_ms=%.2f", (time.perf_counter() - embedding_start) * 1000)

        retrieval_start = time.perf_counter()
        semantic_results = self.semantic_retrieve(
            expanded_question,
            top_k=6,
            question_embedding=question_embedding
        )

        keyword_results = self.keyword_retrieve(
            expanded_question,
            top_k=6
        )

        results = self.reciprocal_rank_fusion(
            semantic_results,
            keyword_results,
            top_k=top_k
        )
        logger.info("RAG_TIMING component=retrieval elapsed_ms=%.2f", (time.perf_counter() - retrieval_start) * 1000)

        return results

    
    def debug_retrieval(self, question):

        expanded_question = expand_query(question)

        print("\nORIGINAL QUERY:")
        print(question)

        print("\nEXPANDED QUERY:")
        print(expanded_question)

        semantic = self.semantic_retrieve(
            expanded_question,
            top_k=10
        )

        keyword = self.keyword_retrieve(
            expanded_question,
            top_k=10
        )

        print("\n========== SEMANTIC RESULTS ==========")

        for rank, item in enumerate(semantic, start=1):
            print(
                rank,
                item["metadata"].get("title"),
                item.get("distance")
            )

        print("\n========== KEYWORD RESULTS ==========")

        for rank, item in enumerate(keyword, start=1):
            print(
                rank,
                item["metadata"].get("title"),
                item.get("keyword_score")
            )

        print("\n========== HYBRID RESULTS ==========")

        hybrid = self.reciprocal_rank_fusion(
            semantic,
            keyword,
            top_k=10
        )

        for rank, item in enumerate(hybrid, start=1):
            print(
                rank,
                item["metadata"].get("title"),
                item.get("rrf_score")
            )