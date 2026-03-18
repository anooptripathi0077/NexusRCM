from __future__ import annotations

from .types import NormalizedPayload


class FHIRMappingEngine:
    def map_to_bundle(self, payload: NormalizedPayload) -> dict:
        patient_id = payload.patient_id or "unknown"
        patient_ref = f"Patient/{patient_id}"

        patient = {
            "resourceType": "Patient",
            "id": patient_id,
            "name": [{"text": payload.patient_name or "Unknown"}],
        }

        conditions = []
        for idx, diagnosis in enumerate(payload.diagnoses, start=1):
            conditions.append(
                {
                    "resourceType": "Condition",
                    "id": f"cond-{idx}",
                    "subject": {"reference": patient_ref},
                    "code": {
                        "coding": [
                            {
                                "system": "http://hl7.org/fhir/sid/icd-10",
                                "code": diagnosis.code,
                                "display": diagnosis.label,
                            }
                        ]
                    },
                    "extension": [
                        {
                            "url": "http://example.org/fhir/StructureDefinition/confidence",
                            "valueDecimal": diagnosis.confidence,
                        }
                    ],
                }
            )

        procedures = []
        for idx, procedure in enumerate(payload.procedures, start=1):
            procedures.append(
                {
                    "resourceType": "Procedure",
                    "id": f"proc-{idx}",
                    "subject": {"reference": patient_ref},
                    "code": {
                        "coding": [
                            {
                                "system": "http://www.ama-assn.org/go/cpt",
                                "code": procedure.code,
                                "display": procedure.label,
                            }
                        ]
                    },
                    "extension": [
                        {
                            "url": "http://example.org/fhir/StructureDefinition/confidence",
                            "valueDecimal": procedure.confidence,
                        }
                    ],
                }
            )

        claim = {
            "resourceType": "Claim",
            "id": f"claim-{patient_id}",
            "patient": {"reference": patient_ref},
            "diagnosis": [
                {
                    "sequence": idx,
                    "diagnosisCodeableConcept": {
                        "coding": [{"code": item.code, "display": item.label}]
                    },
                }
                for idx, item in enumerate(payload.diagnoses, start=1)
            ],
            "procedure": [
                {
                    "sequence": idx,
                    "procedureCodeableConcept": {
                        "coding": [{"code": item.code, "display": item.label}]
                    },
                }
                for idx, item in enumerate(payload.procedures, start=1)
            ],
            "supportingInfo": [
                {"sequence": idx, "valueString": doc}
                for idx, doc in enumerate(payload.supporting_documents, start=1)
            ],
        }

        entries = [patient, *conditions, *procedures, claim]
        return {
            "resourceType": "Bundle",
            "type": "collection",
            "entry": [{"resource": item} for item in entries],
        }
