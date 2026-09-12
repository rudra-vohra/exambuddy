import httpx
import json

client = httpx.Client(base_url="http://localhost:8000", timeout=45.0)

def main():
    print("=== 1. HEALTH ENDPOINT ===")
    r = client.get("/api/health")
    print(f"Status {r.status_code}: {r.json()}")

    print("\n=== 2. IN-CORPUS CHAT ENDPOINT ===")
    r = client.post("/api/chat", json={"query": "What is the condition for an LTI system to be BIBO stable?"})
    data = r.json()
    print(f"Status {r.status_code}")
    print(f"Answer: {data['answer']}")
    print(f"Refusal: {data['refusal']}")
    print(f"Citations: {data['citations']}")

    print("\n=== 3. OUT-OF-CORPUS REFUSAL ENDPOINT ===")
    r = client.post("/api/chat", json={"query": "What is the Kalman filter state estimation equation for linear dynamical systems?"})
    data = r.json()
    print(f"Status {r.status_code}")
    print(f"Answer: {data['answer']}")
    print(f"Refusal: {data['refusal']}")

    print("\n=== 4. DOCUMENTS ENDPOINT ===")
    r = client.get("/api/documents")
    docs = r.json()["documents"]
    print(f"Total documents: {len(docs)}")
    for d in docs:
        print(f"  - {d['source']}: {d['total_pages']} pages, {d['chunks_count']} chunks, OCR: {d['ocr_applied']}")

    print("\n=== 5. PAGE PREVIEW ENDPOINT ===")
    r = client.get("/api/documents/page-preview", params={"source": "dsp_lecture_notes.pdf", "page": 1})
    preview = r.json()
    print(f"Status {r.status_code}, Source: {preview['source']}, Page: {preview['page']}, Content snippet: {preview['content'][:100]}...")

    print("\n=== 6. BENCHMARK EVALUATION ENDPOINT (5 Qs) ===")
    r = client.post("/api/evaluate/run", params={"max_questions": 5})
    eval_data = r.json()
    print(f"Status {r.status_code}")
    print(f"Summary: {json.dumps(eval_data['summary'], indent=2)}")

if __name__ == "__main__":
    main()
