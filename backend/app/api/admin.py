from functools import lru_cache

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
    status
)

from app.admin.service import DocumentService
from app.admin.auth import require_admin

import logging

logger = logging.getLogger(__name__)


router = APIRouter(
    prefix="/api/admin",
    tags=["Admin"],
    dependencies=[Depends(require_admin)]
)

MAX_FILE_SIZE = 15 * 1024 * 1024


@lru_cache
def get_document_service():
    return DocumentService()



@router.get("/dashboard")
def dashboard():
    try:
        service = get_document_service()

        return {
            "status": "success",
            "statistics": service.get_statistics()
        }

    except Exception:
        logger.exception("Dashboard statistics failed")

        raise HTTPException(
            status_code=500,
            detail="Unable to load dashboard statistics."
        )



@router.get("/documents")
def list_documents():
    try:
        service = get_document_service()

        return {
            "status": "success",
            "documents": service.get_documents()
        }

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve documents."
        )


@router.post("/documents/upload", status_code=status.HTTP_201_CREATED)
async def upload_document(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="A filename is required."
        )

    try:
        file_bytes = await file.read(MAX_FILE_SIZE + 1)

        if len(file_bytes) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail="File exceeds the 15 MB upload limit."
            )

        service = get_document_service()

        result = service.upload_document(
            filename=file.filename,
            file_bytes=file_bytes
        )

        return {
            "status": "success",
            "message": "Document uploaded successfully.",
            "document": result
        }

    except HTTPException:
        raise

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Unable to upload the document."
        )

    finally:
        await file.close()


@router.delete("/documents/{document_id}")
def delete_document(document_id: str):
    try:
        service = get_document_service()

        result = service.delete_document(document_id)

        if not result:
            raise HTTPException(
                status_code=404,
                detail="Document not found."
            )

        return {
            "status": "success",
            "message": "Document deleted successfully."
        }

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Unable to delete the document."
        )


@router.get("/sources")
def list_sources():
    try:
        service = get_document_service()

        return {
            "status": "success",
            "sources": service.get_sources()
        }

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve sources."
        )


@router.delete("/sources")
def delete_source(source_url: str):
    try:
        service = get_document_service()

        result = service.delete_source(source_url)

        if not result:
            raise HTTPException(
                status_code=404,
                detail="Source not found."
            )

        return {
            "status": "success",
            "message": "Source deleted successfully."
        }

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Unable to delete the source."
        )
