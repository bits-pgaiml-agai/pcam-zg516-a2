from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path

from .config import CHUNK_OVERLAP, CHUNK_SIZE, INVENTORY_DIR
from .ingest import Element


@dataclass
class Chunk:
    chunk_id: str
    doc_id: str
    source: str
    page: int
    modality: str
    document_type: str
    topic: str
    section: str
    text: str
    sensitivity: str = "public_synthetic"


def _window(text: str, size: int, overlap: int) -> list[str]:
    text = " ".join(text.split())
    if len(text) <= size:
        return [text]
    parts: list[str] = []
    start = 0
    while start < len(text):
        end = min(len(text), start + size)
        parts.append(text[start:end])
        if end >= len(text):
            break
        start = max(0, end - overlap)
    return parts


def chunk_elements(elements: list[Element], size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[Chunk]:
    chunks: list[Chunk] = []
    for i, el in enumerate(elements):
        pieces = _window(el.text, size, overlap)
        for j, piece in enumerate(pieces):
            chunks.append(
                Chunk(
                    chunk_id=f"{el.doc_id}-p{el.page}-{el.modality}-{j}",
                    doc_id=el.doc_id,
                    source=el.source,
                    page=el.page,
                    modality=el.modality,
                    document_type=el.document_type,
                    topic=el.topic,
                    section=el.section,
                    text=piece,
                    sensitivity=el.sensitivity,
                )
            )
    out = INVENTORY_DIR / "chunks.jsonl"
    with out.open("w", encoding="utf-8") as f:
        for ch in chunks:
            f.write(json.dumps(asdict(ch), ensure_ascii=False) + "\n")
    return chunks


def compare_chunking(elements: list[Element]) -> dict:
    a = chunk_elements(elements, size=300, overlap=40)
    b = chunk_elements(elements, size=600, overlap=80)
    # restore default artifacts from preferred config
    preferred = chunk_elements(elements, size=CHUNK_SIZE, overlap=CHUNK_OVERLAP)
    return {
        "config_a": {"size": 300, "overlap": 40, "n_chunks": len(a)},
        "config_b": {"size": 600, "overlap": 80, "n_chunks": len(b)},
        "preferred": {"size": CHUNK_SIZE, "overlap": CHUNK_OVERLAP, "n_chunks": len(preferred)},
    }
