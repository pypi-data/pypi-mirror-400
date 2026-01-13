"""
Execution layer for conditional actions.

Step ②-1: Read-only retrieval execution.
"""

__version__ = "0.1.0"

from .token_validator import TokenValidation, validate_token_for_query
from .retriever import Evidence, simple_grep_retrieve
from .rag_read_gate import rag_read

__all__ = [
    "TokenValidation",
    "validate_token_for_query",
    "Evidence",
    "simple_grep_retrieve",
    "rag_read",
]
