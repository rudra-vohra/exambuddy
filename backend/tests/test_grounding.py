import pytest
from backend.services.retriever import retriever_service
from backend.services.generator import generator_service, EXACT_REFUSAL_MESSAGE

def test_grounded_answer_generation():
    query = "State the symmetry and periodicity properties of the DTFT."
    chunks = retriever_service.retrieve(query=query, top_k=4)
    ctx_str = retriever_service.build_context_string(chunks)
    res = generator_service.generate_grounded_answer(query, chunks, ctx_str)

    assert res["refusal"] is False
    assert len(res["citations"]) > 0
    assert any(c["source"] == "dsp_lecture_notes.pdf" for c in res["citations"])
    assert any(c["page_number"] == 4 for c in res["citations"])
    # Zero emoji check
    assert not any(ord(char) > 127900 for char in res["answer"])

def test_strict_refusal_out_of_corpus():
    query = "What is the Kalman filter state estimation equation for linear dynamical systems?"
    chunks = retriever_service.retrieve(query=query, top_k=4)
    ctx_str = retriever_service.build_context_string(chunks)
    res = generator_service.generate_grounded_answer(query, chunks, ctx_str)

    assert res["refusal"] is True
    assert res["answer"] == EXACT_REFUSAL_MESSAGE
    assert len(res["citations"]) == 0
