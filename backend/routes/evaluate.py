from typing import Optional
from fastapi import APIRouter, Query, HTTPException
from backend.schemas import EvaluationRunResponse
from backend.evaluation.evaluator import evaluator_service
from backend.services.database import db_service

router = APIRouter(prefix="/api/evaluate", tags=["Evaluation"])

@router.post("/run", response_model=EvaluationRunResponse)
async def run_evaluation(max_questions: Optional[int] = Query(None, ge=1, le=30)):
    try:
        run_result = await evaluator_service.run_benchmark(max_questions=max_questions)
        return run_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {str(e)}")

@router.get("/latest")
async def get_latest_evaluation():
    run = await db_service.get_latest_evaluation_run()
    if not run:
        return {"message": "No evaluation runs found yet."}
    return run
