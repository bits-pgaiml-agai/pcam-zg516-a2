from __future__ import annotations

import pickle
from pathlib import Path

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize

from .config import INDEX_DIR, SEED
from .chunking import Chunk


class TfidfEmbedder:
    def __init__(self) -> None:
        self.vectorizer = TfidfVectorizer(
            lowercase=True,
            ngram_range=(1, 2),
            min_df=1,
            max_features=20000,
        )
        self.matrix = None

    def fit_transform(self, texts: list[str]) -> np.ndarray:
        mat = self.vectorizer.fit_transform(texts)
        self.matrix = normalize(mat)
        return self.matrix

    def transform(self, texts: list[str]) -> np.ndarray:
        mat = self.vectorizer.transform(texts)
        return normalize(mat)

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("wb") as f:
            pickle.dump({"vectorizer": self.vectorizer, "matrix": self.matrix}, f)

    @classmethod
    def load(cls, path: Path) -> "TfidfEmbedder":
        obj = cls()
        with path.open("rb") as f:
            payload = pickle.load(f)
        obj.vectorizer = payload["vectorizer"]
        obj.matrix = payload["matrix"]
        return obj


def build_embeddings(chunks: list[Chunk], index_dir: Path | None = None) -> tuple[TfidfEmbedder, list[Chunk]]:
    index_dir = index_dir or INDEX_DIR
    index_dir.mkdir(parents=True, exist_ok=True)
    embedder = TfidfEmbedder()
    texts = [c.text for c in chunks]
    embedder.fit_transform(texts)
    embedder.save(index_dir / "tfidf.pkl")
    with (index_dir / "chunks.pkl").open("wb") as f:
        pickle.dump(chunks, f)
    meta = {"backend": "tfidf", "n_chunks": len(chunks), "seed": SEED}
    (index_dir / "embed_meta.json").write_text(__import__("json").dumps(meta, indent=2), encoding="utf-8")
    return embedder, chunks
