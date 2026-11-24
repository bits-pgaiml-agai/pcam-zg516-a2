from __future__ import annotations

import time
from dataclasses import asdict, dataclass

from .generate import GenerationResult, generate
from .guardrails import check_input, check_output
from .memory import ConversationMemory
from .prompts import PROMPT_VARIANTS
from .vector_store import Hit, VectorStore


@dataclass
class QueryResult:
    query: str
    allowed: bool
    refusal_reason: str | None
    answer: str
    citations: list[str]
    hits: list[dict]
    prompt_variant: str
    latency_sec: float
    guardrail_overhead_sec: float
    input_tokens: int
    output_tokens: int
    backend: str


class RetrievalPipeline:
    def __init__(self, store: VectorStore, memory: ConversationMemory | None = None) -> None:
        self.store = store
        self.memory = memory or ConversationMemory()

    def _format_evidence(self, hits: list[Hit]) -> str:
        blocks = []
        for h in hits:
            ch = h.chunk
            blocks.append(
                f"[{ch.source} p.{ch.page} | {ch.modality}/{ch.topic}] score={h.score:.3f}\n{ch.text}"
            )
        return "\n\n".join(blocks)

    def query(
        self,
        query: str,
        prompt_variant: str = "jinja2",
        multimodal: bool = True,
        topic: str | None = None,
        use_memory: bool = True,
        dos_check: bool = True,
    ) -> QueryResult:
        t0 = time.perf_counter()
        guard_overhead = 0.0

        if dos_check:
            g_in = check_input(query)
            guard_overhead += g_in.elapsed_sec
            if not g_in.allowed:
                return QueryResult(
                    query=query,
                    allowed=False,
                    refusal_reason=g_in.reason,
                    answer=f"Request blocked by input guardrail: {g_in.reason}",
                    citations=[],
                    hits=[],
                    prompt_variant=prompt_variant,
                    latency_sec=time.perf_counter() - t0,
                    guardrail_overhead_sec=guard_overhead,
                    input_tokens=0,
                    output_tokens=0,
                    backend="guardrail",
                )

        rewritten = self.memory.rewrite_followup(query) if use_memory else query
        hits = self.store.search(rewritten, multimodal=multimodal, topic=topic)
        evidence = self._format_evidence(hits)
        ontology = {
            "topic": topic or (hits[0].chunk.topic if hits else "any"),
            "modality": "mixed" if multimodal else "text",
            "document_type": hits[0].chunk.document_type if hits else "any",
        }
        renderer = PROMPT_VARIANTS.get(prompt_variant, PROMPT_VARIANTS["jinja2"])
        if prompt_variant == "jinja2":
            prompt = renderer(
                rewritten,
                evidence,
                ontology,
                conversation=self.memory.as_context() if use_memory else "",
            )
        else:
            prompt = renderer(rewritten, evidence, ontology)

        gen: GenerationResult = generate(prompt, hits)
        g_out = check_output(gen.answer, gen.citations)
        guard_overhead += g_out.elapsed_sec
        answer = gen.answer
        citations = gen.citations
        reason = None
        allowed = True
        if not g_out.allowed:
            allowed = False
            reason = g_out.reason
            answer = f"Insufficient grounded evidence (output guardrail: {g_out.reason})."
            citations = []

        if use_memory and allowed:
            self.memory.add("user", query)
            self.memory.add("assistant", answer)

        return QueryResult(
            query=query,
            allowed=allowed,
            refusal_reason=reason,
            answer=answer,
            citations=citations,
            hits=[
                {
                    "chunk_id": h.chunk.chunk_id,
                    "source": h.chunk.source,
                    "page": h.chunk.page,
                    "modality": h.chunk.modality,
                    "score": h.score,
                }
                for h in hits
            ],
            prompt_variant=prompt_variant,
            latency_sec=time.perf_counter() - t0,
            guardrail_overhead_sec=guard_overhead,
            input_tokens=gen.input_tokens,
            output_tokens=gen.output_tokens,
            backend=gen.backend,
        )

    def to_dict(self, result: QueryResult) -> dict:
        return asdict(result)
