from __future__ import annotations

import json
from dataclasses import asdict, dataclass

from .config import EVIDENCE_DIR
from .prompts import SYSTEM_POLICY


@dataclass
class OptStep:
    iteration: int
    prompt_prefix: str
    score: float
    change: str


def _score(preds: list[str], golds: list[str]) -> float:
    if not preds:
        return 0.0
    hits = 0
    for p, g in zip(preds, golds):
        g_terms = {t.lower() for t in g.split() if len(t) > 3}
        if not g_terms:
            continue
        overlap = sum(1 for t in g_terms if t in p.lower())
        if overlap / max(1, len(g_terms)) >= 0.3:
            hits += 1
    return hits / len(preds)


def optimize_prompt(
    base_policy: str,
    dev_queries: list[str],
    dev_answers: list[str],
    run_fn,
    max_iters: int = 3,
) -> list[OptStep]:
    """
    Lightweight self-improving loop (critique-and-rewrite).
    run_fn(prompt_prefix, query) -> predicted answer string.
    """
    prefix = base_policy or SYSTEM_POLICY
    history: list[OptStep] = []
    critiques = [
        "Add explicit instruction to refuse when evidence is missing.",
        "Require filename and page citation on every sentence with a fact.",
        "Prefer table cells verbatim when the question asks for a numeric SLA or capacity.",
    ]

    for i in range(max_iters):
        change = "baseline" if i == 0 else critiques[min(i - 1, len(critiques) - 1)]
        if i > 0:
            prefix = prefix + " " + critiques[min(i - 1, len(critiques) - 1)]
        preds = [run_fn(prefix, q) for q in dev_queries]
        score = _score(preds, dev_answers)
        history.append(OptStep(iteration=i + 1, prompt_prefix=prefix, score=score, change=change))

    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    out = EVIDENCE_DIR / "E8_self_improve_log.json"
    out.write_text(json.dumps([asdict(h) for h in history], indent=2), encoding="utf-8")
    return history
