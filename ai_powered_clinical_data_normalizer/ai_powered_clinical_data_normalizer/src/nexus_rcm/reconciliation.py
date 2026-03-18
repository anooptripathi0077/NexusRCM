from __future__ import annotations

from .types import NormalizedPayload


class ReconciliationEngine:
    REQUIRED_SUPPORTING_DOCS = {"discharge summary", "lab report", "bill copy"}

    def evaluate(self, payload: NormalizedPayload) -> dict:
        issues: list[str] = []

        unmapped_diagnoses = [item.label for item in payload.diagnoses if not item.code]
        unmapped_procedures = [item.label for item in payload.procedures if not item.code]

        if unmapped_diagnoses:
            issues.append(f"Unmapped diagnoses: {', '.join(unmapped_diagnoses)}")
        if unmapped_procedures:
            issues.append(f"Unmapped procedures: {', '.join(unmapped_procedures)}")

        present_docs = {doc.lower().strip() for doc in payload.supporting_documents}
        missing_docs = sorted(self.REQUIRED_SUPPORTING_DOCS - present_docs)
        if missing_docs:
            issues.append(f"Missing supporting documents: {', '.join(missing_docs)}")

        low_confidence = [
            item.label
            for item in [*payload.diagnoses, *payload.procedures]
            if item.confidence < 0.6
        ]
        if low_confidence:
            issues.append(f"Low confidence mappings require review: {', '.join(low_confidence)}")

        claim_ready = len(issues) == 0
        return {
            "claim_ready": claim_ready,
            "issue_count": len(issues),
            "issues": issues,
        }
