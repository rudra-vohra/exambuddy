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

    # 1. Extract conversation history
    history = []
    if request.history:
        for m in request.history:
            history.append({
                "role": m.role if hasattr(m, "role") else m.get("role", "user"),
                "content": m.content if hasattr(m, "content") else m.get("content", "")
            })
    elif request.session_id:
        db_history = await db_service.get_session_history(session_id)
        for h in db_history:
            if "query" in h and "answer" in h:
                history.append({"role": "user", "content": h["query"]})
                history.append({"role": "assistant", "content": h["answer"]})

    # 2. Reformulate follow-up query with conversational context
    search_query = query
    if history:
        search_query = await asyncio.to_thread(generator_service.reformulate_query, query, history)

    # 3. Retrieve relevant contexts across documents off the event loop
    chunks = await asyncio.to_thread(retriever_service.retrieve, query=search_query)
    context_str = retriever_service.build_context_string(chunks)

    # 4. Generate grounded answer or refusal off the event loop with conversation context
    result = await asyncio.to_thread(
        generator_service.generate_grounded_answer,
        query=query,
        context_chunks=chunks,
        context_string=context_str,
        chat_history=history
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
