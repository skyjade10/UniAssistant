import json
import uuid

from pathlib import Path
from datetime import datetime, timezone
from io import BytesIO

from docx import Document as WordDocument

from app.ingestion.pdf_loader import load_pdf_bytes
from app.processing.text_cleaner import clean_text
from app.processing.text_splitter import split_text

from app.embeddings.embedding_service import EmbeddingService
from app.vectorstore.chroma_store import ChromaStore


# ==========================================
# STORAGE CONFIGURATION
# ==========================================

STORAGE_DIR = Path("storage")
UPLOAD_DIR = STORAGE_DIR / "uploads"
REGISTRY_FILE = STORAGE_DIR / "documents" / "registry.json"

MAX_FILE_SIZE = 15 * 1024 * 1024

ALLOWED_EXTENSIONS = {
    ".pdf",
    ".txt",
    ".docx"
}


class DocumentService:

    def __init__(self):

        UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        REGISTRY_FILE.parent.mkdir(parents=True, exist_ok=True)

        self.embedding_service = EmbeddingService()
        self.store = ChromaStore()

        if not REGISTRY_FILE.exists():
            self._save_registry([])

    # ======================================
    # DOCUMENT REGISTRY
    # ======================================

    def _load_registry(self):

        try:
            with REGISTRY_FILE.open("r", encoding="utf-8") as file:
                documents = json.load(file)

            if not isinstance(documents, list):
                raise RuntimeError("Invalid document registry format.")

            return documents

        except (json.JSONDecodeError, OSError) as error:
            raise RuntimeError(
                "Could not read the document registry."
            ) from error

    def _save_registry(self, documents):

        temporary_file = REGISTRY_FILE.with_suffix(".tmp")

        with temporary_file.open("w", encoding="utf-8") as file:
            json.dump(
                documents,
                file,
                indent=4,
                ensure_ascii=False
            )

        temporary_file.replace(REGISTRY_FILE)

    # ======================================
    # TEXT EXTRACTION
    # ======================================

    def _extract_text(self, filename, file_bytes):

        extension = Path(filename).suffix.lower()

        if extension == ".pdf":
            return load_pdf_bytes(
                file_bytes,
                filename
            )

        if extension == ".txt":

            try:
                text = file_bytes.decode("utf-8-sig")

            except UnicodeDecodeError as error:
                raise ValueError(
                    "TXT files must use UTF-8 encoding."
                ) from error

            return [{
                "content": text,
                "metadata": {
                    "title": filename,
                    "source_type": "txt",
                    "source_url": None,
                    "page_number": None
                }
            }]

        if extension == ".docx":
            try:
                document = WordDocument(BytesIO(file_bytes))

                paragraphs = [
                    paragraph.text
                    for paragraph in document.paragraphs
                    if paragraph.text.strip()
                ]

                # Extract table contents.
                for table in document.tables:
                    for row in table.rows:
                        paragraphs.append(
                            " | ".join(
                                cell.text.strip()
                                for cell in row.cells
                            )
                        )

                text = "\n".join(paragraphs)

            except Exception as error:
                raise ValueError(
                    "Could not process DOCX file."
                ) from error

            return [{
                "content": text,
                "metadata": {
                    "title": filename,
                    "source_type": "docx",
                    "source_url": None,
                    "page_number": None
                }
            }]

        raise ValueError("Unsupported document format.")

    # ======================================
    # UPLOAD AND INDEX DOCUMENT
    # ======================================

    def upload_document(self, filename, file_bytes):

        extension = Path(filename).suffix.lower()

        if extension not in ALLOWED_EXTENSIONS:
            raise ValueError(
                "Only PDF, TXT and DOCX files are supported."
            )

        if not file_bytes:
            raise ValueError("The uploaded file is empty.")

        if len(file_bytes) > MAX_FILE_SIZE:
            raise ValueError(
                "File exceeds the 15 MB upload limit."
            )

        if extension == ".pdf" and not file_bytes.startswith(b"%PDF-"):
            raise ValueError("Invalid PDF file.")

        document_id = str(uuid.uuid4())

        safe_filename = Path(filename).name

        saved_filename = f"{document_id}{extension}"

        saved_path = UPLOAD_DIR / saved_filename

        # ==================================
        # EXTRACT CONTENT
        # ==================================

        extracted_documents = self._extract_text(
            safe_filename,
            file_bytes
        )

        chunks = []
        metadatas = []

        for extracted in extracted_documents:

            cleaned_text = clean_text(
                extracted["content"]
            )

            if not cleaned_text.strip():
                continue

            document_chunks = split_text(cleaned_text)

            for chunk_index, chunk in enumerate(document_chunks):

                chunks.append(chunk)

                metadata = dict(extracted["metadata"])

                metadata.update({
                    "document_id": document_id,
                    "filename": safe_filename,
                    "chunk_index": chunk_index
                })

                metadatas.append(metadata)

        if not chunks:
            raise ValueError(
                "No readable text was found in the document."
            )

        # ==================================
        # GENERATE EMBEDDINGS
        # ==================================

        embeddings = self.embedding_service.generate_embeddings(
            chunks
        )

        # ==================================
        # SAVE AND INDEX
        # ==================================

        document_record = {
            "document_id": document_id,
            "filename": safe_filename,
            "stored_filename": saved_filename,
            "file_type": extension.replace(".", ""),
            "file_size": len(file_bytes),
            "chunks": len(chunks),
            "status": "indexed",
            "uploaded_at": datetime.now(
                timezone.utc
            ).isoformat()
        }

        try:

            # Save original file.
            saved_path.write_bytes(file_bytes)

            # Add chunks to ChromaDB.
            self.store.add_documents(
                chunks,
                embeddings,
                metadatas
            )

            # Register the document.
            registry = self._load_registry()
            registry.append(document_record)

            self._save_registry(registry)

        except Exception:

            # Remove any chunks that may have been inserted,
            # even if add_documents() failed partway through.
            try:
                self.store.delete_document(document_id)
            except Exception:
                pass

            # Remove the original file.
            if saved_path.exists():
                saved_path.unlink()

            raise

        return document_record

    # ======================================
    # LIST DOCUMENTS
    # ======================================

    def get_documents(self):

        return self._load_registry()

    # ======================================
    # GET SINGLE DOCUMENT
    # ======================================

    def get_document(self, document_id):

        registry = self._load_registry()

        for document in registry:

            if document["document_id"] == document_id:
                return document

        return None

    # ======================================
    # DELETE DOCUMENT
    # ======================================

    def delete_document(self, document_id):

        registry = self._load_registry()

        document = next(
            (
                item for item in registry
                if item["document_id"] == document_id
            ),
            None
        )

        if document is None:
            return False

        # Prepare updated registry first.
        updated_registry = [
            item for item in registry
            if item["document_id"] != document_id
        ]

        # Save registry before deleting physical data.
        # If saving fails, the original document remains intact.
        self._save_registry(updated_registry)

        try:

            self.store.delete_document(document_id)

            saved_path = UPLOAD_DIR / document["stored_filename"]

            if saved_path.exists():
                saved_path.unlink()

        except Exception:

            # Restore registry if deletion fails.
            self._save_registry(registry)

            raise

        return True

    # ======================================
    # DELETE SOURCE
    # ======================================

    def delete_source(self, source_url):

        if not source_url:
            return False

        source_file = Path("storage/documents/documents.jsonl")
        removed_source_records = 0

        if source_file.exists():
            try:
                records = []

                with source_file.open("r", encoding="utf-8") as file:
                    for line in file:
                        if not line.strip():
                            continue

                        record = json.loads(line)
                        metadata = record.get("metadata") or {}

                        if metadata.get("source_url") == source_url:
                            removed_source_records += 1
                        else:
                            records.append(record)

                temporary_file = source_file.with_suffix(".tmp")

                with temporary_file.open("w", encoding="utf-8") as file:
                    for record in records:
                        file.write(
                            json.dumps(record, ensure_ascii=False) + "\n"
                        )

                temporary_file.replace(source_file)

            except (json.JSONDecodeError, OSError):
                raise RuntimeError("Could not update the source registry.")

        deleted_chunks = self.store.delete_source(source_url)

        return removed_source_records > 0 or deleted_chunks > 0

    # ======================================
    # DASHBOARD STATISTICS
    # ======================================

    def get_statistics(self):

        documents = self.get_documents()

        total_chunks = self.store.count()

        indexed_documents = sum(
            1
            for document in documents
            if document.get("status") == "indexed"
        )

        return {
            "total_documents": len(documents),
            "total_chunks": total_chunks,
            "indexed_documents": indexed_documents,
            "storage_directory": str(STORAGE_DIR)
        }

    # ======================================
    # SOURCE URLS
    # ======================================

    def get_sources(self):

        source_urls = self.store.get_source_urls()

        return [
            {"source_url": source_url}
            for source_url in source_urls
        ]
