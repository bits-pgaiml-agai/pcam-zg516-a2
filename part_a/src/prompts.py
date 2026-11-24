from __future__ import annotations

from jinja2 import Template

SYSTEM_POLICY = (
    "You are a WES operations assistant. Answer ONLY from the provided evidence. "
    "Every answer must cite source filename and page. If evidence is insufficient, refuse."
)

FEW_SHOTS = [
    {
        "q": "What is the P95 put dwell SLA?",
        "a": "P95 put dwell SLA is 90 seconds per induction cycle. [WES-PUT-000.pdf p.1]",
    },
    {
        "q": "When is blind receiving blocked?",
        "a": "Blind receiving is blocked when ASN lines exceed 200 without a dock appointment. [WES-ASN-002.pdf p.1]",
    },
    {
        "q": "What happens on a stuck-in-cubby incident?",
        "a": "Open a put-wall recovery task within 5 minutes. [WES-EXC-005.pdf p.1]",
    },
]


def render_zero_shot(query: str, evidence: str, ontology: dict) -> str:
    return (
        f"{SYSTEM_POLICY}\n"
        f"Topic filter hint: {ontology.get('topic', 'any')}\n"
        f"Evidence:\n{evidence}\n"
        f"Question: {query}\n"
        f"Answer with citations:"
    )


def render_f_string(query: str, evidence: str, ontology: dict) -> str:
    topic = ontology.get("topic", "any")
    modality = ontology.get("modality", "mixed")
    return (
        f"{SYSTEM_POLICY} Focus topic={topic} modality={modality}.\n"
        f"EVIDENCE:\n{evidence}\nQUESTION:\n{query}\nANSWER:"
    )


def render_three_shot(query: str, evidence: str, ontology: dict) -> str:
    demos = "\n".join([f"Q: {ex['q']}\nA: {ex['a']}" for ex in FEW_SHOTS])
    return (
        f"{SYSTEM_POLICY}\nExamples:\n{demos}\n"
        f"Evidence:\n{evidence}\nQuestion: {query}\nAnswer:"
    )


JINJA_TMPL = Template(
    """{{ policy }}
Ontology: document_type={{ document_type }}, topic={{ topic }}, modality={{ modality }}
{% if conversation %}
Conversation:
{{ conversation }}
{% endif %}
Evidence:
{{ evidence }}
Question: {{ query }}
Return a grounded answer with [source p.page] citations. Refuse if unsupported.
"""
)


def render_jinja2(query: str, evidence: str, ontology: dict, conversation: str = "") -> str:
    return JINJA_TMPL.render(
        policy=SYSTEM_POLICY,
        document_type=ontology.get("document_type", "any"),
        topic=ontology.get("topic", "any"),
        modality=ontology.get("modality", "mixed"),
        conversation=conversation,
        evidence=evidence,
        query=query,
    )


def render_react(query: str, evidence: str, ontology: dict) -> str:
    return (
        f"{SYSTEM_POLICY}\n"
        "Use ReAct steps.\n"
        f"Thought: identify relevant evidence for topic={ontology.get('topic', 'any')}.\n"
        f"Action: read_evidence\n"
        f"Observation:\n{evidence}\n"
        f"Thought: formulate grounded answer with citations.\n"
        f"Question: {query}\n"
        "Final Answer:"
    )


PROMPT_VARIANTS = {
    "zero_shot": render_zero_shot,
    "f_string": render_f_string,
    "three_shot": render_three_shot,
    "jinja2": render_jinja2,
    "react": render_react,
}
