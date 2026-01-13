"""
Lightweight intent detection.

NOT for accuracy. Only for detecting scope mismatch.
"""


def detect_intent(query: str) -> str:
    """
    Detect user intent from query.

    Returns:
        "synthesis" | "execution" | "analysis" | "retrieval_only"

    This is NOT intelligent NLP. This is heuristic mismatch detection.
    """
    q = query.lower()

    # Synthesis indicators
    if any(k in q for k in ["요약", "결론", "합쳐", "정리", "summary", "conclude"]):
        return "synthesis"

    # Execution indicators
    if any(k in q for k in ["실행", "보내", "만들어", "execute", "send", "create"]):
        return "execution"

    # Analysis indicators
    if any(k in q for k in ["분석", "허점", "찾아", "analyze", "find"]):
        return "analysis"

    # Default: retrieval only
    return "retrieval_only"
