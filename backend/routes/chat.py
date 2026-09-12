import uuid
import asyncio
from fastapi import APIRouter, HTTPException
from backend.schemas import ChatRequest, ChatResponse, CitationItem
from backend.services.retriever import retriever_service
from backend.services.generator import generator_service
from backend.services.database import db_service

router = APIRouter(prefix="/api/chat", tags=["Chat"])

@router.post("", response_model=ChatResponse)
async def handle_chat(request: ChatRequest):
    session_id = request.session_id or str(uuid.uuid4())
    query = request.query.strip()

    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    # 1. Retrieve relevant contexts across documents off the event loop
    chunks = await asyncio.to_thread(retriever_service.retrieve, query=query)
    context_str = retriever_service.build_context_string(chunks)

    # 2. Generate grounded answer or refusal off the event loop
    result = await asyncio.to_thread(
        generator_service.generate_grounded_answer,
        query=query,
        context_chunks=chunks,
        context_string=context_str
    )

    citations = [
        CitationItem(
            source=c["source"],
            page_number=c["page_number"],
            text_snippet=c.get("text_snippet", "")
        )
        for c in result.get("citations", [])
    ]

    # 3. Save to database
    await db_service.save_session_message(
        session_id=session_id,
        query=query,
        answer=result["answer"],
        citations=[c.dict() for c in citations],
        refusal=result["refusal"]
    )

    return ChatResponse(
        answer=result["answer"],
        citations=citations,
        refusal=result["refusal"],
        session_id=session_id
    )

@router.get("/history/{session_id}")
async def get_history(session_id: str):
    history = await db_service.get_session_history(session_id)
    return {"session_id": session_id, "messages": history}
