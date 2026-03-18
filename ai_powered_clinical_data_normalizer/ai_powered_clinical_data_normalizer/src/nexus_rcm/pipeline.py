from __future__ import annotations

from dataclasses import asdict
from pathlib import Path

from .coding_agent import CodingAgent
from .extraction_agent import ClinicalAgent
from .fhir_mapper import FHIRMappingEngine
from .ingestion import DataIngestionModule
from .reconciliation import ReconciliationEngine
from .types import IngestedDocument


class NexusRCMPipeline:
    def __init__(self) -> None:
        self.ingestion = DataIngestionModule()
        self.clinical_agent = ClinicalAgent()
        self.coding_agent = CodingAgent()
        self.fhir_mapper = FHIRMappingEngine()
        self.reconciliation = ReconciliationEngine()

    def run(self, input_path: Path) -> dict:
        ingested = self.ingestion.ingest(input_path)
        return self._run_from_ingested(ingested)

    def run_from_text(
        self,
        raw_text: str,
        source_name: str = "api_input.txt",
        document_type: str = "clinical_text",
    ) -> dict:
        ingested = self.ingestion.ingest_text(
            raw_text=raw_text,
            source_name=source_name,
            document_type=document_type,
        )
        return self._run_from_ingested(ingested)

    def run_from_bytes(self, data: bytes, file_name: str) -> dict:
        ingested = self.ingestion.ingest_bytes(data, file_name)
        return self._run_from_ingested(ingested)

    def _run_from_ingested(self, ingested: IngestedDocument) -> dict:
        extracted = self.clinical_agent.extract(ingested)
        normalized = self.coding_agent.normalize(extracted)
        fhir_bundle = self.fhir_mapper.map_to_bundle(normalized)
        reconciliation_report = self.reconciliation.evaluate(normalized)

        return {
            "ingested": asdict(ingested),
            "extracted": asdict(extracted),
            "normalized_payload": {
                "patient_name": normalized.patient_name,
                "patient_id": normalized.patient_id,
                "diagnoses": [asdict(item) for item in normalized.diagnoses],
                "procedures": [asdict(item) for item in normalized.procedures],
                "notes": normalized.notes,
                "supporting_documents": normalized.supporting_documents,
            },
            "fhir_bundle": fhir_bundle,
            "reconciliation_report": reconciliation_report,
        }
