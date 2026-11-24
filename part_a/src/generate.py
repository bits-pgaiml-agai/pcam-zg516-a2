from __future__ import annotations

import re
from dataclasses import dataclass

import httpx

from .config import LLM_BACKEND, OLLAMA_BASE_URL, OLLAMA_MODEL
from .vector_store import Hit


@dataclass
class GenerationResult:
    answer: str
    citations: list[str]
    input_tokens: int
    output_tokens: int
    backend: str


def _estimate_tokens(text: str) -> int:
    return max(1, len(text.split()))


def _citations(hits: list[Hit]) -> list[str]:
    seen: list[str] = []
    for h in hits:
        cite = f"{h.chunk.source} p.{h.chunk.page}"
        if cite not in seen:
            seen.append(cite)
    return seen


def _best_span(query: str, hits: list[Hit]) -> tuple[str, Hit]:
    stop = {
        "what", "when", "where", "which", "how", "does", "the", "and", "for", "from",
        "with", "that", "this", "have", "must", "into", "about", "used", "each",
    }
    q_terms = {
        t.lower()
        for t in re.findall(r"[A-Za-z0-9_+%-]+", query)
        if len(t) > 2 and t.lower() not in stop
    }
    best_sent = ""
    best_hit = hits[0]
    best_score = -1.0
    for h in hits:
        text = h.chunk.text.replace("\n", " ").strip()
        sentences = [text] if len(text) < 320 else re.split(r"(?<=[.!?])\s+", text)
        for s in sentences:
            s_clean = s.strip(" •\t")
            if len(s_clean) < 20:
                continue
            low = s_clean.lower()
            if any(x in low for x in ("synthetic wes handbook", "key facts", "type:", "topic:")):
                continue
            overlap = sum(1 for t in q_terms if t in low)
            score = overlap * 1.5 + 0.2 * h.score
            if "sla" in q_terms and "sla" in low:
                score += 2.0
            if "diagram" in q_terms and "diagram" in low:
                score += 2.0
            if overlap >= max(2, len(q_terms) // 2):
                score += 1.5
            if score > best_score:
                best_score = score
                best_sent = s_clean
                best_hit = h
    if not best_sent:
        best_sent = hits[0].chunk.text[:240]
        best_hit = hits[0]
    return best_sent, best_hit


def _mock_answer(query: str, hits: list[Hit]) -> GenerationResult:
    if not hits:
        return GenerationResult(
            answer="Insufficient evidence in the corpus to answer this question.",
            citations=[],
            input_tokens=_estimate_tokens(query),
            output_tokens=12,
            backend="mock",
        )
    span, best_hit = _best_span(query, hits)
    cites = _citations([best_hit] + [h for h in hits if h is not best_hit])[:3]
    answer = f"{span} Source: {cites[0]}."
    prompt_proxy = query + " " + " ".join(h.chunk.text for h in hits[:3])
    return GenerationResult(
        answer=answer,
        citations=cites,
        input_tokens=_estimate_tokens(prompt_proxy),
        output_tokens=_estimate_tokens(answer),
        backend="mock",
    )


def _ollama_answer(prompt: str, hits: list[Hit]) -> GenerationResult:
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.0, "seed": 42},
    }
    with httpx.Client(timeout=120.0) as client:
        r = client.post(f"{OLLAMA_BASE_URL}/api/generate", json=payload)
        r.raise_for_status()
        data = r.json()
    text = data.get("response", "").strip()
    cites = _citations(hits[:3])
    if cites and cites[0] not in text:
        text = f"{text} [{cites[0]}]"
    return GenerationResult(
        answer=text or "Insufficient evidence.",
        citations=cites,
        input_tokens=int(data.get("prompt_eval_count") or _estimate_tokens(prompt)),
        output_tokens=int(data.get("eval_count") or _estimate_tokens(text)),
        backend=f"ollama:{OLLAMA_MODEL}",
    )


def generate(prompt: str, hits: list[Hit], backend: str | None = None) -> GenerationResult:
    backend = backend or LLM_BACKEND
    if backend == "ollama":
        try:
            return _ollama_answer(prompt, hits)
        except Exception:
            return _mock_answer(prompt, hits)
    return _mock_answer(prompt, hits)
