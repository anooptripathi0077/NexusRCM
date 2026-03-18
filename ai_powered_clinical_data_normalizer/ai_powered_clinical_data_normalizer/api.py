from __future__ import annotations

from fastapi import FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel, Field

from src.nexus_rcm.pipeline import NexusRCMPipeline

app = FastAPI(title="NexusRCM API", version="1.0.0")
pipeline = NexusRCMPipeline()


class NormalizeTextRequest(BaseModel):
    raw_text: str = Field(..., description="Unstructured clinical and billing text")
    source_name: str = Field(default="api_input.txt")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/normalize/text")
def normalize_text(payload: NormalizeTextRequest) -> dict:
    if not payload.raw_text.strip():
        raise HTTPException(status_code=400, detail="raw_text must not be empty")

    return pipeline.run_from_text(
        raw_text=payload.raw_text,
        source_name=payload.source_name,
        document_type="clinical_text",
    )


SUPPORTED_EXTENSIONS = {
    ".txt", ".md", ".csv",           # plain text
    ".pdf",                           # PDF (digital or scanned)
    ".png", ".jpg", ".jpeg",          # raster images
    ".tiff", ".tif", ".bmp", ".webp", # raster images
}


@app.post("/normalize/file")
async def normalize_file(file: UploadFile = File(...)) -> dict:
    file_name = file.filename or "uploaded.txt"
    ext = "." + file_name.rsplit(".", 1)[-1].lower() if "." in file_name else ".txt"

    if ext not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported file type '{ext}'. Supported: {sorted(SUPPORTED_EXTENSIONS)}",
        )

    data = await file.read()
    try:
        return pipeline.run_from_bytes(data, file_name)
    except Exception as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
