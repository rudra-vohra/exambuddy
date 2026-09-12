import pytest
from backend.services.retriever import retriever_service

def test_retriever_in_corpus():
    query = "What is the condition for an LTI system to be BIBO stable?"
    chunks = retriever_service.retrieve(query=query, top_k=4)
    assert len(chunks) > 0
    top_chunk = chunks[0]
    assert "source" in top_chunk
    assert "page_number" in top_chunk
    assert "content" in top_chunk
    assert top_chunk["page_number"] >= 1

def test_build_context_string():
    dummy_chunks = [
        {"source": "doc1.pdf", "page_number": 3, "content": "Sample content text"}
    ]
    ctx = retriever_service.build_context_string(dummy_chunks)
    assert "Source Document: doc1.pdf" in ctx
    assert "Page Number: 3" in ctx
    assert "Sample content text" in ctx
