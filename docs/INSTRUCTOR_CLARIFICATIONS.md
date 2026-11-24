# Instructor clarifications — Assignment 2

Sources (session transcripts):

| Date | File | Role |
|------|------|------|
| 14 Nov 2026 | `Learning/Transcripts/..._07_20261114.docx` | Main A2 briefing (Dhruba Adhikary) |
| 20 Nov 2026 | `Learning/Transcripts/..._08_20261120.docx` | Part A/B dataset clarification |
| 21 Nov 2026 | `Learning/Transcripts/..._09_20261121.docx` | No A2 project guidance (Jinja2 lab only) |

Canonical written brief remains: [PCAM_ZG516_Group_Major_Project_Assignment_2_Complete.pdf](PCAM_ZG516_Group_Major_Project_Assignment_2_Complete.pdf). Where verbal notes conflict with the PDF on Part A scope, **follow the PDF**.

---

## Marks and split

- Assignment 2 = **20 marks** total.
- **Part A (12)**: group problem statement.
- **Part B (8)**: situated-learning **versioned prompt registry** (individual).

Verbal note (14 Nov): Part A might be an either/or among 2–3 topics. **Released PDF fixes Part A as Multimodal Document Retrieval only** — that is what Group 15 implements.

## Submission packaging

- Part A solved **as a group**.
- Part B solved **individually**, but packaged **inside the group submission zip**, unique under each member’s name.
- Part B deliverables: **Git repository** + report **≤ 8 pages PDF**.
- Window: about **three weeks** from release → due **30 Nov 2026**.

## Dataset / corpus rules (confirmed 20 Nov)

| Part | Dataset rule |
|------|----------------|
| **A** | One **shared** corpus chosen by the group (≥100 PDFs/PPTs; text + tables + images). |
| **B** | **Independent** of Part A. Workplace data **or synthetic**. Must meet Satyanarayan / PDF constraints. |

Part A and Part B do **not** need the same dataset.

## Part B constraints (instructor emphasis, 14 Nov)

- Open-weight only: **Qwen**, **DeepSeek**, **GPT open-source / gpt-oss**. No Claude / Gemini / proprietary GPT APIs in reported results.
- Inference free: Ollama, vLLM, llama.cpp, hosted open-weight endpoints, etc.
- ≥ **4** prompts, ≥ **4000** tokens total, I/O schemas (Pydantic), golden set ≥ **20**, ≥ **3** open-weight models.
- Version prompts; select best version; include **migration / model-selection** plan.
- **No two Part B submissions the same**; plagiarism → **zero for both parties**.
- No confidential org data; **mask / anonymise / synthetic**.
- If org use is impossible, pick any experimental use case (learning goal > org fidelity).

## Pedagogical expectations tied to the brief

- Prompt registry ≈ iterate versions against a golden set with traceability (v0 → vN → promote).
- Treat prompts like software: immutable role/task vs mutable context.
- Pydantic validation with measured first-pass vs after-repair.
- Prefer local open-source experimentation over paid closed APIs for reported results.

## Group 15 application

- **Part A domain (this repo):** synthetic **Warehouse Execution / WES operations handbook** corpus (non-confidential). Real Fortna/client docs are not used.
- **Part B:** each member’s own org/synthetic use case under `part_b/` (or member subfolders).
