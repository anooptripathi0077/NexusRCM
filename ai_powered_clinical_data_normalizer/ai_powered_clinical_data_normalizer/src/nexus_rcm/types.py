from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class IngestedDocument:
    source_path: str
    document_type: str
    raw_text: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ClinicalExtraction:
    patient_name: str | None
    patient_id: str | None
    diagnoses: list[str]
    procedures: list[str]
    notes: list[str]
    supporting_documents: list[str]


@dataclass
class CodedItem:
    label: str
    code: str | None
    code_system: str
    confidence: float


@dataclass
class NormalizedPayload:
    patient_name: str | None
    patient_id: str | None
    diagnoses: list[CodedItem]
    procedures: list[CodedItem]
    notes: list[str]
    supporting_documents: list[str]
