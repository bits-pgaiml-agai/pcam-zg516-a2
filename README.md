# pcam-zg516-a2

**BITS Pilani WILP · PGAIML · PCAM\* ZG516 Applied Generative AI**  
**Group Major Project / Assignment-2 · Group 15**

| Part | Title | Mode | Marks |
|------|-------|------|-------|
| **A** | Multimodal Document Retrieval System | Group | 12 |
| **B** | Versioned Prompt Registry with Schema-Validated Evaluation and Model Migration | Individual | 8 |
| | **Total** | | **20** |

Deadline: **30 November 2026**

Assignment brief: [docs/PCAM_ZG516_Group_Major_Project_Assignment_2_Complete.pdf](docs/PCAM_ZG516_Group_Major_Project_Assignment_2_Complete.pdf)

---

## Repository layout

```
pcam-zg516-a2/
├── README.md
├── TEAM.md
├── docs/                          # assignment brief + design notes
├── part_a/                        # Group — multimodal retrieval (12 marks)
│   ├── notebooks/
│   ├── src/                       # ingest, embed, retrieve, generate, guardrails
│   ├── data/
│   │   ├── corpus_inventory/      # tracked inventory (raw PDFs/PPTs stay local)
│   │   ├── golden_set/            # ≥30 Q&A with source doc/page
│   │   └── ontology/              # metadata ontology
│   ├── evidence/                  # E1–E10 tables, logs, latency, tokens
│   ├── reports/
│   └── demo/
└── part_b/                        # Individual — prompt registry (8 marks)
    ├── README.md                  # setup + ONE command to reproduce eval
    ├── registry/
    │   ├── prompts/               # ≥4 versioned YAML prompts
    │   └── registry.py
    ├── schemas/                   # Pydantic v2 I/O models
    ├── data/
    │   ├── golden_set.jsonl       # ≥20 cases, ≥4 edge/adversarial
    │   └── DATA_STATEMENT.md
    ├── eval/
    │   ├── evaluate.py
    │   ├── metrics.py
    │   └── results/
    ├── models/config.yaml
    ├── token_count.py
    └── report.pdf
```

---

## Part A — Multimodal Document Retrieval (group)

Build a retrieval system over **≥100 PDFs/PPTs** that extracts and searches **text, tables, and images**, with grounded answers, guardrails, self-improving prompts, and measured latency/tokens/consistency.

### Required experiments (E1–E10)

| ID | Focus |
|----|--------|
| E1 | Corpus and ingestion (≥100 docs; text/table/image counts) |
| E2 | Embedding and chunking comparison |
| E3 | Text-only vs multimodal / metadata-aware retrieval |
| E4 | Conversational memory (multi-turn) |
| E5 | Golden set (≥30) + automatic eval + ≥3 failures |
| E6 | Consistency, tokens, P95 latency &lt; 90s, DoS/guardrail overhead &lt; 6s |
| E7 | Prompt ablation (zero-shot, f-string, three-shot, Jinja2, ReAct/CREATE) |
| E8 | Self-improving prompt (≥3 iterations, dev/test split) |
| E9 | Guardrails + metadata ontology |
| E10 | End-to-end integrated demo |

### Constraints (headline)

- **FR1–FR5:** ≥100 docs; multimodal search; P95 query &lt; 90s; DoS/guardrails &lt; 6s overhead; self-improving prompts  
- **NFR1–NFR2:** response consistency (≥5 runs); token optimisation vs naive baseline  

### Deliverables

- Technical report (~10–15 pages) · Colab/notebook · demo (8–10 min) · contribution statement  
- Corpus inventory, HLD/LLD, golden set, ablation + self-improve log, ontology, benchmark table  

**Status:** scaffold only — corpus domain and approval TBD.

---

## Part B — Versioned Prompt Registry (individual)

Production-shaped prompt registry for an **organisation use case** (masked/synthetic data OK): ≥4 prompts (≥4,000 tokens total, each ≥500), Pydantic v2 I/O, golden set ≥20, evaluate on ≥3 open-weight models (Qwen, DeepSeek, gpt-oss-20b).

Reproduce evaluation (once implemented):

```bash
python part_b/eval/evaluate.py --model ... --prompt-version ...
```

Allowed models only: Qwen family, DeepSeek family, OpenAI gpt-oss-20b. No closed APIs in reported results.

**Status:** scaffold only — org use case TBD per member.

---

## Team

See [TEAM.md](TEAM.md) (same Group 15 as Assignment-1).

## Links

| Need | Link |
|------|------|
| GitHub | [bits-pgaiml-agai/pcam-zg516-a2](https://github.com/bits-pgaiml-agai/pcam-zg516-a2) |
| Assignment 1 | [bits-pgaiml-agai/pcam-zg516-a1-banking77](https://github.com/bits-pgaiml-agai/pcam-zg516-a1-banking77) |
