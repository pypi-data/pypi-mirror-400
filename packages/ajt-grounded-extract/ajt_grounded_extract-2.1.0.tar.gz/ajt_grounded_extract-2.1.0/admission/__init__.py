"""
Admission system for conditional action authorization.

Step ②-0: Minimal control structure for read-only RAG.
"""

__version__ = "0.1.0"

from .interface import AdmissionResult, CAN_PROCEED
from .rules_rag_read import evaluate_rag_read

__all__ = [
    "AdmissionResult",
    "CAN_PROCEED",
    "evaluate_rag_read",
]
