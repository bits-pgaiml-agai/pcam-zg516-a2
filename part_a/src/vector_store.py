from __future__ import annotations

import pickle
import re
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from .chunking import Chunk
from .config import INDEX_DIR, TOP_K
from .embeddings import TfidfEmbedder


@dataclass
class Hit:
    chunk: Chunk
    score: float


def _terms(text: str) -> set[str]:
    return {t.lower() for t in re.findall(r"[A-Za-z0-9_+%-]+", text) if len(t) > 2}


class VectorStore:
    def __init__(self, embedder: TfidfEmbedder, chunks: list[Chunk]) -> None:
        self.embedder = embedder
        self.chunks = chunks
        self.matrix = embedder.matrix
        self._chunk_terms = [_terms(c.text) for c in chunks]

    @classmethod
    def load(cls, index_dir: Path | None = None) -> "VectorStore":
        index_dir = index_dir or INDEX_DIR
        embedder = TfidfEmbedder.load(index_dir / "tfidf.pkl")
        with (index_dir / "chunks.pkl").open("rb") as f:
            chunks = pickle.load(f)
        return cls(embedder, chunks)

    def search(
        self,
        query: str,
        top_k: int = TOP_K,
        modality: str | None = None,
        topic: str | None = None,
        multimodal: bool = True,
    ) -> list[Hit]:
        q = self.embedder.transform([query])
        dense = (self.matrix @ q.T).toarray().ravel()
        q_terms = _terms(query)
        scores = np.zeros_like(dense)
        for i, cterms in enumerate(self._chunk_terms):
            if not q_terms:
                kw = 0.0
            else:
                kw = len(q_terms & cterms) / len(q_terms)
            scores[i] = 0.65 * float(dense[i]) + 0.35 * kw

        order = np.argsort(-scores)
        hits: list[Hit] = []
        for idx in order:
            ch = self.chunks[idx]
            if modality and ch.modality != modality:
                continue
            if topic and ch.topic != topic:
                continue
            if not multimodal and ch.modality != "text":
                continue
            hits.append(Hit(chunk=ch, score=float(scores[idx])))
            if len(hits) >= top_k:
                break
        return hits
