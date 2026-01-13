"""
Token validator for execution layer.

Enforces:
- action match
- scope match
- reuse policy (forbidden)
- context_hash derivation (no manual supply)
- auto_revoke policy
"""
from dataclasses import dataclass
from typing import Dict, Any
import hashlib


@dataclass
class TokenValidation:
    """Result of token validation."""
    ok: bool
    reason: str


def derive_context_hash(query: str) -> str:
    """
    Derive context_hash from query.

    Must match admission/rules_rag_read.py derivation logic.
    """
    return hashlib.sha256(query.encode("utf-8")).hexdigest()


def validate_token_for_query(token: Dict[str, Any], query: str) -> TokenValidation:
    """
    Validate token for specific query.

    ALL checks must pass. ANY failure → STOP.
    """
    # 1. Action match
    if token.get("action") != "rag_read":
        return TokenValidation(False, "TOKEN_ACTION_MISMATCH")

    # 2. Scope match
    if token.get("scope") != "read_only":
        return TokenValidation(False, "TOKEN_SCOPE_MISMATCH")

    # 3. Reuse policy
    if token.get("reuse") != "forbidden":
        return TokenValidation(False, "TOKEN_REUSE_POLICY_VIOLATION")

    # 4. Auto-revoke policy
    if token.get("auto_revoke_on_context_change") is not True:
        return TokenValidation(False, "TOKEN_REVOKE_POLICY_MISSING")

    # 5. Context hash match
    expected = derive_context_hash(query)
    if token.get("context_hash") != expected:
        return TokenValidation(False, "CONTEXT_HASH_MISMATCH")

    return TokenValidation(True, "OK")
