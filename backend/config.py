from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    GEMINI_API_KEY: str = Field(default="")
    QDRANT_URL: str = Field(default="http://localhost:6333")
    QDRANT_COLLECTION: str = Field(default="rag_itgeeks")
    MONGO_URI: str = Field(default="mongodb://localhost:27017")
    MONGO_DB_NAME: str = Field(default="itgeeks_rag")
    OCR_MODEL: str = Field(default="gemini-3.5-flash-lite")
    GENERATION_MODEL: str = Field(default="gemini-3.5-flash-lite")
    EMBEDDING_MODEL: str = Field(default="models/gemini-embedding-2")
    CHUNK_SIZE: int = Field(default=1000)
    CHUNK_OVERLAP: int = Field(default=400)
    MIN_CHARS_THRESHOLD: int = Field(default=20)
    DPI_SCALE: float = Field(default=2.0)
    BATCH_SIZE: int = Field(default=20)
    DELAY_SECONDS: int = Field(default=15)
    SIMILARITY_SCORE_THRESHOLD: float = Field(default=0.45)
    TOP_K: int = Field(default=6)

    model_config = SettingsConfigDict(
        env_file=(BASE_DIR / ".env", BASE_DIR / "rag" / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
