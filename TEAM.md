# Team — Group 15

Same group as Assignment-1 ([pcam-zg516-a1-banking77](https://github.com/bits-pgaiml-agai/pcam-zg516-a1-banking77)).

| Name | Assignment-2 workstream |
|------|-------------------------|
| Anil Kumar Reddy K | Part A — corpus / ingest / evaluation support |
| Nisha Palanisamy | Part A — prompts / guardrails / demo |
| Venkata Srinivasa Rao Tunuguntla | Part A — retrieval architecture / pipeline; Part B — individual |

## Shared contracts

- **Part A corpus domain:** Synthetic WES operations handbook (public synthetic; instructor approval for any future real corpus)
- **Part A embedding / vector store:** TF-IDF + in-process cosine store (`part_a/data/index/`)
- **Part A LLM backend:** `mock` default; optional `ollama` (`qwen2.5:1.5b-instruct`)
- **Part B org use case:** TBD per member (masked or synthetic; independent of Part A)
- **Part B models:** ≥1 each from Qwen, DeepSeek, gpt-oss-20b
- **Seed:** 42

## Instructor packaging note

Part B is individual but submitted inside the group zip under each member’s name ([docs/INSTRUCTOR_CLARIFICATIONS.md](docs/INSTRUCTOR_CLARIFICATIONS.md)).
