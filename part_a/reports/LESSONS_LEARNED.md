# Part A — Lessons learned (draft)

## Group

- Synthetic corpus with deterministic facts made golden-set construction and regression eval tractable before a real 100-doc corpus is approved.
- Modality tagging (text/table/image caption) beat a text-only index on diagram/table questions in E3.
- Token cost is dominated by evidence packing; smaller chunks + top-k beat sending whole PDFs.

## Individual (placeholders — each member to personalize)

| Member | Lesson |
|--------|--------|
| Anil Kumar Reddy K | TBD |
| Nisha Palanisamy | TBD |
| Venkata Srinivasa Rao Tunuguntla | Local TF-IDF + mock generator unblocks pipeline/eval before GPU/Ollama; keep Ollama as a swap-in backend for the demo. |
