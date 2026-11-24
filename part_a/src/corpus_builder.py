from __future__ import annotations

import json
import random
from dataclasses import asdict, dataclass
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

from .config import CORPUS_DIR, INVENTORY_DIR, SEED

TOPICS = [
    ("put_wall", "Put Wall Operations"),
    ("pick_path", "Pick Path Optimization"),
    ("asn_receiving", "ASN Receiving"),
    ("wave_planning", "Wave Planning"),
    ("inventory", "Inventory Accuracy"),
    ("exceptions", "Exception Handling"),
    ("packing", "Packing Stations"),
    ("shipping", "Shipping & Carrier Handoff"),
    ("safety", "Floor Safety"),
    ("system_overview", "WES System Overview"),
]

DOC_TYPES = ["sop", "guide", "playbook", "reference", "diagram_sheet", "checklist"]


@dataclass
class DocRecord:
    doc_id: str
    filename: str
    document_type: str
    topic: str
    title: str
    pages: int
    n_tables: int
    n_images: int
    has_text: bool
    sensitivity: str = "public_synthetic"


def _facts(topic: str, idx: int) -> list[str]:
    """Canonical policy facts live on the first document of each topic (idx < 10)."""
    canonical = idx < 10
    base = {
        "put_wall": [
            f"Document {idx}: Put-wall lane capacity for wall-{idx % 20 + 1} is {12 + (idx % 8)} cubbies.",
            (
                "A put confirmation must be scanned before the next SKU is released to the wall."
                if canonical
                else f"Put confirmation policy for wall-{idx % 20 + 1} follows local SOP variant {idx}."
            ),
            (
                "P95 put dwell SLA is 90 seconds per induction cycle."
                if canonical
                else f"Local put dwell target for wall-{idx % 20 + 1} is {60 + (idx % 5) * 10} seconds."
            ),
            (
                "Light-directed put uses green for target cubby and red for blocked lane."
                if canonical
                else f"Light codes for wall-{idx % 20 + 1} are published on the station placard."
            ),
        ],
        "pick_path": [
            f"Document {idx}: Zone {chr(65 + idx % 6)} uses serpentine pick with batch size {4 + idx % 5}.",
            (
                "Shortest-path heuristic is disabled when congestion score exceeds 0.7."
                if canonical
                else f"Congestion threshold for zone {chr(65 + idx % 6)} is documented locally."
            ),
            (
                "Pickers must scan location then SKU then quantity for each pick line."
                if canonical
                else f"Scan sequence variant {idx} applies in this zone guide."
            ),
            (
                "Hot-pick SKUs are staged in forward pick faces near packing."
                if canonical
                else f"Hot-pick staging note for document {idx}."
            ),
        ],
        "asn_receiving": [
            f"Document {idx}: ASN-{1000 + idx} requires QC sample rate of {5 + idx % 10} percent.",
            (
                "Blind receiving is blocked when ASN lines exceed 200 without dock appointment."
                if canonical
                else f"Blind receiving rule variant {idx} applies at this dock."
            ),
            (
                "Damaged cartons must be booked to exception code RCV-DMG within 15 minutes."
                if canonical
                else f"Damage booking window for ASN-{1000 + idx} follows dock playbook {idx}."
            ),
            (
                "Putaway task generation waits until ASN is closed or partially closed."
                if canonical
                else f"Putaway trigger notes for ASN-{1000 + idx}."
            ),
        ],
        "wave_planning": [
            f"Document {idx}: Wave W-{idx % 50 + 1} priority score uses order age, SLA and cube utilization.",
            (
                "Maximum concurrent active waves per building is 8."
                if canonical
                else f"Building wave concurrency cap note {idx}."
            ),
            (
                "Single-line orders may bypass wave and go direct-to-pack."
                if canonical
                else f"Bypass rule variant {idx} for single-line orders."
            ),
            (
                "Wave release is gated on inventory reservation success rate >= 98%."
                if canonical
                else f"Reservation gate percentage for wave doc {idx} is local."
            ),
        ],
        "inventory": [
            f"Document {idx}: Cycle count ABC class A locations every {7 + idx % 7} days.",
            (
                "Variance above 2% triggers recount before adjustment posting."
                if canonical
                else f"Variance threshold note for inventory doc {idx}."
            ),
            (
                "License-plate inventory is mandatory for multi-SKU pallets."
                if canonical
                else f"LPN inventory note {idx}."
            ),
            (
                "Negative on-hand is blocked at WES; adjustments require supervisor role."
                if canonical
                else f"Adjustment role note for inventory doc {idx}."
            ),
        ],
        "exceptions": [
            f"Document {idx}: Short-pick exception EXP-SP-{idx % 100} routes to research queue.",
            (
                "Stuck-in-cubby incidents open a put-wall recovery task within 5 minutes."
                if canonical
                else f"Cubby recovery SLA note {idx}."
            ),
            (
                "System downtime playbook freezes new wave releases after 3 minutes outage."
                if canonical
                else f"Downtime freeze note {idx}."
            ),
            (
                "Unscannable barcode uses manual entry with dual verification."
                if canonical
                else f"Unscannable handling note {idx}."
            ),
        ],
        "packing": [
            f"Document {idx}: Pack station PS-{idx % 30 + 1} default carton is C{idx % 5 + 1}.",
            (
                "Weight check tolerance is +/- 3% of expected ship weight."
                if canonical
                else f"Weight tolerance note {idx}."
            ),
            (
                "Gift-wrap orders must not use auto-bagger lines."
                if canonical
                else f"Gift-wrap routing note {idx}."
            ),
            (
                "Pack confirmation posts tracking number back to host OMS."
                if canonical
                else f"Pack confirmation note {idx}."
            ),
        ],
        "shipping": [
            f"Document {idx}: Carrier cut-off for ground is 17:{idx % 50:02d} local dock time.",
            (
                "LTL freight requires BOL print before trailer close."
                if canonical
                else f"LTL close note {idx}."
            ),
            (
                "Manifest close fails if any carton lacks a valid tracking ID."
                if canonical
                else f"Manifest validation note {idx}."
            ),
            (
                "Sortation chute jam raises shipping exception SHP-JAM."
                if canonical
                else f"Chute jam note {idx}."
            ),
        ],
        "safety": [
            f"Document {idx}: safety bulletin reference SAF-{idx:03d}.",
            (
                "Pedestrian lanes are marked yellow; powered equipment yields at crossings."
                if canonical
                else f"Pedestrian marking note {idx}."
            ),
            (
                "Emergency stop cords are tested every shift start."
                if canonical
                else f"E-stop test note {idx}."
            ),
            (
                "PPE required in put-wall and packing zones includes safety shoes."
                if canonical
                else f"PPE note {idx}."
            ),
            (
                "Spill response kit locations are posted on every aisle end-cap."
                if canonical
                else f"Spill kit note {idx}."
            ),
        ],
        "system_overview": [
            f"Document {idx}: system overview sheet SYS-{idx:03d}.",
            (
                "WES orchestrates receiving, inventory, fulfilment waves, packing and shipping."
                if canonical
                else f"WES scope note {idx}."
            ),
            (
                "Host OMS owns order promise; WES owns warehouse execution state."
                if canonical
                else f"OMS/WES boundary note {idx}."
            ),
            (
                "All operator actions are audited with user id, station id and timestamp."
                if canonical
                else f"Audit field note {idx}."
            ),
            (
                "Simulation mode uses synthetic LPNs prefixed TXN-DEMO-."
                if canonical
                else f"Simulation LPN note {idx}."
            ),
        ],
    }
    return list(base[topic])


def _table_data(topic: str, idx: int) -> list[list[str]]:
    if topic == "put_wall":
        return [
            ["Lane", "Cubbies", "SLA_sec", "Status"],
            [f"L{idx % 10 + 1}", str(12 + idx % 8), "90", "ACTIVE"],
            [f"L{(idx + 1) % 10 + 1}", str(10 + idx % 6), "90", "BLOCKED" if idx % 7 == 0 else "ACTIVE"],
            [f"L{(idx + 2) % 10 + 1}", str(14 + idx % 4), "120", "ACTIVE"],
        ]
    if topic == "wave_planning":
        return [
            ["Wave", "Orders", "Priority", "Reservation_%"],
            [f"W-{idx % 50 + 1}", str(100 + idx % 40), "HIGH", "99.1"],
            [f"W-{(idx + 1) % 50 + 1}", str(80 + idx % 30), "MED", "98.4"],
            [f"W-{(idx + 2) % 50 + 1}", str(60 + idx % 25), "LOW", "97.9"],
        ]
    if topic == "inventory":
        return [
            ["SKU", "OnHand", "Allocated", "ABC"],
            [f"SKU-{idx:04d}", str(50 + idx % 20), str(10 + idx % 8), "A"],
            [f"SKU-{idx + 1:04d}", str(30 + idx % 15), str(5 + idx % 5), "B"],
            [f"SKU-{idx + 2:04d}", str(12 + idx % 10), str(2 + idx % 3), "C"],
        ]
    return [
        ["Metric", "Target", "Actual"],
        ["P95_latency_sec", "90", str(40 + idx % 30)],
        ["Accuracy_%", "99.5", f"{98.5 + (idx % 10) / 10:.1f}"],
        ["Exceptions_per_hour", "5", str(1 + idx % 6)],
    ]


def _write_pdf(
    path: Path,
    topic: str,
    title: str,
    doc_type: str,
    idx: int,
    with_table: bool,
    with_image: bool,
) -> tuple[int, int, int]:
    page_w, page_h = letter
    c = canvas.Canvas(str(path), pagesize=letter)
    facts = _facts(topic, idx)

    c.setFont("Helvetica-Bold", 16)
    c.drawString(1 * inch, page_h - 0.9 * inch, title[:90])
    c.setFont("Helvetica", 10)
    c.drawString(1 * inch, page_h - 1.15 * inch, f"Type: {doc_type} | Topic: {topic} | Synthetic WES handbook")
    y = page_h - 1.5 * inch
    c.setFont("Helvetica-Bold", 12)
    c.drawString(1 * inch, y, "Key facts")
    y -= 18
    c.setFont("Helvetica", 10)
    for f in facts:
        for line in _wrap(f, 95):
            c.drawString(1 * inch, y, f"• {line}" if line == f or line.startswith(f[:20]) else f"  {line}")
            if line == f or f.startswith(line):
                pass
            y -= 14
            if y < 2.8 * inch:
                break
        else:
            continue
        break

    y -= 8
    c.setFont("Helvetica-Bold", 12)
    c.drawString(1 * inch, y, "Procedure")
    y -= 16
    c.setFont("Helvetica", 10)
    proc = (
        f"Operators follow the {title} procedure. All scans are validated by WES. "
        f"If validation fails, open the matching exception code and hold the unit. "
        f"Do not bypass confirmation for document index {idx}."
    )
    for line in _wrap(proc, 95):
        c.drawString(1 * inch, y, line)
        y -= 13

    n_tables = 0
    if with_table:
        y -= 10
        c.setFont("Helvetica-Bold", 12)
        c.drawString(1 * inch, y, "Reference table")
        y -= 16
        c.setFont("Courier", 9)
        for row in _table_data(topic, idx):
            c.drawString(1 * inch, y, " | ".join(row))
            y -= 12
        n_tables = 1

    c.showPage()
    pages = 1
    n_images = 0

    if with_image:
        c.setFont("Helvetica-Bold", 12)
        c.drawString(1 * inch, page_h - 1 * inch, f"Figure: {topic.replace('_', ' ').title()} flow")
        yb = page_h - 1.8 * inch
        boxes = ["Input", "WES decision", "Operator action", "Confirm / Exception"]
        x = 0.8 * inch
        for i, label in enumerate(boxes):
            c.setStrokeColor(colors.HexColor("#1f4e79"))
            c.setFillColor(colors.HexColor("#d6e6f5"))
            c.roundRect(x, yb, 1.55 * inch, 0.7 * inch, 6, fill=1, stroke=1)
            c.setFillColor(colors.black)
            c.setFont("Helvetica", 8)
            c.drawCentredString(x + 0.77 * inch, yb + 0.3 * inch, label)
            if i < len(boxes) - 1:
                c.line(x + 1.55 * inch, yb + 0.35 * inch, x + 1.75 * inch, yb + 0.35 * inch)
            x += 1.75 * inch
        c.setFont("Helvetica", 10)
        c.drawString(
            1 * inch,
            yb - 0.55 * inch,
            f"Diagram callout: step {(idx % 4) + 1} must complete before downstream release.",
        )
        c.setFont("Helvetica", 9)
        c.drawString(
            1 * inch,
            yb - 0.85 * inch,
            "Image modality: layout diagram searchable via OCR/caption text embedded in the PDF.",
        )
        c.showPage()
        pages = 2
        n_images = 1

    c.save()
    return pages, n_tables, n_images


def _wrap(text: str, width: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    cur: list[str] = []
    for w in words:
        trial = (" ".join(cur + [w])).strip()
        if len(trial) <= width:
            cur.append(w)
        else:
            if cur:
                lines.append(" ".join(cur))
            cur = [w]
    if cur:
        lines.append(" ".join(cur))
    return lines or [text]


def build_corpus(n_docs: int = 110, out_dir: Path | None = None) -> list[DocRecord]:
    random.seed(SEED)
    out_dir = out_dir or CORPUS_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    INVENTORY_DIR.mkdir(parents=True, exist_ok=True)

    for old in out_dir.glob("*.pdf"):
        old.unlink()

    records: list[DocRecord] = []
    for i in range(n_docs):
        topic_key, topic_title = TOPICS[i % len(TOPICS)]
        doc_type = DOC_TYPES[i % len(DOC_TYPES)]
        doc_id = f"WES-{topic_key[:3].upper()}-{i:03d}"
        title = f"{topic_title} — {doc_type.upper()} #{i:03d}"
        filename = f"{doc_id}.pdf"
        path = out_dir / filename
        with_table = i % 3 != 2
        with_image = i % 4 == 0
        pages, n_tables, n_images = _write_pdf(
            path, topic_key, title, doc_type, i, with_table, with_image
        )
        records.append(
            DocRecord(
                doc_id=doc_id,
                filename=filename,
                document_type=doc_type,
                topic=topic_key,
                title=title,
                pages=pages,
                n_tables=n_tables,
                n_images=n_images,
                has_text=True,
            )
        )

    inventory = {
        "domain": "synthetic_wes_operations",
        "n_documents": len(records),
        "n_pages": sum(r.pages for r in records),
        "n_tables": sum(r.n_tables for r in records),
        "n_images": sum(r.n_images for r in records),
        "sensitivity": "public_synthetic",
        "documents": [asdict(r) for r in records],
    }
    (INVENTORY_DIR / "inventory.json").write_text(json.dumps(inventory, indent=2), encoding="utf-8")
    return records


if __name__ == "__main__":
    recs = build_corpus()
    print(f"Built {len(recs)} documents → {CORPUS_DIR}")
