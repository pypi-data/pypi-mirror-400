"""
STOP-first judgment module: decide ACCEPT | STOP | NEED_REVIEW.
"""
from typing import Dict, List, Optional
from enum import Enum


class Decision(str, Enum):
    """Extraction decision taxonomy."""
    ACCEPT = "ACCEPT"
    STOP = "STOP"
    NEED_REVIEW = "NEED_REVIEW"


class StopReason(str, Enum):
    """Why extraction was stopped."""
    NO_CANDIDATES = "no_candidates_found"
    INSUFFICIENT_CONFIDENCE = "insufficient_confidence"
    CONFLICTING_VALUES = "conflicting_values"
    MISSING_EVIDENCE = "missing_evidence"
    EVIDENCE_INTEGRITY_FAILED = "evidence_integrity_failed"


class ExtractionJudge:
    """STOP-first decision engine."""

    def __init__(self, schema: Dict):
        self.schema = schema
        self.requirements = schema.get("evidence_requirements", {})
        self.min_confidence = self.requirements.get("min_confidence", 0.7)
        self.stop_on_conflict = self.requirements.get("stop_on_conflict", True)

    def judge(self, field_name: str, candidates: List[Dict]) -> Dict:
        """
        Make STOP-first decision for a field.

        Returns:
        - decision: ACCEPT | STOP | NEED_REVIEW
        - value: extracted value (if ACCEPT)
        - evidence: evidence object (if ACCEPT)
        - confidence: final confidence
        - stop_reason: why stopped (if STOP)
        - stop_proof: evidence of why stopped
        """
        # Rule 1: No candidates → STOP
        if not candidates:
            return self._stop(
                field_name,
                StopReason.NO_CANDIDATES,
                {"searched": True, "candidates_found": 0}
            )

        # Rule 2: Conflicting values → STOP
        if self.stop_on_conflict:
            unique_values = set(c["value"] for c in candidates)
            if len(unique_values) > 1:
                return self._stop(
                    field_name,
                    StopReason.CONFLICTING_VALUES,
                    {
                        "candidates": [
                            {
                                "value": c["value"],
                                "confidence": c["confidence"],
                                "evidence": c.get("evidence", {}).get("quote")
                            }
                            for c in candidates
                        ]
                    }
                )

        # Rule 3: Insufficient confidence → STOP
        best_candidate = max(candidates, key=lambda c: c["confidence"])
        if best_candidate["confidence"] < self.min_confidence:
            return self._stop(
                field_name,
                StopReason.INSUFFICIENT_CONFIDENCE,
                {
                    "threshold": self.min_confidence,
                    "actual": best_candidate["confidence"],
                    "value": best_candidate["value"]
                }
            )

        # Rule 4: Missing evidence → STOP
        if "evidence" not in best_candidate:
            return self._stop(
                field_name,
                StopReason.MISSING_EVIDENCE,
                {"value": best_candidate["value"]}
            )

        # Rule 5: Evidence integrity check
        verification = best_candidate.get("verification", {})
        if not verification.get("valid", True):
            return self._stop(
                field_name,
                StopReason.EVIDENCE_INTEGRITY_FAILED,
                {
                    "issues": verification.get("issues", []),
                    "value": best_candidate["value"]
                }
            )

        # All checks passed → ACCEPT
        return self._accept(field_name, best_candidate)

    def _accept(self, field_name: str, candidate: Dict) -> Dict:
        """Create ACCEPT decision."""
        return {
            "field_name": field_name,
            "decision": Decision.ACCEPT,
            "value": candidate["value"],
            "evidence": candidate["evidence"],
            "confidence": candidate["confidence"],
            "stop_reason": None,
            "stop_proof": None
        }

    def _stop(
        self,
        field_name: str,
        reason: StopReason,
        proof: Dict
    ) -> Dict:
        """Create STOP decision with negative proof."""
        return {
            "field_name": field_name,
            "decision": Decision.STOP,
            "value": None,
            "evidence": None,
            "confidence": 0.0,
            "stop_reason": reason.value,
            "stop_proof": proof
        }
