import time
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

class IngestionService:
    def __init__(self):
        self._embeddings = None
        self._vector_store = None
        self._client = None

    @property
    def embeddings(self):
        if self._embeddings is None:
            self._embeddings = GoogleGenerativeAIEmbeddings(
                model=settings.EMBEDDING_MODEL,
                google_api_key=settings.GEMINI_API_KEY
            )
        return self._embeddings

    @property
    def qdrant_client(self) -> QdrantClient:
        if self._client is None:
            self._client = QdrantClient(url=settings.QDRANT_URL)
        return self._client

    def get_vector_store(self) -> QdrantVectorStore:
        if self._vector_store is None:
            self._vector_store = QdrantVectorStore(
                client=self.qdrant_client,
                collection_name=settings.QDRANT_COLLECTION,
                embedding=self.embeddings
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
        batch_size = settings.BATCH_SIZE
        delay = min(settings.DELAY_SECONDS, 3)

        if settings.QDRANT_COLLECTION not in collections:
            first_batch = chunks[:batch_size]
            vector_store = await asyncio.to_thread(
                QdrantVectorStore.from_documents,
                documents=first_batch,
                embedding=self.embeddings,
                url=settings.QDRANT_URL,
                collection_name=settings.QDRANT_COLLECTION
            )
            start_idx = batch_size
        else:
            vector_store = self.get_vector_store()
            start_idx = 0

        # Add remaining chunks in throttled batches non-blockingly
        for i in range(start_idx, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            await asyncio.to_thread(vector_store.add_documents, batch)
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

ingestion_service = IngestionService()
