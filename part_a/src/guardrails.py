from __future__ import annotations

import re
import time
from dataclasses import dataclass


INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?previous\s+instructions",
    r"system\s*prompt",
    r"reveal\s+(your|the)\s+(system|hidden)\s+prompt",
    r"jailbreak",
    r"do\s+anything\s+now",
]

PII_PATTERNS = [
    r"\b\d{3}-\d{2}-\d{4}\b",
    r"\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b",
    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
]

OUT_OF_SCOPE = [
    "bitcoin",
    "crypto wallet",
    "write malware",
    "medical diagnosis",
    "legal advice for lawsuit",
]


@dataclass
class GuardResult:
    allowed: bool
    reason: str
    elapsed_sec: float


def check_input(query: str) -> GuardResult:
    t0 = time.perf_counter()
    q = query.lower()
    for pat in INJECTION_PATTERNS:
        if re.search(pat, q):
            return GuardResult(False, "prompt_injection", time.perf_counter() - t0)
    for pat in PII_PATTERNS:
        if re.search(pat, query):
            return GuardResult(False, "personal_data", time.perf_counter() - t0)
    for phrase in OUT_OF_SCOPE:
        if phrase in q:
            return GuardResult(False, "out_of_scope", time.perf_counter() - t0)
    return GuardResult(True, "ok", time.perf_counter() - t0)


def check_output(answer: str, citations: list[str]) -> GuardResult:
    t0 = time.perf_counter()
    if not answer.strip():
        return GuardResult(False, "empty_answer", time.perf_counter() - t0)
    if not citations:
        return GuardResult(False, "missing_citation", time.perf_counter() - t0)
    low = answer.lower()
    if "i made this up" in low or "as an ai" in low and "no evidence" in low:
        return GuardResult(False, "ungrounded", time.perf_counter() - t0)
    return GuardResult(True, "ok", time.perf_counter() - t0)
