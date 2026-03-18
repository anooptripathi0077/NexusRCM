from __future__ import annotations

import re

from .types import ClinicalExtraction, IngestedDocument


class ClinicalAgent:
    def extract(self, doc: IngestedDocument) -> ClinicalExtraction:
        lines = [line.strip() for line in doc.raw_text.splitlines() if line.strip()]
        parsed_indices: set[int] = set()

        patient_name = self._extract_field(lines, r"^(?:Patient\s*)?Name\s*:\s*(.+)$")
        patient_id = self._extract_field(lines, r"^Patient\s*ID\s*:\s*(.+)$")
        if patient_name:
            patient_name = self._clean_name(patient_name)

        diagnoses = self._extract_list(lines, "Diagnosis", parsed_indices)
        procedures = self._extract_list(lines, "Procedure", parsed_indices)
        supporting_documents = self._extract_list(lines, "Supporting Document")

        diagnoses.extend(self._extract_diagnosis_sections(lines, parsed_indices))
        procedures.extend(self._extract_operation_sections(lines, parsed_indices))
        diagnoses = self._dedupe(diagnoses)
        procedures = self._dedupe(procedures)

        notes = []
        for idx, line in enumerate(lines):
            if idx in parsed_indices:
                continue
            if not any(
                line.lower().startswith(prefix)
                for prefix in (
                    "patient name:",
                    "name:",
                    "patient id:",
                    "diagnosis:",
                    "procedure:",
                    "supporting document:",
                )
            ):
                notes.append(line)

        return ClinicalExtraction(
            patient_name=patient_name,
            patient_id=patient_id,
            diagnoses=diagnoses,
            procedures=procedures,
            notes=notes,
            supporting_documents=supporting_documents,
        )

    @staticmethod
    def _extract_field(lines: list[str], pattern: str) -> str | None:
        regex = re.compile(pattern, re.IGNORECASE)
        for line in lines:
            match = regex.match(line)
            if match:
                return match.group(1).strip()
        return None

    @staticmethod
    def _extract_list(lines: list[str], key: str, parsed_indices: set[int] | None = None) -> list[str]:
        values = []
        prefix = f"{key.lower()}:"
        for idx, line in enumerate(lines):
            if line.lower().startswith(prefix):
                values.append(line.split(":", 1)[1].strip())
                if parsed_indices is not None:
                    parsed_indices.add(idx)
        return values

    @staticmethod
    def _extract_diagnosis_sections(lines: list[str], parsed_indices: set[int]) -> list[str]:
        diagnoses: list[str] = []
        headers = {"admitting diagnosis", "final diagnosis"}
        stop_words = {
            "operation",
            "results",
            "attending physician",
            "chart completed",
            "patient data sheet",
            "consent for admission",
        }

        for idx, line in enumerate(lines):
            lower = line.lower()
            if any(header in lower for header in headers):
                parsed_indices.add(idx)
                if ":" in line:
                    value = line.split(":", 1)[1].strip(" ;,")
                    if value:
                        diagnoses.append(value)

                next_idx = idx + 1
                while next_idx < len(lines):
                    candidate = lines[next_idx].strip()
                    candidate_lower = candidate.lower()
                    if not candidate:
                        break
                    if candidate_lower in stop_words or candidate_lower.startswith("secondary:"):
                        break
                    if "diagnosis" in candidate_lower or "operation" == candidate_lower:
                        break

                    diagnoses.append(candidate.strip(" ;,"))
                    parsed_indices.add(next_idx)
                    break

            if lower.startswith("secondary:"):
                value = line.split(":", 1)[1].strip(" ;,")
                if value:
                    diagnoses.append(value)
                parsed_indices.add(idx)

        return diagnoses

    @staticmethod
    def _extract_operation_sections(lines: list[str], parsed_indices: set[int]) -> list[str]:
        procedures: list[str] = []
        stop_words = {
            "results",
            "attending physician",
            "chart completed",
            "patient data sheet",
            "consent for admission",
        }

        for idx, line in enumerate(lines):
            lower = line.lower()
            if lower == "operation" or lower.startswith("operation:"):
                parsed_indices.add(idx)
                next_idx = idx + 1
                while next_idx < len(lines):
                    candidate = lines[next_idx].strip()
                    candidate_lower = candidate.lower()
                    if not candidate:
                        break
                    if any(stop in candidate_lower for stop in stop_words):
                        break
                    if "diagnosis" in candidate_lower:
                        break
                    if len(procedures) >= 8:
                        break

                    procedures.append(candidate.strip(" ;,"))
                    parsed_indices.add(next_idx)
                    next_idx += 1

            if "(diagnostic)" in lower or "(treatment)" in lower:
                procedures.append(line.strip(" ;,"))
                parsed_indices.add(idx)

        return procedures

    @staticmethod
    def _dedupe(items: list[str]) -> list[str]:
        seen: set[str] = set()
        result: list[str] = []
        for item in items:
            normalized = " ".join(item.lower().split())
            if not normalized or normalized in seen:
                continue
            seen.add(normalized)
            result.append(item)
        return result

    @staticmethod
    def _clean_name(name: str) -> str:
        cleaned = name.replace("_", " ")
        cleaned = re.sub(r"\([^)]*\)", "", cleaned)
        cleaned = re.sub(r"\s+", " ", cleaned).strip(" ,;")
        return cleaned
