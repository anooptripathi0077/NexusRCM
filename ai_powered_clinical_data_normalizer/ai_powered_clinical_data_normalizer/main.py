from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.nexus_rcm.pipeline import NexusRCMPipeline


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="NexusRCM MVP pipeline runner")
    parser.add_argument("--input", required=True, help="Path to input clinical text file")
    parser.add_argument("--output", default="output", help="Output directory")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_path = Path(args.input)
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    pipeline = NexusRCMPipeline()
    result = pipeline.run(input_path=input_path)

    (output_dir / "normalized_payload.json").write_text(
        json.dumps(result["normalized_payload"], indent=2), encoding="utf-8"
    )
    (output_dir / "fhir_bundle.json").write_text(
        json.dumps(result["fhir_bundle"], indent=2), encoding="utf-8"
    )
    (output_dir / "reconciliation_report.json").write_text(
        json.dumps(result["reconciliation_report"], indent=2), encoding="utf-8"
    )

    print("Pipeline completed successfully.")
    print(f"Outputs written to: {output_dir.resolve()}")


if __name__ == "__main__":
    main()
