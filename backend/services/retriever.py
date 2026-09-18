import logging
import re
from typing import List, Dict, Any, Tuple, Optional
from langchain_qdrant import QdrantVectorStore
from qdrant_client.http import models
from backend.config import settings
from backend.services.ingestion import ingestion_service

logger = logging.getLogger(__name__)

class RetrieverService:
    def __init__(self):
        self._query_cache: Dict[str, List[Dict[str, Any]]] = {}

    def extract_target_source(self, query: str) -> Optional[str]:
        # Match filenames with extensions e.g. test_text.pdf, slides.pdf, notes.png, doc.md
        matches = re.findall(r'[\w\-\.]+\.(?:pdf|png|jpg|jpeg|webp|md|txt|pptx|ppt)', query, re.IGNORECASE)
        if matches:
            return matches[0].strip('[]() ')
        return None

    def retrieve(self, query: str, top_k: int = None) -> List[Dict[str, Any]]:
        k = top_k or settings.TOP_K
        target_source = self.extract_target_source(query)

        # For document overview / topic queries, expand k to ensure comprehensive topic coverage
        if target_source and any(w in query.lower() for w in ['topic', 'cover', 'chapter', 'syllabus', 'about', 'overview', 'content']):
            k = max(k, 8)

        cache_key = f"{query.strip().lower()}_{k}_{target_source or 'all'}"
        if cache_key in self._query_cache:
            return self._query_cache[cache_key]

        vector_store = ingestion_service.get_vector_store()
        results_with_score = []

        # If a specific document source is detected, search strictly within that document
        filter_condition = None
        if target_source:
            filter_condition = models.Filter(
                must=[models.FieldCondition(key="metadata.source", match=models.MatchValue(value=target_source))]
            )

        for attempt in range(3):
            try:
                if filter_condition:
                    results_with_score = vector_store.similarity_search_with_score(query=query, k=k, filter=filter_condition)
                    # If filtered search returned nothing (e.g. filename slight mismatch), fallback to unfiltered
                    if not results_with_score:
                        results_with_score = vector_store.similarity_search_with_score(query=query, k=k)
                else:
                    results_with_score = vector_store.similarity_search_with_score(query=query, k=k)
                break
            except Exception as e:
                logger.warning(f"Qdrant retrieve attempt {attempt + 1} failed: {e}")
                if attempt < 2:
                    import time
                    time.sleep(0.5 * (attempt + 1))
                else:
                    return []

        retrieved = []
        for doc, score in results_with_score:
            page_num = doc.metadata.get("page_number")
            if page_num is None:
                # Try page_label or page
                raw_page = doc.metadata.get("page_label", doc.metadata.get("page", 1))
                try:
                    page_num = int(raw_page)
                except (ValueError, TypeError):
                    page_num = 1

            source = doc.metadata.get("source", "unknown_document")
            retrieved.append({
                "content": doc.page_content,
                "source": source,
                "page_number": int(page_num),
                "score": float(score),
                "ocr": doc.metadata.get("ocr", False),
                "format": doc.metadata.get("format", "unknown")
            })

        if len(self._query_cache) > 200:
            self._query_cache.clear()
        self._query_cache[cache_key] = retrieved

        return retrieved

    def clear_cache(self):
        self._query_cache.clear()

    def build_context_string(self, chunks: List[Dict[str, Any]]) -> str:
        formatted_chunks = []
        for idx, chunk in enumerate(chunks, 1):
            formatted_chunks.append(
                f"--- [EXCERPT {idx}] ---\n"
                f"Source Document: {chunk['source']}\n"
                f"Page Number: {chunk['page_number']}\n"
                f"Content:\n{chunk['content']}"
            )
        return "\n\n".join(formatted_chunks)

retriever_service = RetrieverService()
