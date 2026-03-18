# NexusRCM MVP

## An Agentic Normalization Layer for Revenue Reconciliation

NexusRCM is an intelligent, multi-agent pipeline that transforms unstructured clinical records into standardized FHIR claims, bridging the translation gap between clinical reality and payer requirements to eliminate revenue leakage.

### Why this matters

The root cause of Revenue Cycle Management (RCM) inefficiencies is not a lack of data—it is the translation gap.

- Clinical documentation and physician language often do not map cleanly to billing codes.
- Procedures are improperly coded, and claims are rejected.
- Supporting clinical documents are rarely structured for payer validation.

NexusRCM introduces an agentic normalization layer between raw hospital data and rigid payer requirements, ensuring that clinical care and revenue are aligned before claims submission.

## NexusRCM architecture (4-phase pipeline)

1. **Context-Aware Data Ingestion**
   - Ingest unstructured clinical formats (text, PDFs, reports) with a context-aware approach.
   - Understand document layout, tables, and narrative structure instead of blind OCR scraping.

2. **Dual-Agent Extraction and Normalization**
   - **Agent 1 (Clinical Agent)**: Extracts entities from unstructured text and converts them into standardized JSON.
   - **Agent 2 (Coding Agent)**: Normalizes terms into ICD-10 and CPT with semantic vector search and confidence scores.

3. **Dynamic FHIR Mapping Engine**
   - Maps normalized structured data to HL7 FHIR resources.
   - Example mappings: diagnoses → `Condition`, treatments → `Procedure`, claim details → `Claim`.

4. **Pre-emptive Reconciliation Logic**
   - Automated auditor checks for logical consistency.
   - Verifies CPT/ICD coherence and required supporting document linkage.

## Impact

By shifting from manual entry to AI-assisted normalization and review, NexusRCM:

- Helps hospital billing teams and RCM managers catch mismatches before submission.
- Reduces claim rejections and underpayments.
- Aligns clinical care, billing codes, and claims for better revenue reconciliation.

## What this MVP implements

1. Context-aware ingestion from text and PDF sources.
2. Dual-agent pipeline with extraction + coding normalization.
3. Mapping to FHIR resources (`Patient`, `Condition`, `Procedure`, `Claim`).
4. Pre-emptive reconciliation checks for clinical and billing consistency.
5. FastAPI endpoints for text/file normalization.

## Project structure

```
.
├── data/
│   └── sample_record.txt
├── output/
│   ├── fhir_bundle.json
│   ├── normalized_payload.json
│   └── reconciliation_report.json
├── api.py
├── main.py
├── requirements.txt
└── src/
    └── nexus_rcm/
        ├── __init__.py
        ├── coding_agent.py
        ├── extraction_agent.py
        ├── fhir_mapper.py
        ├── ingestion.py
        ├── pipeline.py
        ├── reconciliation.py
        └── types.py
```

## Quickstart

1. Install dependencies:

```bash
python -m pip install -r requirements.txt
```

2. Run normalization from sample text:

```bash
python main.py --input data/sample_record.txt --output output
```

3. Optional: run API server:

```bash
uvicorn api:app --reload
```

4. Generate claim outputs:

- `output/normalized_payload.json`
- `output/fhir_bundle.json`
- `output/reconciliation_report.json`

## API Endpoints

- `GET /health` - liveness check
- `POST /normalize/text` - normalize raw clinical text
- `POST /normalize/file` - normalize uploaded clinical document

## Next steps

- Add a production-grade Vision-Language ingestion module for PDF/scan layout parsing.
- Add interactive validation UI for coders to review agent outputs.
- Add an explainability layer that surfaces why each ICD/CPT mapping was chosen.
