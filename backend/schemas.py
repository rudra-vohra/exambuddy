from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field

class CitationItem(BaseModel):
    source: str = Field(..., description="Filename or document name")
    page_number: int = Field(..., description="Exact page or slide number")
    text_snippet: str = Field(default="", description="Relevant excerpt supporting the statement")

class ChatMessage(BaseModel):
    role: str = Field(..., description="Role: 'user' or 'assistant'")
    content: str = Field(..., description="Message text content")

class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Student exam query")
    session_id: Optional[str] = Field(default=None, description="Optional conversation session ID")
    history: Optional[List[ChatMessage]] = Field(default=None, description="Optional previous conversation messages")

class ChatResponse(BaseModel):
    answer: str = Field(..., description="Strictly grounded response or exact refusal message")
    citations: List[CitationItem] = Field(default_factory=list, description="List of exact document page citations")
    refusal: bool = Field(..., description="True if query is out-of-corpus or ungrounded")
    session_id: str = Field(..., description="Session identifier")

class DocumentMetadata(BaseModel):
    source: str
    format: str
    total_pages: int
    chunks_count: int
    ocr_applied: bool
    created_at: str

class DocumentListResponse(BaseModel):
    documents: List[DocumentMetadata]

class IngestResponse(BaseModel):
    status: str
    source: str
    pages_indexed: int
    chunks_indexed: int
    ocr_pages: int

class PagePreviewResponse(BaseModel):
    source: str
    page: int
    content: str
    is_ocr: bool = False
    image_base64: Optional[str] = None

class EvaluationItemResult(BaseModel):
    id: int
    query: str
    category: str  # "single_source", "multi_source", "refusal"
    ground_truth_pages: List[Dict[str, Any]]
    expected_answer: Optional[str] = None
    predicted_answer: str
    predicted_citations: List[CitationItem]
    is_refusal: bool
    citation_correct: bool
    refusal_correct: bool
    passed: bool

class EvaluationSummary(BaseModel):
    total_questions: int
    target_questions: int
    target_passed: int
    refusal_questions: int
    refusal_passed: int
    refusal_rate: float
    citation_accuracy: float
    overall_passed: int
    overall_accuracy: float

class EvaluationRunResponse(BaseModel):
    run_id: str
    timestamp: str
    summary: EvaluationSummary
    details: List[EvaluationItemResult]

class HealthResponse(BaseModel):
    status: str
    qdrant_connected: bool
    mongo_connected: bool
    collection_name: str
    total_vectors: int
