import json
import os
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from backend.config import settings

logger = logging.getLogger(__name__)

LOCAL_STORAGE_DIR = Path(__file__).resolve().parent.parent / "data"
LOCAL_STORAGE_DIR.mkdir(parents=True, exist_ok=True)
LOCAL_STORE_FILE = LOCAL_STORAGE_DIR / "fallback_store.json"

class DatabaseService:
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.db = None
        self.is_connected = False
        self._init_local_store()

    def _init_local_store(self):
        if not LOCAL_STORE_FILE.exists():
            initial_data = {
                "chat_sessions": [],
                "documents": [],
                "evaluation_runs": []
            }
            with open(LOCAL_STORE_FILE, "w", encoding="utf-8") as f:
                json.dump(initial_data, f, indent=2)

    def _read_local_store(self) -> Dict[str, Any]:
        try:
            with open(LOCAL_STORE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {"chat_sessions": [], "documents": [], "evaluation_runs": []}

    def _write_local_store(self, data: Dict[str, Any]):
        with open(LOCAL_STORE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=str)

    async def connect(self):
        try:
            self.client = AsyncIOMotorClient(settings.MONGO_URI, serverSelectionTimeoutMS=2000)
            # Trigger quick server ping
            await self.client.admin.command('ping')
            self.db = self.client[settings.MONGO_DB_NAME]
            self.is_connected = True
        except (ConnectionFailure, ServerSelectionTimeoutError, Exception):
            self.is_connected = False
            self.db = None

    async def ping(self) -> bool:
        if not self.client:
            await self.connect()
        try:
            if self.client:
                await self.client.admin.command('ping')
                self.is_connected = True
                return True
        except Exception:
            self.is_connected = False
        return False

    async def save_session_message(self, session_id: str, query: str, answer: str, citations: List[Dict[str, Any]], refusal: bool):
        entry = {
            "session_id": session_id,
            "query": query,
            "answer": answer,
            "citations": citations,
            "refusal": refusal,
            "timestamp": datetime.utcnow().isoformat()
        }
        if self.is_connected and self.db is not None:
            try:
                await self.db.chat_sessions.insert_one(entry)
                return
            except Exception:
                pass
        
        # Local fallback
        data = self._read_local_store()
        data["chat_sessions"].append(entry)
        self._write_local_store(data)

    async def get_session_history(self, session_id: str) -> List[Dict[str, Any]]:
        if self.is_connected and self.db is not None:
            try:
                cursor = self.db.chat_sessions.find({"session_id": session_id}).sort("timestamp", 1)
                items = await cursor.to_list(length=100)
                for item in items:
                    item.pop("_id", None)
                return items
            except Exception:
                pass
        
        data = self._read_local_store()
        return [s for s in data.get("chat_sessions", []) if s.get("session_id") == session_id]

    async def record_document(self, source: str, doc_format: str, total_pages: int, chunks_count: int, ocr_applied: bool):
        doc_entry = {
            "source": source,
            "format": doc_format,
            "total_pages": total_pages,
            "chunks_count": chunks_count,
            "ocr_applied": ocr_applied,
            "created_at": datetime.utcnow().isoformat()
        }
        if not self.is_connected or self.db is None:
            await self.connect()

        if self.is_connected and self.db is not None:
            try:
                await self.db.documents.update_one(
                    {"source": source},
                    {"$set": doc_entry},
                    upsert=True
                )
            except Exception as e:
                logger.error(f"MongoDB record_document error: {e}")

        data = self._read_local_store()
        docs = [d for d in data.get("documents", []) if d.get("source") != source]
        docs.append(doc_entry)
        data["documents"] = docs
        self._write_local_store(data)

    async def list_documents(self) -> List[Dict[str, Any]]:
        if not self.is_connected or self.db is None:
            await self.connect()

        if self.is_connected and self.db is not None:
            try:
                cursor = self.db.documents.find({}).sort("created_at", -1)
                items = await cursor.to_list(length=100)
                for item in items:
                    item.pop("_id", None)
                if items:
                    return items
            except Exception as e:
                logger.error(f"MongoDB list_documents error: {e}")

        data = self._read_local_store()
        return data.get("documents", [])

    async def delete_document(self, source: str) -> bool:
        if self.is_connected and self.db is not None:
            try:
                await self.db.documents.delete_many({"source": source})
                await self.db.chunks.delete_many({"source": source})
            except Exception:
                pass

        data = self._read_local_store()
        data["documents"] = [d for d in data.get("documents", []) if d.get("source") != source]
        self._write_local_store(data)
        return True

    async def save_evaluation_run(self, run_id: str, summary: Dict[str, Any], details: List[Dict[str, Any]]):
        run_entry = {
            "run_id": run_id,
            "timestamp": datetime.utcnow().isoformat(),
            "summary": summary,
            "details": details
        }
        if self.is_connected and self.db is not None:
            try:
                await self.db.evaluation_runs.insert_one(run_entry)
                return
            except Exception:
                pass

        data = self._read_local_store()
        data["evaluation_runs"].append(run_entry)
        self._write_local_store(data)

    async def get_latest_evaluation_run(self) -> Optional[Dict[str, Any]]:
        if self.is_connected and self.db is not None:
            try:
                run = await self.db.evaluation_runs.find_one({}, sort=[("timestamp", -1)])
                if run:
                    run.pop("_id", None)
                    return run
            except Exception:
                pass

        data = self._read_local_store()
        runs = data.get("evaluation_runs", [])
        return runs[-1] if runs else None

db_service = DatabaseService()
