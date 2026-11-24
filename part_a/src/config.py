from __future__ import annotations

import os
from pathlib import Path

PART_A_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PART_A_ROOT / "data"
CORPUS_DIR = DATA_DIR / "corpus_synthetic"
INVENTORY_DIR = DATA_DIR / "corpus_inventory"
GOLDEN_DIR = DATA_DIR / "golden_set"
ONTOLOGY_DIR = DATA_DIR / "ontology"
EVIDENCE_DIR = PART_A_ROOT / "evidence"
INDEX_DIR = DATA_DIR / "index"

SEED = 42
CHUNK_SIZE = 450
CHUNK_OVERLAP = 60
TOP_K = 8
EMBEDDING_BACKEND = "tfidf"
LLM_BACKEND = os.environ.get("LLM_BACKEND", "mock")
OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "qwen2.5:1.5b-instruct")
P95_LATENCY_BUDGET_SEC = 90.0
GUARDRAIL_OVERHEAD_BUDGET_SEC = 6.0

DOMAIN = "Warehouse Execution System (WES) — synthetic operations handbook"
TARGET_USER = "Warehouse operations analyst / floor supervisor"
SCENARIO = (
    "Answer operational questions from WES SOPs, put-wall guides, ASN flows, "
    "exception playbooks and diagram callouts — with citations — without fine-tuning."
)
