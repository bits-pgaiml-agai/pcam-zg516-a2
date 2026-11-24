# Part A — Multimodal Document Retrieval (Group 15)

Synthetic **WES operations handbook** corpus (≥100 PDFs) with text, tables and diagram pages. Retrieval is multimodal via modality-tagged chunks; generation defaults to a deterministic **mock** backend (optional **Ollama**).

## Quick start

```bash
cd part_a
pip install -r requirements.txt
python scripts/build_golden_set.py
python scripts/run_part_a.py
```

This builds the corpus, indexes it, runs E1–E10 evidence writers into `evidence/`.

### Optional Ollama

```bash
# PowerShell
$env:LLM_BACKEND="ollama"   # or edit src/config.py
ollama pull qwen2.5:1.5b-instruct
python scripts/run_part_a.py
```

## Layout

- `src/` — ingest → retrieve → generate pipeline  
- `data/corpus_synthetic/` — generated PDFs  
- `data/golden_set/golden_set.jsonl` — ≥30 questions  
- `data/ontology/metadata_ontology.yaml`  
- `evidence/` — experiment outputs  
- `reports/HLD.md`, `reports/LLD.md`  
- `notebooks/PartA_Multimodal_Retrieval.ipynb`

## Experiments

| ID | Script artifact |
|----|-----------------|
| E1 | `evidence/E1_corpus_ingestion.json` |
| E2 | `evidence/E2_chunking_comparison.json` |
| E3 | `evidence/E3_retrieval_comparison.json` |
| E4 | `evidence/E4_memory_transcript.json` |
| E5 | `evidence/E5_*.json` |
| E6 | latency fields in E5 + guardrail overhead |
| E7 | `evidence/E7_prompt_ablation.json` |
| E8 | `evidence/E8_self_improve_*.json` |
| E9 | `evidence/E9_guardrails.json` |
| E10 | `evidence/E10_*.json` |

## Data handling

All corpus content is **public synthetic** WES documentation. No client or Fortna confidential data is included.
