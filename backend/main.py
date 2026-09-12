import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.config import settings
from backend.schemas import HealthResponse
from backend.services.database import db_service
from backend.services.ingestion import ingestion_service
from backend.routes.chat import router as chat_router
from backend.routes.documents import router as documents_router
from backend.routes.evaluate import router as evaluate_router

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("rag_itgeeks")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up Exam-Night Multimodal RAG Companion...")
    await db_service.connect()
    try:
        ingestion_service.ensure_collection()
    except Exception as e:
        logger.warning(f"Qdrant collection initialization warning: {e}")
    yield
    logger.info("Shutting down...")

app = FastAPI(
    title="The ExamBuddy",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    qdrant_ok = False
    vector_count = 0
    try:
        collections = ingestion_service.qdrant_client.get_collections().collections
        exists = any(c.name == settings.QDRANT_COLLECTION for c in collections)
        if exists:
            info = ingestion_service.qdrant_client.get_collection(collection_name=settings.QDRANT_COLLECTION)
            vector_count = info.points_count or 0
        qdrant_ok = True
    except Exception as e:
        logger.error(f"Qdrant health check error: {e}")

    mongo_ok = await db_service.ping()

    status = "healthy" if (qdrant_ok and mongo_ok) else "degraded"
    return HealthResponse(
        status=status,
        qdrant_connected=qdrant_ok,
        mongo_connected=mongo_ok,
        collection_name=settings.QDRANT_COLLECTION,
        total_vectors=vector_count
    )

app.include_router(chat_router)
app.include_router(documents_router)
app.include_router(evaluate_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
