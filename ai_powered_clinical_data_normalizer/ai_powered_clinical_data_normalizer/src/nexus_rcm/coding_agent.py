from __future__ import annotations

import re

from .types import ClinicalExtraction, CodedItem, NormalizedPayload


class CodingAgent:
    ICD10_MAP = {
        "type 2 diabetes": "E11.9",
        "hypertension": "I10",
        "chronic kidney disease": "N18.9",
        "pneumonia": "J18.9",
    }

    CPT_MAP = {
        "complete blood count": "85027",
        "x-ray chest": "71045",
        "ecg": "93000",
        "hemodialysis": "90935",
    }

    def normalize(self, extracted: ClinicalExtraction) -> NormalizedPayload:
        diagnosis_items = [self._map_diagnosis(item) for item in extracted.diagnoses]
        procedure_items = [self._map_procedure(item) for item in extracted.procedures]

        return NormalizedPayload(
            patient_name=extracted.patient_name,
            patient_id=extracted.patient_id,
            diagnoses=diagnosis_items,
            procedures=procedure_items,
            notes=extracted.notes,
            supporting_documents=extracted.supporting_documents,
        )

    def _map_diagnosis(self, label: str) -> CodedItem:
        mapped_code, confidence = self._lookup(label, self.ICD10_MAP)
        return CodedItem(
            label=label,
            code=mapped_code,
            code_system="ICD-10",
            confidence=confidence,
        )

    def _map_procedure(self, label: str) -> CodedItem:
        mapped_code, confidence = self._lookup(label, self.CPT_MAP)
        return CodedItem(
            label=label,
            code=mapped_code,
            code_system="CPT",
            confidence=confidence,
        )

    @staticmethod
    def _lookup(label: str, dictionary: dict[str, str]) -> tuple[str | None, float]:
        label_tokens = CodingAgent._tokenize(label)

        best_phrase: str | None = None
        best_code: str | None = None
        best_score = 0.0

        for phrase, code in dictionary.items():
            phrase_tokens = CodingAgent._tokenize(phrase)
            if not phrase_tokens:
                continue

            overlap = len(label_tokens & phrase_tokens)
            score = overlap / len(phrase_tokens)

            if phrase in label.lower() or label.lower() in phrase:
                score = max(score, 0.95)

            if score > best_score:
                best_score = score
                best_phrase = phrase
                best_code = code

        if best_code is None or best_score < 0.5:
            return None, 0.35

        confidence = min(0.99, 0.55 + (best_score * 0.44))
        if best_phrase and best_phrase == label.lower().strip():
            confidence = max(confidence, 0.97)
        return best_code, round(confidence, 2)

    @staticmethod
    def _tokenize(text: str) -> set[str]:
        return {token for token in re.findall(r"[a-zA-Z0-9]+", text.lower()) if token}
