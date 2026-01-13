"""
Archive module: write-once evidence artifacts with timestamps and hashes.
"""
import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List


class EvidenceArchive:
    """Write-once artifact storage with integrity guarantees."""

    def __init__(self, archive_dir: str = "evidence"):
        self.archive_dir = Path(archive_dir)
        self.archive_dir.mkdir(exist_ok=True)

    def archive_extraction(
        self,
        document_data: Dict,
        results: List[Dict]
    ) -> Dict:
        """
        Archive extraction results as write-once artifacts.

        Creates:
        - extraction_{timestamp}.jsonl: line-delimited extraction results
        - manifest_{timestamp}.json: metadata and integrity hashes
        """
        timestamp = datetime.now(timezone.utc).isoformat()
        safe_timestamp = timestamp.replace(":", "-").replace(".", "-")

        # Prepare extraction record
        extraction_record = {
            "timestamp": timestamp,
            "document": {
                "path": document_data["path"],
                "content_hash": document_data["content_hash"],
                "size_bytes": document_data["size_bytes"]
            },
            "results": results,
            "trace_signature": self._compute_trace_signature(
                document_data, results
            )
        }

        # Write JSONL (one result per line)
        jsonl_path = self.archive_dir / f"extraction_{safe_timestamp}.jsonl"
        with open(jsonl_path, 'w') as f:
            for result in results:
                f.write(json.dumps(result) + '\n')

        # Compute JSONL hash
        jsonl_hash = self._hash_file(jsonl_path)

        # Create manifest
        manifest = {
            "timestamp": timestamp,
            "document_hash": document_data["content_hash"],
            "extraction_file": str(jsonl_path),
            "extraction_hash": jsonl_hash,
            "result_count": len(results),
            "stop_events": [
                r for r in results if r["decision"] == "STOP"
            ],
            "accept_events": [
                r for r in results if r["decision"] == "ACCEPT"
            ],
            "trace_signature": extraction_record["trace_signature"]
        }

        # Write manifest
        manifest_path = self.archive_dir / f"manifest_{safe_timestamp}.json"
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)

        return {
            "jsonl_path": str(jsonl_path),
            "manifest_path": str(manifest_path),
            "timestamp": timestamp,
            "trace_signature": extraction_record["trace_signature"]
        }

    def _compute_trace_signature(
        self,
        document_data: Dict,
        results: List[Dict]
    ) -> str:
        """
        Compute unique signature for extraction trace.

        Combines document hash + results hash for tamper detection.
        """
        doc_hash = document_data["content_hash"]
        results_json = json.dumps(results, sort_keys=True)
        results_hash = hashlib.sha256(
            results_json.encode('utf-8')
        ).hexdigest()

        combined = f"{doc_hash}:{results_hash}"
        return hashlib.sha256(combined.encode('utf-8')).hexdigest()

    def _hash_file(self, path: Path) -> str:
        """Compute SHA-256 hash of file."""
        sha256 = hashlib.sha256()
        with open(path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                sha256.update(chunk)
        return sha256.hexdigest()
