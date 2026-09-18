import json
import re
import logging
from typing import List, Dict, Any, Tuple, Optional
from openai import OpenAI
from backend.config import settings
from backend.schemas import CitationItem, ChatResponse

logger = logging.getLogger(__name__)

EXACT_REFUSAL_MESSAGE = "The provided course materials do not contain sufficient information to answer this question."

GROUNDED_SYSTEM_PROMPT = """You are an exam-night study assistant. You answer student queries strictly using ONLY the provided course material excerpts.

CRITICAL RULES:
1. Strict Grounding: You must NEVER use your pre-trained knowledge to answer questions not present in the excerpts. If the excerpts do not explicitly contain the necessary information to answer the question, or if the question asks about a topic outside the provided excerpts, you MUST REFUSE.
2. Refusal Requirement: When refusing, set "refusal": true, set "answer": "The provided course materials do not contain sufficient information to answer this question.", and set "citations": [].
3. Structured Citations Only: All document and page number citations must be placed strictly in the "citations" list. Do NOT include inline citations, source brackets, or tags like [Source: ...] or (Source: ...) inside the "answer" text. Keep the "answer" text clean, professional, and directly readable.
4. Multi-Document Synthesis: When a question requires combining concepts from different documents, clearly synthesize the facts in the answer and include all corresponding sources and pages in the "citations" list.
5. Zero Emojis: Do not include any emojis in your response.
6. Zero Conversational Filler: Do not add greetings, apologies, or fluff. Provide concise, direct academic answers.
7. Topic Overview & Listing: When the student asks what topics, concepts, or chapters are covered in a document, you must format your response as a clear, well-structured bulleted list of the topics covered with brief descriptions. Ensure every referenced topic is cited in the "citations" list with its document source and page number.

You MUST respond strictly with a valid JSON object in the following format:
{
  "refusal": false,
  "answer": "Your detailed, grounded answer written in clean prose without any inline [Source: ...] tags...",
  "citations": [
    {
      "source": "filename.pdf",
      "page_number": 12,
      "text_snippet": "exact or near-exact short sentence from the context"
    }
  ]
}

If the excerpts do NOT contain the answer:
{
  "refusal": true,
  "answer": "The provided course materials do not contain sufficient information to answer this question.",
  "citations": []
}"""

class GeneratorService:
    def __init__(self):
        self._client = None
        self._cached_key = None

    @property
    def client(self) -> OpenAI:
        current_key = settings.GEMINI_API_KEY
        if self._client is None or self._cached_key != current_key:
            self._client = OpenAI(
                api_key=current_key,
                base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
            )
            self._cached_key = current_key
        return self._client

    def reformulate_query(self, query: str, chat_history: Optional[List[Dict[str, Any]]] = None) -> str:
        if not chat_history:
            return query

        recent = [m for m in chat_history if m.get("content") and str(m.get("content")).strip()]
        if not recent:
            return query

        dialogue = []
        for m in recent[-4:]:
            role = "Student" if m.get("role") == "user" else "Assistant"
            dialogue.append(f"{role}: {str(m.get('content', '')).strip()[:250]}")
        dialogue_text = "\n".join(dialogue)

        system_instruction = (
            "Given the following dialogue history between a Student and an Assistant, "
            "reformulate the student's latest query into a standalone search query that captures "
            "the core subject, technology, or topic discussed in the conversation. "
            "If the latest query is already completely standalone and self-contained, return it unchanged. "
            "Do NOT answer the question. Only output the standalone query."
        )

        try:
            response = self.client.chat.completions.create(
                model=settings.GENERATION_MODEL,
                messages=[
                    {"role": "system", "content": system_instruction},
                    {
                        "role": "user",
                        "content": f"Dialogue History:\n{dialogue_text}\n\nStudent Query: {query}\n\nStandalone Query:"
                    }
                ],
                temperature=0.0,
                timeout=8.0
            )
            reformulated = response.choices[0].message.content.strip()
            reformulated = re.sub(r'^(Standalone Query|Query|Question):\s*', '', reformulated, flags=re.IGNORECASE)
            reformulated = reformulated.strip('"\' \n')
            return reformulated if reformulated else query
        except Exception as e:
            logger.warning(f"Query reformulation error: {e}")
            return query

    def generate_grounded_answer(
        self,
        query: str,
        context_chunks: List[Dict[str, Any]],
        context_string: str,
        chat_history: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        # If no chunks were retrieved at all
        if not context_chunks or not context_string.strip():
            return {
                "answer": EXACT_REFUSAL_MESSAGE,
                "citations": [],
                "refusal": True
            }

        history_section = ""
        if chat_history:
            recent_turns = []
            for m in chat_history[-4:]:
                r = "Student" if m.get("role") == "user" else "Assistant"
                c = str(m.get("content", "")).strip()[:300]
                if c:
                    recent_turns.append(f"{r}: {c}")
            if recent_turns:
                history_section = "Previous Conversation:\n" + "\n".join(recent_turns) + "\n\n"

        user_content = f"""{history_section}Student Query:
{query}

Available Course Material Excerpts:
{context_string}

Remember: If the answer cannot be determined purely from these excerpts, you must output a refusal JSON."""

        try:
            response = self.client.chat.completions.create(
                model=settings.GENERATION_MODEL,
                messages=[
                    {"role": "system", "content": GROUNDED_SYSTEM_PROMPT},
                    {"role": "user", "content": user_content}
                ],
                response_format={"type": "json_object"},
                temperature=0.0,
                timeout=60.0
            )
            raw_text = response.choices[0].message.content.strip()

            # Robust JSON extraction
            parsed = None
            try:
                parsed = json.loads(raw_text)
            except Exception:
                cleaned = re.sub(r"^```(?:json)?\s*", "", raw_text)
                cleaned = re.sub(r"\s*```$", "", cleaned)
                try:
                    parsed = json.loads(cleaned)
                except Exception:
                    match = re.search(r"(\{.*\})", raw_text, re.DOTALL)
                    if match:
                        parsed = json.loads(match.group(1))
                    else:
                        raise ValueError(f"Could not parse JSON response from LLM: {raw_text[:200]}")

            is_refusal = bool(parsed.get("refusal", False))
            answer = parsed.get("answer", "")
            
            # Sanitize refusal
            if is_refusal or EXACT_REFUSAL_MESSAGE in answer:
                return {
                    "answer": EXACT_REFUSAL_MESSAGE,
                    "citations": [],
                    "refusal": True
                }

            # Strip any inline source tags like [Source: ...], (Source: ...) so answer text is clean
            answer = re.sub(r"\[Source:[^\]]*\]", "", answer, flags=re.IGNORECASE)
            answer = re.sub(r"\(Source:[^\)]*\)", "", answer, flags=re.IGNORECASE)
            answer = re.sub(r"\[p\.\s*\d+\]", "", answer, flags=re.IGNORECASE)
            answer = re.sub(r"\s+([.,;:!?])", r"\1", answer)
            answer = re.sub(r"  +", " ", answer).strip()

            # Parse citations
            raw_citations = parsed.get("citations", [])
            citations = []
            for c in raw_citations:
                try:
                    citations.append({
                        "source": str(c.get("source", "")),
                        "page_number": int(c.get("page_number", 1)),
                        "text_snippet": str(c.get("text_snippet", ""))
                    })
                except (ValueError, TypeError):
                    continue

            # If the model didn't provide structured citations but answered, fallback to matched chunk sources
            if not citations and context_chunks:
                for chunk in context_chunks[:2]:
                    citations.append({
                        "source": chunk["source"],
                        "page_number": chunk["page_number"],
                        "text_snippet": chunk["content"][:150]
                    })

            return {
                "answer": answer,
                "citations": citations,
                "refusal": False
            }

        except Exception as e:
            logger.error(f"Error during LLM generation: {e}")
            # In case of generation failure or invalid JSON, refuse safely
            return {
                "answer": EXACT_REFUSAL_MESSAGE,
                "citations": [],
                "refusal": True
            }

generator_service = GeneratorService()
