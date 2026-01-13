"""
Extraction module: find candidate values using rules or LLM.
"""
import re
from typing import Dict, List, Optional


class RuleBasedExtractor:
    """Extract field values using regex patterns."""

    def __init__(self, schema: Dict):
        self.schema = schema

    def extract(self, content: str) -> List[Dict]:
        """
        Extract candidates for all schema fields.

        Returns list of candidates with:
        - field_name
        - value
        - start_offset
        - end_offset
        - confidence
        """
        candidates = []

        for field in self.schema.get("fields", []):
            field_candidates = self._extract_field(content, field)
            candidates.extend(field_candidates)

        return candidates

    def _extract_field(self, content: str, field: Dict) -> List[Dict]:
        """Extract candidates for a specific field."""
        field_name = field["name"]
        candidates = []

        # Example: effective_date extraction
        if field_name == "effective_date":
            candidates.extend(self._extract_effective_date(content))

        return candidates

    def _extract_effective_date(self, content: str) -> List[Dict]:
        """Extract effective date candidates."""
        candidates = []

        # Pattern 1: "Effective Date: MM/DD/YYYY"
        pattern1 = r'(?i)effective\s+date\s*[:]\s*(\d{1,2}/\d{1,2}/\d{4})'
        for match in re.finditer(pattern1, content):
            candidates.append({
                "field_name": "effective_date",
                "value": match.group(1),
                "start_offset": match.start(1),
                "end_offset": match.end(1),
                "confidence": 0.9,
                "pattern": "explicit_label"
            })

        # Pattern 2: "effective as of YYYY-MM-DD"
        pattern2 = r'(?i)effective\s+as\s+of\s+(\d{4}-\d{2}-\d{2})'
        for match in re.finditer(pattern2, content):
            candidates.append({
                "field_name": "effective_date",
                "value": match.group(1),
                "start_offset": match.start(1),
                "end_offset": match.end(1),
                "confidence": 0.85,
                "pattern": "phrase_match"
            })

        # Pattern 3: "becomes effective on [written date]"
        pattern3 = r'(?i)becomes\s+effective\s+on\s+([A-Z][a-z]+\s+\d{1,2},\s+\d{4})'
        for match in re.finditer(pattern3, content):
            candidates.append({
                "field_name": "effective_date",
                "value": match.group(1),
                "start_offset": match.start(1),
                "end_offset": match.end(1),
                "confidence": 0.8,
                "pattern": "written_form"
            })

        return candidates
