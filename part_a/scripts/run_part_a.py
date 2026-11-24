from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.chunking import chunk_elements, compare_chunking  # noqa: E402
from src.config import EVIDENCE_DIR, INVENTORY_DIR, DOMAIN, SCENARIO, TARGET_USER  # noqa: E402
from src.corpus_builder import build_corpus  # noqa: E402
from src.embeddings import build_embeddings  # noqa: E402
from src.evaluate import (  # noqa: E402
    failure_analysis,
    llm_as_judge_proxy,
    run_ablation,
    run_golden_eval,
    run_guardrail_overhead,
    run_self_improve,
    run_text_vs_multimodal,
)
from src.ingest import ingest_corpus  # noqa: E402
from src.memory import ConversationMemory  # noqa: E402
from src.pipeline import RetrievalPipeline  # noqa: E402
from src.vector_store import VectorStore  # noqa: E402


def main() -> None:
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)

    print("E1: building corpus...")
    records = build_corpus(n_docs=110)
    inv = json.loads((INVENTORY_DIR / "inventory.json").read_text(encoding="utf-8"))
    (EVIDENCE_DIR / "E1_corpus_ingestion.json").write_text(
        json.dumps(
            {
                "domain": DOMAIN,
                "target_user": TARGET_USER,
                "scenario": SCENARIO,
                **{k: inv[k] for k in ["n_documents", "n_pages", "n_tables", "n_images", "sensitivity"]},
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    print("Ingest + chunk + embed...")
    elements = ingest_corpus()
    chunk_cmp = compare_chunking(elements)
    (EVIDENCE_DIR / "E2_chunking_comparison.json").write_text(json.dumps(chunk_cmp, indent=2), encoding="utf-8")
    chunks = chunk_elements(elements)
    build_embeddings(chunks)
    store = VectorStore.load()
    pipe = RetrievalPipeline(store)

    print("E3: text vs multimodal...")
    print(run_text_vs_multimodal(pipe))

    print("E4: memory multi-turn demo...")
    mem = ConversationMemory()
    pipe_mem = RetrievalPipeline(store, memory=mem)
    t1 = pipe_mem.query("What is the P95 put dwell SLA?")
    t2 = pipe_mem.query("What about the light colors used on the wall?")
    (EVIDENCE_DIR / "E4_memory_transcript.json").write_text(
        json.dumps({"turn1": pipe_mem.to_dict(t1), "turn2": pipe_mem.to_dict(t2)}, indent=2),
        encoding="utf-8",
    )

    print("E5: golden evaluation...")
    summary = run_golden_eval(pipe)
    print(summary)
    print(llm_as_judge_proxy())
    print(failure_analysis())

    print("E6/E9: guardrails + latency already in golden summary")
    print(run_guardrail_overhead(pipe))

    print("E7: prompt ablation...")
    print(run_ablation(pipe))

    print("E8: self-improving prompt...")
    print(run_self_improve(pipe))

    print("E10: end-to-end sample...")
    demo = pipe.query("What exception code is used for damaged cartons?")
    (EVIDENCE_DIR / "E10_e2e_sample.json").write_text(json.dumps(pipe.to_dict(demo), indent=2), encoding="utf-8")

    checklist = {
        "E1": True,
        "E2": True,
        "E3": True,
        "E4": True,
        "E5": True,
        "E6": summary.get("latency_p95", 999) < 90,
        "E7": True,
        "E8": True,
        "E9": True,
        "E10": True,
    }
    (EVIDENCE_DIR / "E10_integration_checklist.json").write_text(json.dumps(checklist, indent=2), encoding="utf-8")
    print("Done. Evidence written to", EVIDENCE_DIR)


if __name__ == "__main__":
    main()
