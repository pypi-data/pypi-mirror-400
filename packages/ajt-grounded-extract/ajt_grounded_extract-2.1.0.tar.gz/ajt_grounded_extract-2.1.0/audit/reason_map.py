"""
Reason code to human explanation mapping.

From observation: reason codes are machine-readable but human-incomprehensible.
This maps constitutional rules to human explanations.
"""

REASON_EXPLANATION = {
    "NO_SYNTHESIS": {
        "human": "Synthesis is forbidden by constitution for read_only scope.",
        "how_to_proceed": "Request a new action with scope: synthesis.",
        "constitutional_reference": "STEP_2_1_RAG_EXECUTION.md - DoD: NO_SYNTHESIS"
    },
    "NO_CHAINING": {
        "human": "Chaining to downstream actions is forbidden.",
        "how_to_proceed": "Request each action separately with individual admission.",
        "constitutional_reference": "STEP_2_1_RAG_EXECUTION.md - DoD: NO_CHAINING"
    },
    "ADMISSION_FAILED": {
        "human": "Admission requirements not met.",
        "how_to_proceed": "Check required fields: decision_maker, why, scope, query.",
        "constitutional_reference": "STEP_2_0_RAG_ADMISSION.md - Rules"
    },
    "TOKEN_CONSTRAINT": {
        "human": "Token validation failed (scope, reuse, or context_hash mismatch).",
        "how_to_proceed": "Request new token with matching context.",
        "constitutional_reference": "STEP_2_1_RAG_EXECUTION.md - Token Validator"
    }
}
