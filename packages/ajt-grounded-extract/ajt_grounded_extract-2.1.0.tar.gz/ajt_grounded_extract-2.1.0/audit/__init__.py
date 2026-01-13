"""
Audit system for ②-2.

Logs why system stopped, not what it did.
"""

__version__ = "0.1.0"

from .intent_detector import detect_intent
from .reason_map import REASON_EXPLANATION

__all__ = [
    "detect_intent",
    "REASON_EXPLANATION",
]
