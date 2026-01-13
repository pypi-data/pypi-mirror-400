"""
Evidence grounding module: map extracted values to document spans.
"""
from typing import Dict, List, Optional


class EvidenceGrounder:
    """Ground extracted values to exact document evidence."""

    def __init__(self, document_data: Dict):
        self.content = document_data["content"]
        self.line_index = document_data["line_index"]

    def ground_candidate(self, candidate: Dict) -> Dict:
        """
        Add evidence grounding to candidate.

        Returns enhanced candidate with:
        - evidence.quote: exact text
        - evidence.start: start offset
        - evidence.end: end offset
        - evidence.line: line number
        - evidence.context: surrounding text
        """
        start = candidate["start_offset"]
        end = candidate["end_offset"]

        # Extract exact quote
        quote = self.content[start:end]

        # Find line number
        line_num = self._find_line(start)

        # Get context (±50 chars)
        context_start = max(0, start - 50)
        context_end = min(len(self.content), end + 50)
        context = self.content[context_start:context_end]

        evidence = {
            "quote": quote,
            "start": start,
            "end": end,
            "line": line_num,
            "context": context,
            "context_start": context_start,
            "context_end": context_end
        }

        # Add evidence to candidate
        grounded = candidate.copy()
        grounded["evidence"] = evidence

        return grounded

    def _find_line(self, offset: int) -> Optional[int]:
        """Find line number for offset."""
        for idx in self.line_index:
            if idx["start"] <= offset < idx["end"]:
                return idx["line"]
        return None

    def verify_evidence(self, grounded: Dict) -> Dict:
        """
        Verify evidence integrity.

        Returns verification result with:
        - valid: bool
        - issues: list of problems
        """
        issues = []

        evidence = grounded.get("evidence", {})

        # Check quote matches offset range
        expected_quote = self.content[
            evidence["start"]:evidence["end"]
        ]
        if evidence["quote"] != expected_quote:
            issues.append("Quote mismatch with offset range")

        # Check value appears in quote
        value = grounded.get("value", "")
        if value not in evidence.get("quote", ""):
            issues.append("Value not found in evidence quote")

        return {
            "valid": len(issues) == 0,
            "issues": issues
        }
