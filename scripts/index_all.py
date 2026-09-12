import asyncio
import sys
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from backend.config import settings
from backend.services.ingestion import ingestion_service
from backend.services.database import db_service

async def main():
    print("==================================================")
    print("INDEXING MULTIMODAL COURSE CORPUS INTO QDRANT & MONGO")
    print(f"Collection: {settings.QDRANT_COLLECTION}")
    print(f"Qdrant URL: {settings.QDRANT_URL}")
    print("==================================================")

    # Ensure MongoDB connected
    await db_service.connect()

    files_to_index = [
        BASE_DIR / "corpus" / "pdf" / "dsp_lecture_notes.pdf",
        BASE_DIR / "corpus" / "slides" / "dsp_slides_sampling_quantization.pdf",
        BASE_DIR / "corpus" / "markdown" / "dsp_algorithms_cheatsheet.md",
        BASE_DIR / "corpus" / "handwritten" / "handwritten_bilinear_transform.pdf",
    ]

    total_chunks = 0
    total_ocr = 0

    for file_path in files_to_index:
        if not file_path.exists():
            print(f"Skipping missing file: {file_path}")
            continue

        print(f"\nProcessing {file_path.name}...")
        try:
            res = await ingestion_service.ingest_file(file_path)
            print(f"-> Indexed {file_path.name}: {res['total_pages']} pages, {res['chunks_indexed']} chunks, OCR pages: {res['ocr_pages']}")
            total_chunks += res["chunks_indexed"]
            total_ocr += res["ocr_pages"]
        except Exception as e:
            print(f"-> Error indexing {file_path.name}: {e}")

    print("\n==================================================")
    print(f"INGESTION COMPLETE: {len(files_to_index)} documents, {total_chunks} chunks, {total_ocr} OCR pages.")
    print("==================================================")

if __name__ == "__main__":
    asyncio.run(main())
