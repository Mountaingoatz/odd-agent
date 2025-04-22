"""
Very‑lightweight document classifier.

Heuristics based on filename + first‑page keywords.
Categories:
  DDQ | News Article | Regulatory Filing | Financial Statement
  Pitch Deck | Portfolio Data | Other
"""
from __future__ import annotations
import os, re
from typing import Literal

Category = Literal[
    "DDQ", "News Article", "Regulatory Filing",
    "Financial Statement", "Pitch Deck",
    "Portfolio Data", "Other"
]

_KEYWORDS = {
    "DDQ":       (r"\bddq\b",),
    "Regulatory Filing": (r"\b13f\b", r"\bform\s+adv\b", r"\badv\b"),
    "Financial Statement": (r"statement of operations", r"income statement",
                            r"balance sheet", r"financial statements?"),
    "Pitch Deck": (r"pitch deck", r"investor presentation", r"marketing deck"),
    "Portfolio Data": (r"portfolio holdings?", r"position list"),
    "News Article": (r"\b(reuters|bloomberg|ft\.com|wall street journal)\b",),
}

def classify(path: str, first_page_text: str | None = None) -> Category:
    name = os.path.basename(path).lower()

    def match(patterns):
        target = f"{name}  {first_page_text or ''}".lower()
        return any(re.search(p, target) for p in patterns)

    for cat, patterns in _KEYWORDS.items():
        if match(patterns):
            return cat                        # type: ignore
    return "Other"                           # type: ignore
