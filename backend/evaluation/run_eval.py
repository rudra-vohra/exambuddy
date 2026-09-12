import asyncio
import sys
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

from backend.evaluation.evaluator import evaluator_service

async def main():
    print("==================================================")
    print("STARTING EXAM-NIGHT RAG EVALUATION BENCHMARK")
    print("==================================================")
    
    max_q = int(sys.argv[1]) if len(sys.argv) > 1 else None
    result = await evaluator_service.run_benchmark(max_questions=max_q)

    summary = result.summary
    print("\n--- BENCHMARK RESULTS ---")
    print(f"Run ID: {result.run_id}")
    print(f"Total Questions Evaluated: {summary.total_questions}")
    print(f"Target Questions: {summary.target_questions} | Passed: {summary.target_passed}")
    print(f"Citation Accuracy: {summary.citation_accuracy}%")
    print(f"Refusal Questions: {summary.refusal_questions} | Passed: {summary.refusal_passed}")
    print(f"Refusal Rate: {summary.refusal_rate}% (Target: 100%)")
    print(f"Overall Accuracy: {summary.overall_accuracy}%\n")

    print("--- SAMPLE QUESTION DETAILS ---")
    for r in result.details[:5]:
        status_str = "PASS" if r.passed else "FAIL"
        print(f"[{status_str}] Q{r.id} ({r.category}): {r.query[:70]}...")
        if r.predicted_citations:
            cits = ", ".join([f"{c.source} p.{c.page_number}" for c in r.predicted_citations])
            print(f"       Citations: {cits}")
        if r.is_refusal:
            print(f"       Refusal: {r.predicted_answer}")

    print("==================================================")

if __name__ == "__main__":
    asyncio.run(main())
