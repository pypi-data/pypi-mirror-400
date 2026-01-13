"""
Main extraction pipeline: ingest → extract → ground → judge → archive.
"""
import json
from pathlib import Path
from typing import Dict, List

from engine.ingest import DocumentIngestor
from engine.extract import RuleBasedExtractor
from engine.ground import EvidenceGrounder
from engine.judge import ExtractionJudge
from engine.archive import EvidenceArchive


class ExtractionPipeline:
    """End-to-end extraction with STOP-first judgment."""

    def __init__(self, schema_path: str = "schema/extraction_schema.json"):
        with open(schema_path, 'r') as f:
            self.schema = json.load(f)

        self.extractor = RuleBasedExtractor(self.schema)
        self.judge = ExtractionJudge(self.schema)
        self.archive = EvidenceArchive()

    def run(self, document_path: str) -> Dict:
        """
        Run full extraction pipeline.

        Returns:
        - results: list of field decisions
        - artifact_refs: paths to archived evidence
        - summary: counts and statistics
        """
        # 1. Ingest
        print(f"[INGEST] Loading {document_path}...")
        ingestor = DocumentIngestor(document_path)
        document_data = ingestor.load()
        print(f"  → Hash: {document_data['content_hash'][:16]}...")

        # 2. Extract candidates
        print("[EXTRACT] Finding candidates...")
        candidates = self.extractor.extract(document_data["content"])
        print(f"  → Found {len(candidates)} candidates")

        # 3. Ground evidence
        print("[GROUND] Mapping evidence...")
        grounder = EvidenceGrounder(document_data)
        grounded = []
        for candidate in candidates:
            g = grounder.ground_candidate(candidate)
            verification = grounder.verify_evidence(g)
            g["verification"] = verification
            grounded.append(g)

        # 4. Judge (STOP-first)
        print("[JUDGE] Making decisions...")
        results = []
        for field in self.schema["fields"]:
            field_name = field["name"]
            field_candidates = [
                c for c in grounded if c["field_name"] == field_name
            ]
            decision = self.judge.judge(field_name, field_candidates)
            results.append(decision)
            print(f"  → {field_name}: {decision['decision']}")

        # 5. Archive
        print("[ARCHIVE] Writing artifacts...")
        archive_info = self.archive.archive_extraction(
            document_data, results
        )
        print(f"  → Manifest: {archive_info['manifest_path']}")

        # Summary
        summary = {
            "total_fields": len(results),
            "accepted": sum(1 for r in results if r["decision"] == "ACCEPT"),
            "stopped": sum(1 for r in results if r["decision"] == "STOP"),
            "need_review": sum(
                1 for r in results if r["decision"] == "NEED_REVIEW"
            )
        }

        return {
            "results": results,
            "artifact_refs": archive_info,
            "summary": summary,
            "document": {
                "path": document_path,
                "hash": document_data["content_hash"]
            }
        }
