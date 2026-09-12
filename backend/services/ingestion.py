import time
import re
import asyncio
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from backend.config import settings
from backend.services.parser import parser_service
from backend.services.database import db_service

logger = logging.getLogger(__name__)

def extract_retry_seconds(error_msg: str, default: float = 30.0) -> float:
    match = re.search(r"retry in (\d+(?:\.\d+)?)s", str(error_msg), re.IGNORECASE)
    if match:
        return float(match.group(1)) + 1.5
    match = re.search(r"seconds:\s*(\d+)", str(error_msg), re.IGNORECASE)
    if match:
        return float(match.group(1)) + 1.5
    return default

class IngestionService:
    def __init__(self):
        self._embeddings = None
        self._vector_store = None
        self._client = None
        self._cached_key = None

    @property
    def embeddings(self):
        current_key = settings.GEMINI_API_KEY
        if self._embeddings is None or self._cached_key != current_key:
            self._embeddings = GoogleGenerativeAIEmbeddings(
                model=settings.EMBEDDING_MODEL,
                google_api_key=current_key
            )
            self._vector_store = None
            self._cached_key = current_key
        return self._embeddings

    @property
    def qdrant_client(self) -> QdrantClient:
        if self._client is None:
            self._client = QdrantClient(url=settings.QDRANT_URL)
        return self._client

    def get_vector_store(self) -> QdrantVectorStore:
        emb = self.embeddings
        if self._vector_store is None:
            self._vector_store = QdrantVectorStore(
                client=self.qdrant_client,
                collection_name=settings.QDRANT_COLLECTION,
                embedding=emb
            )
        return self._vector_store

    def ensure_collection(self):
        try:
            collections = self.qdrant_client.get_collections().collections
            exists = any(c.name == settings.QDRANT_COLLECTION for c in collections)
            if not exists:
                pass
        except Exception as e:
            logger.error(f"Error checking Qdrant collections: {e}")

    async def _add_documents_with_retry(self, vector_store: QdrantVectorStore, batch: List[Any], max_retries: int = 5):
        for attempt in range(max_retries):
            try:
                await asyncio.to_thread(vector_store.add_documents, batch)
                return
            except Exception as e:
                err_str = str(e)
                if any(term in err_str.lower() for term in ["429", "quota", "resourceexhausted", "rate"]):
                    wait_time = extract_retry_seconds(err_str, default=25.0 * (attempt + 1))
                    logger.warning(
                        f"Rate limit reached on batch (attempt {attempt + 1}/{max_retries}). "
                        f"Sleeping {wait_time:.1f}s before retry: {err_str[:200]}"
                    )
                    if attempt < max_retries - 1:
                        await asyncio.sleep(wait_time)
                        continue
                logger.error(f"Error adding batch to vector store: {e}")
                raise

    async def _from_documents_with_retry(self, batch: List[Any], max_retries: int = 5) -> QdrantVectorStore:
        for attempt in range(max_retries):
            try:
                return await asyncio.to_thread(
                    QdrantVectorStore.from_documents,
                    documents=batch,
                    embedding=self.embeddings,
                    url=settings.QDRANT_URL,
                    collection_name=settings.QDRANT_COLLECTION
                )
            except Exception as e:
                err_str = str(e)
                if any(term in err_str.lower() for term in ["429", "quota", "resourceexhausted", "rate"]):
                    wait_time = extract_retry_seconds(err_str, default=25.0 * (attempt + 1))
                    logger.warning(
                        f"Rate limit on initial vector store creation (attempt {attempt + 1}/{max_retries}). "
                        f"Sleeping {wait_time:.1f}s before retry: {err_str[:200]}"
                    )
                    if attempt < max_retries - 1:
                        await asyncio.sleep(wait_time)
                        continue
                raise

    async def ingest_file(self, file_path: Path) -> Dict[str, Any]:
        docs, ocr_count, doc_format = await asyncio.to_thread(parser_service.parse_file, file_path)
        
        # Split documents into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        chunks = text_splitter.split_documents(docs)

        # Ensure all chunk metadata has source and page_label
        for idx, chunk in enumerate(chunks):
            chunk.metadata["chunk_id"] = f"{file_path.name}_{chunk.metadata.get('page_number', 1)}_{idx}"
            if "source" not in chunk.metadata:
                chunk.metadata["source"] = file_path.name
            if "page_label" not in chunk.metadata:
                chunk.metadata["page_label"] = str(chunk.metadata.get("page_number", 1))

        # Check if collection exists
        collections = [c.name for c in self.qdrant_client.get_collections().collections]
        batch_size = 15
        delay = 8

        if settings.QDRANT_COLLECTION not in collections:
            first_batch = chunks[:batch_size]
            vector_store = await self._from_documents_with_retry(first_batch)
            start_idx = batch_size
        else:
            vector_store = self.get_vector_store()
            start_idx = 0

        # Add remaining chunks in throttled batches non-blockingly with rate limit backoff
        for i in range(start_idx, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            await self._add_documents_with_retry(vector_store, batch)
            if i + batch_size < len(chunks):
                await asyncio.sleep(delay)

        # Record document metadata in database
        total_pages = max([d.metadata.get("page_number", 1) for d in docs], default=1)
        await db_service.record_document(
            source=file_path.name,
            doc_format=doc_format,
            total_pages=total_pages,
            chunks_count=len(chunks),
            ocr_applied=ocr_count > 0
        )

        return {
            "source": file_path.name,
            "format": doc_format,
            "total_pages": total_pages,
            "chunks_indexed": len(chunks),
            "ocr_pages": ocr_count
        }

    async def delete_document(self, source: str) -> Dict[str, Any]:
        from qdrant_client.http import models as qmodels
        from backend.services.retriever import retriever_service

        points_deleted = 0
        try:
            # 1. Count points in Qdrant matching metadata.source
            count_filter = qmodels.Filter(
                must=[
                    qmodels.FieldCondition(
                        key="metadata.source",
                        match=qmodels.MatchValue(value=source)
                    )
                ]
            )
            count_res = await asyncio.to_thread(
                self.qdrant_client.count,
                collection_name=settings.QDRANT_COLLECTION,
                count_filter=count_filter
            )
            points_deleted = count_res.count

            # 2. Delete points from Qdrant
            if points_deleted > 0:
                await asyncio.to_thread(
                    self.qdrant_client.delete,
                    collection_name=settings.QDRANT_COLLECTION,
                    points_selector=qmodels.FilterSelector(filter=count_filter)
                )
        except Exception as e:
            logger.error(f"Error deleting vectors from Qdrant for source {source}: {e}")

        # 3. Delete metadata and chunks from MongoDB / local store
        try:
            await db_service.delete_document(source)
        except Exception as e:
            logger.error(f"Error deleting document from database for source {source}: {e}")

        # 4. Remove physical file from uploads or corpus directories
        search_paths = [
            Path(__file__).resolve().parent.parent.parent / "corpus" / "uploads",
            Path(__file__).resolve().parent.parent.parent / "corpus" / "pdf",
            Path(__file__).resolve().parent.parent.parent / "corpus" / "slides",
            Path(__file__).resolve().parent.parent.parent / "corpus" / "markdown",
            Path(__file__).resolve().parent.parent.parent / "corpus" / "handwritten",
            Path(__file__).resolve().parent.parent.parent / "corpus",
        ]
        file_deleted = False
        for folder in search_paths:
            candidate = folder / source
            if candidate.exists() and candidate.is_file():
                try:
                    candidate.unlink()
                    file_deleted = True
                except Exception as e:
                    logger.warning(f"Could not delete physical file {candidate}: {e}")

        # 5. Invalidate retriever query cache
        retriever_service.clear_cache()

        return {
            "source": source,
            "points_deleted": points_deleted,
            "file_deleted": file_deleted,
            "status": "deleted"
        }

ingestion_service = IngestionService()

