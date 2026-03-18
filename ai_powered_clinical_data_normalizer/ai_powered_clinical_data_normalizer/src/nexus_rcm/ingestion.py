from __future__ import annotations

import io
from pathlib import Path

import fitz  # pymupdf
from PIL import Image
import pytesseract

from .types import IngestedDocument

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".tiff", ".tif", ".bmp", ".webp"}


class DataIngestionModule:
    def ingest(self, input_path: Path) -> IngestedDocument:
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")
        data = input_path.read_bytes()
        return self.ingest_bytes(data, file_name=input_path.name)

    def ingest_text(
        self,
        raw_text: str,
        source_name: str = "api_input.txt",
        document_type: str = "clinical_text",
    ) -> IngestedDocument:
        return IngestedDocument(
            source_path=source_name,
            document_type=document_type,
            raw_text=raw_text,
            metadata={
                "file_name": source_name,
                "extension": Path(source_name).suffix.lower(),
                "line_count": len(raw_text.splitlines()),
            },
        )

    def ingest_bytes(self, data: bytes, file_name: str) -> IngestedDocument:
        ext = Path(file_name).suffix.lower()
        document_type = self._infer_document_type(ext)
        raw_text = self._extract_text(data, ext)
        return IngestedDocument(
            source_path=file_name,
            document_type=document_type,
            raw_text=raw_text,
            metadata={
                "file_name": file_name,
                "extension": ext,
                "line_count": len(raw_text.splitlines()),
            },
        )

    def _extract_text(self, data: bytes, extension: str) -> str:
        if extension == ".pdf":
            return self._pdf_bytes_to_text(data)
        if extension in IMAGE_EXTENSIONS:
            return self._image_bytes_to_text(data)
        try:
            return data.decode("utf-8")
        except UnicodeDecodeError:
            return data.decode("latin-1", errors="replace")

    _TESSERACT_HINT = (
        "Tesseract OCR is required for image/scanned-PDF processing but is not installed. "
        "Download the Windows installer from "
        "https://github.com/UB-Mannheim/tesseract/wiki , install it, "
        'then make sure "tesseract" is on your PATH and restart the server.'
    )

    @staticmethod
    def _pdf_bytes_to_text(data: bytes) -> str:
        doc = fitz.open(stream=data, filetype="pdf")
        pages: list[str] = []
        for page in doc:
            text = page.get_text().strip()
            if text:
                pages.append(text)
            else:
                # Scanned page — render at 300 DPI and attempt OCR
                try:
                    pix = page.get_pixmap(dpi=300)
                    img = Image.open(io.BytesIO(pix.tobytes("png")))
                    pages.append(pytesseract.image_to_string(img).strip())
                except Exception as exc:
                    if "tesseract" in str(exc).lower():
                        raise RuntimeError(DataIngestionModule._TESSERACT_HINT) from exc
                    raise
        return "\n".join(pages).strip()

    @staticmethod
    def _image_bytes_to_text(data: bytes) -> str:
        img = Image.open(io.BytesIO(data))
        try:
            return pytesseract.image_to_string(img).strip()
        except Exception as exc:
            if "tesseract" in str(exc).lower():
                raise RuntimeError(DataIngestionModule._TESSERACT_HINT) from exc
            raise

    @staticmethod
    def _infer_document_type(extension: str) -> str:
        if extension in {".txt", ".md", ".csv"}:
            return "clinical_text"
        if extension == ".pdf":
            return "pdf_record"
        if extension in IMAGE_EXTENSIONS:
            return "image_record"
        return "unknown_record"
