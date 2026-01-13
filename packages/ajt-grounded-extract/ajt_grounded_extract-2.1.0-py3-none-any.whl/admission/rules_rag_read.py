"""
Rules for rag_read action.

Conditional authorization for read-only retrieval.
"""
import hashlib
from typing import Dict, Any
from .interface import AdmissionResult


REQUIRED_FIELDS = ["decision_maker", "why", "scope", "query"]


def evaluate_rag_read(payload: Dict[str, Any]) -> AdmissionResult:
    """
    Evaluate admission for rag_read action.

    ALL conditions must be proven. Failure of ANY condition → STOP.
    """
    # 1. Required field validation
    for field in REQUIRED_FIELDS:
        if field not in payload:
            return AdmissionResult(
                allowed=False,
                reason=f"MISSING_FIELD: {field}"
            )

    # 2. Scope restriction
    if payload["scope"] != "read_only":
        return AdmissionResult(
            allowed=False,
            reason="INVALID_SCOPE: only read_only allowed"
        )

    # 3. context_hash automatic derivation
    # Manual supply of context_hash invalidates token
    if "context_hash" in payload:
        return AdmissionResult(
            allowed=False,
            reason="MANUAL_HASH_REJECTED: context_hash must be auto-derived"
        )

    raw = payload["query"].encode("utf-8")
    context_hash = hashlib.sha256(raw).hexdigest()

    # 4. Token issuance
    token = {
        "action": "rag_read",
        "scope": "read_only",
        "reuse": "forbidden",
        "context_hash": context_hash,
        "decision_maker": payload["decision_maker"],
        "auto_revoke_on_context_change": True,
    }

    return AdmissionResult(
        allowed=True,
        reason="ALL_CONDITIONS_PROVEN",
        token=token
    )
