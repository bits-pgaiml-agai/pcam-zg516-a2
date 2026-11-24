# Part B — Versioned Prompt Registry (individual)

Scaffold for the Part B deliverable checklist (Assignment-2 §4.7).

## Layout

```
part_b/
├── README.md
├── registry/
│   ├── prompts/*.yaml
│   └── registry.py
├── schemas/*.py
├── data/
│   ├── golden_set.jsonl
│   └── DATA_STATEMENT.md
├── eval/
│   ├── evaluate.py
│   ├── metrics.py
│   └── results/
├── models/config.yaml
├── token_count.py
└── report.pdf
```

## Reproduce evaluation (once implemented)

```bash
python eval/evaluate.py --model <name> --prompt-version <semver>
```

## Checklist

- [ ] ≥4 prompts, ≥4,000 tokens total, no prompt under 500 tokens
- [ ] ≥1 prompt with ≥2 versions (evaluated)
- [ ] Pydantic I/O for every prompt + ≥1 business-rule validator
- [ ] Golden set ≥20 cases, ≥4 edge/adversarial
- [ ] ≥3 models: Qwen, DeepSeek, gpt-oss-20b (one each)
- [ ] Migration plan OR per-prompt model selection
- [ ] Data handling statement + AI-assistant use declaration
