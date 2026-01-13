"""
Document ingestion module: load, normalize, hash, index.
"""
import hashlib
import json
from pathlib import Path
from typing import Dict, List, Optional


class DocumentIngestor:
    """Load and normalize document for extraction."""

    def __init__(self, document_path: str):
        self.path = Path(document_path)
        self.content: Optional[str] = None
        self.content_hash: Optional[str] = None
        self.line_index: List[Dict[str, int]] = []

    def load(self) -> Dict:
        """Load document and compute metadata."""
        if not self.path.exists():
            raise FileNotFoundError(f"Document not found: {self.path}")

        # Read content
        with open(self.path, 'r', encoding='utf-8') as f:
            self.content = f.read()

        # Compute hash
        self.content_hash = hashlib.sha256(
            self.content.encode('utf-8')
        ).hexdigest()

        # Build line index
        self._build_line_index()

        return {
            "path": str(self.path),
            "content": self.content,
            "content_hash": self.content_hash,
            "line_index": self.line_index,
            "size_bytes": len(self.content.encode('utf-8'))
        }

    def _build_line_index(self):
        """Build line->offset mapping for evidence grounding."""
        offset = 0
        for line_num, line in enumerate(self.content.split('\n'), start=1):
            self.line_index.append({
                "line": line_num,
                "start": offset,
                "end": offset + len(line),
                "text": line
            })
            offset += len(line) + 1  # +1 for newline

    def get_span_text(self, start: int, end: int) -> str:
        """Extract text from offset range."""
        return self.content[start:end]

    def find_line_for_offset(self, offset: int) -> Optional[int]:
        """Find line number for given offset."""
        for idx in self.line_index:
            if idx["start"] <= offset < idx["end"]:
                return idx["line"]
        return None
