from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Turn:
    role: str
    content: str


@dataclass
class ConversationMemory:
    """Short-term conversational memory for multi-turn follow-ups."""

    max_turns: int = 8
    turns: list[Turn] = field(default_factory=list)

    def add(self, role: str, content: str) -> None:
        self.turns.append(Turn(role=role, content=content))
        if len(self.turns) > self.max_turns:
            self.turns = self.turns[-self.max_turns :]

    def as_context(self) -> str:
        if not self.turns:
            return ""
        lines = [f"{t.role}: {t.content}" for t in self.turns]
        return "\n".join(lines)

    def rewrite_followup(self, query: str) -> str:
        if not self.turns:
            return query
        last_user = next((t.content for t in reversed(self.turns) if t.role == "user"), "")
        if query.lower().startswith(("what about", "and ", "also ", "how about", "for that")):
            return f"{last_user} | follow-up: {query}"
        return query
