import base64
from pathlib import Path
from typing import List, Dict, Any, Tuple
import pymupdf
from langchain_core.documents import Document
from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from backend.config import settings

class MultimodalParser:
    def __init__(self):
        self._vlm = None
        self._cached_key = None

    @property
    def vlm(self):
        current_key = settings.GEMINI_API_KEY
        if self._vlm is None or self._cached_key != current_key:
            self._vlm = ChatGoogleGenerativeAI(
                model=settings.OCR_MODEL,
                google_api_key=current_key
            )
            self._cached_key = current_key
        return self._vlm

    def render_pdf_page_to_base64(self, pdf_path: Path, page_index: int) -> str:
        doc = pymupdf.open(pdf_path)
        page = doc[page_index]
        matrix = pymupdf.Matrix(settings.DPI_SCALE, settings.DPI_SCALE)
        pix = page.get_pixmap(matrix=matrix)
        png_bytes = pix.tobytes("png")
        doc.close()
        return base64.b64encode(png_bytes).decode("utf-8")

    def transcribe_image_b64(self, image_b64: str) -> str:
        prompt_text = (
            "Transcribe all handwritten and printed text on this page exactly as written. "
            "Preserve structure (headings, bullet points, equations) where possible. "
            "Do not add commentary, only output the transcription."
        )
        message = HumanMessage(
            content=[
                {"type": "text", "text": prompt_text},
                {
                    "type": "image_url",
                    "image_url": f"data:image/png;base64,{image_b64}"
                }
            ]
        )
        try:
            response = self.vlm.invoke([message])
            content = response.content
            if isinstance(content, list):
                parts = []
                for part in content:
                    if isinstance(part, str):
                        parts.append(part)
                    elif isinstance(part, dict) and "text" in part:
                        parts.append(part["text"])
                content = "\n".join(parts)
            return content.strip() if isinstance(content, str) else str(content)
        except Exception as e:
            return f"[OCR Error: {str(e)}]"

    def parse_pdf(self, file_path: Path, doc_format: str = "pdf") -> Tuple[List[Document], int]:
        doc = pymupdf.open(file_path)
        documents: List[Document] = []
        ocr_count = 0
        total_pages = len(doc)

        for page_index in range(total_pages):
            page = doc[page_index]
            page_num = page_index + 1  # 1-indexed for student-facing citations
            text = page.get_text().strip()
            is_ocr = False

            if len(text) < settings.MIN_CHARS_THRESHOLD:
                # Page contains little or no extractable text (e.g. handwritten scan or visual diagram)
                img_b64 = self.render_pdf_page_to_base64(file_path, page_index)
                transcription = self.transcribe_image_b64(img_b64)
                text = transcription
                is_ocr = True
                ocr_count += 1

            meta = {
                "source": file_path.name,
                "page_label": str(page_num),
                "page_number": page_num,
                "total_pages": total_pages,
                "format": doc_format,
                "ocr": is_ocr
            }
            documents.append(Document(page_content=text, metadata=meta))

        doc.close()
        return documents, ocr_count

    def parse_image_file(self, file_path: Path) -> Tuple[List[Document], int]:
        image_bytes = file_path.read_bytes()
        img_b64 = base64.b64encode(image_bytes).decode("utf-8")
        transcription = self.transcribe_image_b64(img_b64)

        meta = {
            "source": file_path.name,
            "page_label": "1",
            "page_number": 1,
            "total_pages": 1,
            "format": "handwritten_image",
            "ocr": True
        }
        return [Document(page_content=transcription, metadata=meta)], 1

    def parse_text_or_markdown(self, file_path: Path) -> Tuple[List[Document], int]:
        text = file_path.read_text(encoding="utf-8")
        # Split markdown into sections or logical pages if separator exists
        sections = text.split("\n---") if "\n---" in text else [text]
        documents: List[Document] = []

        total_pages = len(sections)
        for idx, section in enumerate(sections):
            page_num = idx + 1
            meta = {
                "source": file_path.name,
                "page_label": str(page_num),
                "page_number": page_num,
                "total_pages": total_pages,
                "format": "markdown",
                "ocr": False
            }
            documents.append(Document(page_content=section.strip(), metadata=meta))

        return documents, 0

    def parse_file(self, file_path: Path) -> Tuple[List[Document], int, str]:
        ext = file_path.suffix.lower()
        if ext == ".pdf":
            doc_format = "slides" if "slide" in file_path.stem.lower() else "pdf"
            docs, ocr_count = self.parse_pdf(file_path, doc_format=doc_format)
            return docs, ocr_count, doc_format
        elif ext in [".png", ".jpg", ".jpeg"]:
            docs, ocr_count = self.parse_image_file(file_path)
            return docs, ocr_count, "handwritten_image"
        elif ext in [".md", ".txt"]:
            docs, ocr_count = self.parse_text_or_markdown(file_path)
            return docs, ocr_count, "markdown"
        else:
            raise ValueError(f"Unsupported file format: {ext}")

parser_service = MultimodalParser()
