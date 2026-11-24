from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path

from pypdf import PdfReader

from .config import CORPUS_DIR, INVENTORY_DIR


@dataclass
class Element:
    doc_id: str
    source: str
    page: int
    modality: str
    document_type: str
    topic: str
    section: str
    text: str
    sensitivity: str = "public_synthetic"


def _parse_header_meta(text: str) -> tuple[str, str]:
    doc_type = "reference"
    topic = "system_overview"
    m_type = re.search(r"Type:\s*(\w+)", text)
    m_topic = re.search(r"Topic:\s*([a-z_]+)", text)
    if m_type:
        doc_type = m_type.group(1).strip()
    if m_topic:
        topic = m_topic.group(1).strip()
    return doc_type, topic


def _fact_lines(text: str) -> list[str]:
    lines = []
    for raw in re.split(r"[\n\r]+|(?<=\.)\s+|•", text):
        line = raw.strip(" \t•|-")
        if len(line) < 25:
            continue
        if any(x in line.lower() for x in ("synthetic wes handbook", "key facts", "type:", "topic:", "procedure")):
            continue
        lines.append(line)
    return lines


def _split_modalities(page_text: str) -> list[tuple[str, str, str]]:
    """Return list of (modality, section, text)."""
    chunks: list[tuple[str, str, str]] = []
    if not page_text or not page_text.strip():
        return chunks

    lower = page_text.lower()
    if "figure:" in lower or "diagram callout" in lower or "image modality" in lower:
        for line in _fact_lines(page_text):
            chunks.append(("image", "diagram", line))
        if not chunks:
            chunks.append(("image", "diagram", page_text.strip()))
        return chunks

    if "reference table" in lower or " | " in page_text:
        if "Reference table" in page_text:
            pre, _, rest = page_text.partition("Reference table")
            for line in _fact_lines(pre):
                chunks.append(("text", "body", line))
            table_body = ("Reference table\n" + rest).strip()
            for row in table_body.splitlines():
                row = row.strip()
                if row:
                    chunks.append(("table", "reference_table", row))
        else:
            chunks.append(("table", "reference_table", page_text.strip()))
        return chunks

    for line in _fact_lines(page_text):
        chunks.append(("text", "body", line))
    if not chunks:
        chunks.append(("text", "body", page_text.strip()))
    return chunks


def ingest_corpus(corpus_dir: Path | None = None) -> list[Element]:
    corpus_dir = corpus_dir or CORPUS_DIR
    inventory_path = INVENTORY_DIR / "inventory.json"
    inv = json.loads(inventory_path.read_text(encoding="utf-8")) if inventory_path.exists() else {"documents": []}
    meta_by_file = {d["filename"]: d for d in inv.get("documents", [])}

    elements: list[Element] = []
    for pdf_path in sorted(corpus_dir.glob("*.pdf")):
        meta = meta_by_file.get(pdf_path.name, {})
        doc_id = meta.get("doc_id", pdf_path.stem)
        reader = PdfReader(str(pdf_path))
        for page_idx, page in enumerate(reader.pages, start=1):
            raw = page.extract_text() or ""
            doc_type, topic = _parse_header_meta(raw)
            doc_type = meta.get("document_type", doc_type)
            topic = meta.get("topic", topic)
            for modality, section, text in _split_modalities(raw):
                elements.append(
                    Element(
                        doc_id=doc_id,
                        source=pdf_path.name,
                        page=page_idx,
                        modality=modality,
                        document_type=doc_type,
                        topic=topic,
                        section=section,
                        text=text,
                    )
                )

    out = INVENTORY_DIR / "elements.jsonl"
    with out.open("w", encoding="utf-8") as f:
        for el in elements:
            f.write(json.dumps(asdict(el), ensure_ascii=False) + "\n")

    stats = {
        "n_elements": len(elements),
        "n_text": sum(1 for e in elements if e.modality == "text"),
        "n_table": sum(1 for e in elements if e.modality == "table"),
        "n_image": sum(1 for e in elements if e.modality == "image"),
        "n_docs": len({e.doc_id for e in elements}),
    }
    (INVENTORY_DIR / "ingestion_stats.json").write_text(json.dumps(stats, indent=2), encoding="utf-8")
    return elements
