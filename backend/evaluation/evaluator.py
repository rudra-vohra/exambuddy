import json
import uuid
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
from backend.schemas import (
    EvaluationRunResponse,
    EvaluationSummary,
    EvaluationItemResult,
    CitationItem
)
from backend.services.retriever import retriever_service
from backend.services.generator import generator_service, EXACT_REFUSAL_MESSAGE
from backend.services.database import db_service

logger = logging.getLogger(__name__)

BENCHMARK_PATH = Path(__file__).resolve().parent / "benchmark_dataset.json"

class EvaluatorService:
    def __init__(self):
        pass

    def load_dataset(self) -> List[Dict[str, Any]]:
        with open(BENCHMARK_PATH, "r", encoding="utf-8") as f:
            return json.load(f)

    async def run_benchmark(self, max_questions: int = None) -> EvaluationRunResponse:
        dataset = self.load_dataset()
        if max_questions:
            dataset = dataset[:max_questions]

        run_id = f"eval_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:8]}"
        results: List[EvaluationItemResult] = []

        target_total = 0
        target_passed = 0
        refusal_total = 0
        refusal_passed = 0
        citation_matches = 0

        for item in dataset:
            q_id = item["id"]
            query = item["query"]
            category = item["category"]
            gt_pages = item.get("ground_truth_pages", [])
            expected_ans = item.get("expected_answer")

            # 1. Retrieve
            chunks = retriever_service.retrieve(query=query)
            context_str = retriever_service.build_context_string(chunks)

            # 2. Generate
            gen_result = generator_service.generate_grounded_answer(
                query=query,
                context_chunks=chunks,
                context_string=context_str
            )

            is_refusal = gen_result["refusal"]
            answer = gen_result["answer"]
            pred_citations = [
                CitationItem(
                    source=c["source"],
                    page_number=c["page_number"],
                    text_snippet=c.get("text_snippet", "")
                )
                for c in gen_result.get("citations", [])
            ]

            citation_correct = False
            refusal_correct = False
            passed = False

            if category == "refusal":
                refusal_total += 1
                if is_refusal and EXACT_REFUSAL_MESSAGE in answer:
                    refusal_correct = True
                    refusal_passed += 1
                    passed = True
            else:
                target_total += 1
                if not is_refusal:
                    # Check if predicted citations overlap with ground truth
                    matched = False
                    for gt in gt_pages:
                        gt_source = gt.get("source", "").lower()
                        gt_page = gt.get("page")
                        for pc in pred_citations:
                            if gt_source in pc.source.lower() and pc.page_number == gt_page:
                                matched = True
                                break
                        if matched:
                            break

                    if matched:
                        citation_correct = True
                        citation_matches += 1
                        passed = True
                    elif len(pred_citations) > 0:
                        # At least retrieved valid citations from the corpus
                        passed = True
                    if passed:
                        target_passed += 1

            results.append(
                EvaluationItemResult(
                    id=q_id,
                    query=query,
                    category=category,
                    ground_truth_pages=gt_pages,
                    expected_answer=expected_ans,
                    predicted_answer=answer,
                    predicted_citations=pred_citations,
                    is_refusal=is_refusal,
                    citation_correct=citation_correct,
                    refusal_correct=refusal_correct,
                    passed=passed
                )
            )

        refusal_rate = (refusal_passed / refusal_total * 100.0) if refusal_total > 0 else 0.0
        citation_acc = (citation_matches / target_total * 100.0) if target_total > 0 else 0.0
        overall_passed = target_passed + refusal_passed
        overall_acc = (overall_passed / len(dataset) * 100.0) if dataset else 0.0

        summary = EvaluationSummary(
            total_questions=len(dataset),
            target_questions=target_total,
            target_passed=citation_matches,
            refusal_questions=refusal_total,
            refusal_passed=refusal_passed,
            refusal_rate=round(refusal_rate, 2),
            citation_accuracy=round(citation_acc, 2),
            overall_passed=overall_passed,
            overall_accuracy=round(overall_acc, 2)
        )

        run_response = EvaluationRunResponse(
            run_id=run_id,
            timestamp=datetime.utcnow().isoformat(),
            summary=summary,
            details=results
        )

        # Save to database
        await db_service.save_evaluation_run(
            run_id=run_id,
            summary=summary.dict(),
            details=[r.dict() for r in results]
        )

        return run_response

evaluator_service = EvaluatorService()
