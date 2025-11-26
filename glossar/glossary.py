import json
from copyreg import remove_extension
from pathlib import Path
from typing import List, Optional
from .glossaryEntry import GlossaryEntry


class Glossary:
    def __init__(self,) -> None:
        self.entries: List[GlossaryEntry] = []

    def add_entry(self, entry: GlossaryEntry) -> None:
        self.entries.append(entry)

    def find_by_term(self, term: str) -> Optional[GlossaryEntry]:
        term_lower = term.casefold()
        for entry in self.entries:
            if entry.term.lower() == term_lower:
                return entry
        return None

    def search(self, query: str) -> List[GlossaryEntry]:
        query_lower = query.casefold()
        results: List[GlossaryEntry] = []
        for entry in self.entries:
            if query_lower in entry.term.lower() or query_lower in entry.definition.lower():
                results.append(entry)
        return results

    def remove_by_term(self, term: str) -> List[GlossaryEntry]:
        term_lower = term.casefold()
        for i, entry in enumerate(self.entries):
            if entry.term.lower() == term_lower:
                del self.entries[i]
                return True
        return False

    def list_sorted_by(self, f) -> List[GlossaryEntry]:
        return sorted(self.entries, key=lambda e: (getattr(e, f) or "").lower())

    def save_to_file(self, filepath: str) -> None:
        path = Path(filepath)
        data = [entry.to_dict() for entry in self.entries]
        text = json.dumps(data, indent=2, ensure_ascii=False)
        path.write_text(text, encoding="utf-8")

    def update_entry(self,
                     original_term: str,
                     new_term: Optional[str] = None,
                     definition: Optional[str] = None,
                     append_definition: Optional[str] = None,
                     category: Optional[str] = None,
                     add_tags: Optional[str] = None,
                     remove_tags: Optional[str] = None,
                     set_tags: Optional[str] = None,
                     clear_tags: bool = False,
                     force: bool = False
                     ) -> bool:

        entry = self.find_by_term(original_term)
        if not entry:
            return False

        if new_term and new_term != original_term:
            existing = self.find_by_term(new_term)
            if existing and not force:
                print(f"Target term {new_term} already exists. Use --force to overwrite.")
            entry.term = new_term

        if definition is not None:
            entry.definition = definition
        if append_definition:
            if entry.definition:
                entry.definition = entry.definition.rstrip() + "\n\n" + append_definition
            else:
                entry.definition = append_definition

        if category is not None:
            entry.category = category

        if clear_tags:
            entry.tags = []
        if set_tags is not None:
            entry.tags = list(dict.fromkeys([t.strip() for t in set_tags if t.strip()]))
        else:
            if add_tags:
                for t in add_tags:
                    ts = t.strip()
                    if ts and ts not in entry.tags:
                        entry.tags.append(ts)
            if remove_tags:
                for t in remove_tags:
                    ts = t.strip()
                    if ts in entry.tags:
                        entry.tags.remove(ts)
        return True


    def load_from_file(self, filepath: str) -> None:
        path = Path(filepath)
        if not path.exists():
            return
        raw = path.read_text(encoding="utf-8")
        data_list = json.loads(raw)
        self.entries = [GlossaryEntry.from_dict(d) for d in data_list]
