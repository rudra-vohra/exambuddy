from pathlib import Path
import pytest
from backend.services.parser import parser_service

BASE_DIR = Path(__file__).resolve().parent.parent.parent

def test_parse_lecture_pdf():
    pdf_path = BASE_DIR / "corpus" / "pdf" / "dsp_lecture_notes.pdf"
    assert pdf_path.exists(), "dsp_lecture_notes.pdf must exist"

    docs, ocr_count, doc_format = parser_service.parse_file(pdf_path)
    assert len(docs) == 26
    assert doc_format == "pdf"
    assert docs[0].metadata["page_number"] == 1
    assert "Discrete-Time Signals" in docs[0].page_content

def test_parse_slides():
    slides_path = BASE_DIR / "corpus" / "slides" / "dsp_slides_sampling_quantization.pdf"
    assert slides_path.exists(), "dsp_slides_sampling_quantization.pdf must exist"

    docs, ocr_count, doc_format = parser_service.parse_file(slides_path)
    assert len(docs) == 18
    assert doc_format == "slides"
    assert "Nyquist-Shannon" in docs[1].page_content

def test_parse_markdown():
    md_path = BASE_DIR / "corpus" / "markdown" / "dsp_algorithms_cheatsheet.md"
    assert md_path.exists(), "dsp_algorithms_cheatsheet.md must exist"

    docs, ocr_count, doc_format = parser_service.parse_file(md_path)
    assert len(docs) == 10
    assert doc_format == "markdown"
    assert "Twiddle" in docs[0].page_content
