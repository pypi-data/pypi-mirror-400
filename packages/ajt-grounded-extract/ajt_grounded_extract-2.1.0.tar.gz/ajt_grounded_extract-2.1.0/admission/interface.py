"""
Admission Interface

DEFAULT: STOP unless ALL conditions proven.
"""
from dataclasses import dataclass
from typing import Dict, Any, Optional


@dataclass
class AdmissionResult:
    """Result of admission evaluation."""
    allowed: bool
    reason: str
    token: Optional[Dict[str, Any]] = None


def CAN_PROCEED(action: str, payload: Dict[str, Any]) -> AdmissionResult:
    """
    Admission interface.

    DEFAULT: STOP
    Override only if ALL conditions proven.
    """
    # DEFAULT: STOP
    return AdmissionResult(
        allowed=False,
        reason="DEFAULT_STOP: no rule evaluated"
    )
