from dataclasses import dataclass, asdict
from typing import List, Dict, Any


@dataclass
class GlossaryEntry:
    term: str
    definition: str
    category: str | None = None
    tags: List[str] | None = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "GlossaryEntry":
        return GlossaryEntry(
            term=data["term"],
            definition=data["definition"],
            category=data.get("category"),
            tags=data.get("tags") or [],
        )
