"""
Minimal read-only retriever.

NO external dependencies.
NO synthesis.
NO chaining.

Returns raw evidence only.
"""
from dataclasses import dataclass
from typing import List
import os


@dataclass
class Evidence:
    """Single piece of evidence."""
    source: str
    snippet: str


def simple_grep_retrieve(query: str, corpus_dir: str, max_hits: int = 5) -> List[Evidence]:
    """
    Minimal read-only retriever.

    Scans .md/.txt files in corpus_dir.
    Returns snippets containing query terms.

    NO synthesis. NO ranking. NO LLM.
    Pure grep-like search.
    """
    # Extract terms (minimum 3 chars)
    terms = [t for t in query.lower().split() if len(t) >= 3]
    if not terms:
        return []

    hits: List[Evidence] = []

    # Walk directory
    for root, _, files in os.walk(corpus_dir):
        for fn in files:
            if not (fn.endswith(".md") or fn.endswith(".txt")):
                continue

            path = os.path.join(root, fn)
            try:
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    text = f.read()
            except Exception:
                continue

            low = text.lower()

            # Check if any term matches
            if any(t in low for t in terms):
                # Find first match position
                idx = min((low.find(t) for t in terms if low.find(t) != -1), default=-1)
                if idx == -1:
                    continue

                # Extract snippet around first match
                start = max(0, idx - 120)
                end = min(len(text), idx + 280)
                snippet = text[start:end].replace("\n", " ")

                hits.append(Evidence(source=path, snippet=snippet))

                if len(hits) >= max_hits:
                    return hits

    return hits
