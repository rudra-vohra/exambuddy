import os
import shutil
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from backend.schemas import DocumentListResponse, DocumentMetadata, IngestResponse, PagePreviewResponse
from backend.services.database import db_service
from backend.services.ingestion import ingestion_service
from backend.services.retriever import retriever_service
from backend.services.parser import parser_service

router = APIRouter(prefix="/api/documents", tags=["Documents"])

UPLOAD_DIR = Path(__file__).resolve().parent.parent.parent / "corpus" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@router.get("", response_model=DocumentListResponse)
async def list_documents():
    docs_data = await db_service.list_documents()
    docs = [
        DocumentMetadata(
            source=d.get("source", "unknown"),
            format=d.get("format", "unknown"),
            total_pages=d.get("total_pages", 1),
            chunks_count=d.get("chunks_count", 0),
            ocr_applied=d.get("ocr_applied", False),
            created_at=d.get("created_at", "")
        )
        for d in docs_data
    ]
    return DocumentListResponse(documents=docs)

@router.post("/upload", response_model=IngestResponse)
async def upload_document(file: UploadFile = File(...)):
    allowed_extensions = {".pdf", ".md", ".txt", ".png", ".jpg", ".jpeg"}
    suffix = Path(file.filename).suffix.lower()
    if suffix not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{suffix}'. Allowed: {', '.join(allowed_extensions)}"
        )

    file_path = UPLOAD_DIR / file.filename
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")

    try:
        result = await ingestion_service.ingest_file(file_path)
        retriever_service.clear_cache()
        return IngestResponse(
            status="success",
            source=result["source"],
            pages_indexed=result["total_pages"],
            chunks_indexed=result["chunks_indexed"],
            ocr_pages=result["ocr_pages"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")

@router.delete("/{source}")
async def delete_document(source: str):
    source = source.strip()
    if not source:
        raise HTTPException(status_code=400, detail="Source document name required.")

    try:
        res = await ingestion_service.delete_document(source)
        return {
            "status": "success",
            "message": f"Document '{source}' deleted successfully from vector database, MongoDB, and storage.",
            "details": res
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete document: {str(e)}")


@router.get("/page-preview", response_model=PagePreviewResponse)
async def get_page_preview(
    source: str = Query(..., description="Document source name"),
    page: int = Query(1, ge=1, description="Page number")
):
    # Search for source in corpus directories or uploads
    search_paths = [
        Path(__file__).resolve().parent.parent.parent / "corpus",
        Path(__file__).resolve().parent.parent.parent / "corpus" / "uploads",
        Path(__file__).resolve().parent.parent.parent / "corpus" / "pdf",
        Path(__file__).resolve().parent.parent.parent / "corpus" / "slides",
        Path(__file__).resolve().parent.parent.parent / "corpus" / "markdown",
        Path(__file__).resolve().parent.parent.parent / "corpus" / "handwritten",
        Path(__file__).resolve().parent.parent.parent / "rag",
    ]

    target_file = None
    for p in search_paths:
        cand = p / source
        if cand.exists() and cand.is_file():
            target_file = cand
            break

    if not target_file:
        return PagePreviewResponse(
            source=source,
            page=page,
            content=f"Document '{source}' preview not found on filesystem.",
            is_ocr=False
        )

    ext = target_file.suffix.lower()
    if ext == ".pdf":
        import pymupdf
        doc = pymupdf.open(target_file)
        if page > len(doc):
            doc.close()
            return PagePreviewResponse(source=source, page=page, content="Page out of bounds.", is_ocr=False)
        
        pdf_page = doc[page - 1]
        text = pdf_page.get_text().strip()
        doc.close()

        # Always render the PDF page to high-resolution image base64 for direct visual verification
        img_b64 = parser_service.render_pdf_page_to_base64(target_file, page - 1)
        is_ocr = False
        if len(text) < 20:
            is_ocr = True
            text = parser_service.transcribe_image_b64(img_b64)

        return PagePreviewResponse(
            source=source,
            page=page,
            content=text,
            is_ocr=is_ocr,
            image_base64=img_b64
        )

    elif ext in [".png", ".jpg", ".jpeg"]:
        import base64
        b64 = base64.b64encode(target_file.read_bytes()).decode("utf-8")
        text = parser_service.transcribe_image_b64(b64)
        return PagePreviewResponse(
            source=source,
            page=page,
            content=text,
            is_ocr=True,
            image_base64=b64
        )

    elif ext in [".md", ".txt"]:
        content = target_file.read_text(encoding="utf-8")
        sections = content.split("\n---") if "\n---" in content else [content]
        sec_text = sections[page - 1] if page <= len(sections) else content
        return PagePreviewResponse(
            source=source,
            page=page,
            content=sec_text.strip(),
            is_ocr=False
        )

    return PagePreviewResponse(
        source=source,
        page=page,
        content="Unsupported preview format",
        is_ocr=False
    )
