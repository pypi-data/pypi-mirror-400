"""
RAG read gate: admission → validation → retrieval.

NO synthesis.
NO chaining.
NO downstream actions.

Returns raw evidence only.
"""
from typing import Dict, Any
import sys
import json
import uuid
import datetime
from pathlib import Path

# Import from admission (frozen)
sys.path.insert(0, str(Path(__file__).parent.parent))
from admission.rules_rag_read import evaluate_rag_read

# Import from execution (this layer)
from .token_validator import validate_token_for_query
from .retriever import simple_grep_retrieve

# Import from audit (②-2)
from audit.intent_detector import detect_intent


# --- AUDIT START ---
def _emit_audit(event: dict):
    """Emit audit event to stdout (append-only, no interpretation)."""
    event["timestamp"] = datetime.datetime.utcnow().isoformat()
    event["proof_id"] = str(uuid.uuid4())
    print(json.dumps(event, ensure_ascii=False))
# --- AUDIT END ---


def rag_read(request: Dict[str, Any], corpus_dir: str) -> Dict[str, Any]:
    """
    Execute rag_read with full admission and token validation.

    Flow:
    1. Admission evaluation (from frozen ②-0)
    2. Token validation
    3. Retrieval execution (if token valid)
    4. Return raw evidence (NO synthesis)

    Returns:
        {
            "allowed": bool,
            "reason": str,
            "token": dict or None,
            "evidence": list of {"source": str, "snippet": str}
        }
    """
    # Step 1: Admission
    admission = evaluate_rag_read(request)
    if not admission.allowed:
        # --- AUDIT START ---
        _emit_audit({
            "action": "rag_read",
            "decision_maker": request.get("decision_maker"),
            "admission": {
                "allowed": False,
                "reason_code": admission.reason,
                "constitutional_rule": "ADMISSION_FAILED"
            }
        })
        # --- AUDIT END ---

        return {
            "allowed": False,
            "reason": admission.reason,
            "token": None,
            "evidence": []
        }

    # Step 2: Token validation
    token = admission.token
    query = request["query"]

    tv = validate_token_for_query(token, query)
    if not tv.ok:
        # --- AUDIT START ---
        _emit_audit({
            "action": "rag_read",
            "decision_maker": request.get("decision_maker"),
            "admission": {
                "allowed": False,
                "reason_code": f"TOKEN_INVALID: {tv.reason}",
                "constitutional_rule": "TOKEN_CONSTRAINT"
            }
        })
        # --- AUDIT END ---

        return {
            "allowed": False,
            "reason": f"TOKEN_INVALID: {tv.reason}",
            "token": None,
            "evidence": []
        }

    # Step 3: Retrieval (read-only)
    evidence = simple_grep_retrieve(query=query, corpus_dir=corpus_dir, max_hits=5)

    # Step 4: Return raw evidence
    # IMPORTANT: NO synthesis, NO chaining, NO downstream actions

    # --- AUDIT START ---
    intent = detect_intent(query)
    _emit_audit({
        "action": "rag_read",
        "decision_maker": request["decision_maker"],
        "admission": {
            "allowed": True,
            "reason_code": "RAG_READ_EXECUTED_READ_ONLY",
            "constitutional_rule": "NO_SYNTHESIS"
        },
        "intent_vs_scope": {
            "detected_intent": intent,
            "granted_scope": "read_only",
            "scope_mismatch": intent != "retrieval_only"
        },
        "retrieval": {
            "evidence_count": len(evidence),
            "zero_results_reason": (
                "language_mismatch" if len(evidence) == 0 else None
            )
        },
        "next_action_hint": {
            "suggested_scope": "synthesis" if intent != "retrieval_only" else None,
            "required_action": "request_new_action" if intent != "retrieval_only" else None
        }
    })
    # --- AUDIT END ---

    return {
        "allowed": True,
        "reason": "RAG_READ_EXECUTED_READ_ONLY",
        "token": token,
        "evidence": [{"source": e.source, "snippet": e.snippet} for e in evidence]
    }
