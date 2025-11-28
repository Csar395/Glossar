import argparse
import sys

from glossar.main import GLOSSARY_DIR, CURRENT_META_FILE
from glossar.helpFunctions import print_single_entry_as_table
from glossar.pathFunctions import get_active_filepath, set_active_filepath
from glossar.glossary import Glossary
from glossar.glossaryEntry import GlossaryEntry


def handle_init(args: argparse.Namespace, glossary: Glossary) -> None:
    filename = f"{args.name}.json"
    path = GLOSSARY_DIR / filename

    if path.exists() and not args.force:
        print(f"Glossary file {path} exists."
              f"If you wish to overwrite it, use --force.")
        return

    glossary.entries.clear()
    glossary.save_to_file(str(path))

    set_active_filepath(path)

    print(f"Glossary file in '{path}' created and activated.")


def handle_add(args: argparse.Namespace, glossary: Glossary) -> None:
    term = args.term.strip()
    print(f"New entry for Term: {term}")

    definition = input("Definition: ").strip()
    while not definition:
        print("Definition is required.")
        definition = input("Definition: ").strip()

    category = input("Category (optional): ").strip()
    if category == "":
        category = None

    tags_raw = input("Tags, seperated by comma (optional): ").strip()
    if tags_raw:
        tags = [t.strip() for t in tags_raw.split(",") if t.strip()]
    else:
        tags = []

    existing = glossary.find_by_term(term)
    if existing is not None:
        overwrite = input(f"Term {term} already exists. Overwrite? (y/n): ").strip().lower()
        if overwrite not in ["y", "j", "yes"]:
            print("Cancelled. Entry was not changed.")
            return
        glossary.remove_by_term(term)

    entry = GlossaryEntry(term=term, definition=definition, category=category, tags=tags)

    glossary.add_entry(entry)

    active_path = get_active_filepath()
    glossary.save_to_file(active_path)

    print(f"Term {term} added to glossary in {CURRENT_META_FILE}.")


def handle_remove(args: argparse.Namespace, glossary: Glossary) -> None:
    term = args.term[0]

    entry = glossary.find_by_term(term)
    if not entry:
        print(f"Entry '{term}' not found in glossary.")
        return

    print("Entry found in glossary.:")
    print_single_entry_as_table(entry)

    if not args.force:
        resp = input(f"Sure?: '{term}'(y/N): ").strip().lower()
        if resp not in ("y", "j", "yes"):
            print("Cancelled. Entry is not deleted.")
            return

    glossary.remove_by_term(term)

    active_path = get_active_filepath()
    glossary.save_to_file(str(active_path))

    print(f"Entry '{term}' is deleted.")


def handle_edit(args: argparse.Namespace, glossary: Glossary) -> None:
    orig_term = args.term[0]
    set_tags = None
    if args.set_tags:
        set_tags = [t.strip() for t in args.set_tags.split(",") if t.strip()]

    try:
        success = glossary.update_entry(
            original_term=orig_term,
            new_term=args.term_new,
            definition=args.definition,
            append_definition=args.append_definition,
            category=args.category,
            add_tags=args.add_tags,
            remove_tags=args.remove_tags,
            set_tags=set_tags,
            clear_tags=args.clear_tags,
            force=args.force
        )
    except ValueError as e:
        print(f"Fehler: {e}")
        sys.exit(2)

    if not success:
        print(f"Entry '{orig_term}' not found.")
        sys.exit(1)

    active_path = get_active_filepath()
    glossary.save_to_file(str(active_path))
    print(f"Entry '{orig_term}' updated.")
    new_term_to_show = args.term_new or orig_term
    entry = glossary.find_by_term(new_term_to_show)
    if entry:
        print_single_entry_as_table(entry)


def handle_list(args: argparse.Namespace, glossary: Glossary) -> None:
    entries = glossary.entries[:]

    tags_filter = []
    if getattr(args, "tags_csv", None):
        tags_filter = [t.strip() for t in args.tags_csv.split(",") if t.strip()]
    if getattr(args, "tags", None):
        tags_filter.extend([t.strip() for t in args.tags if t and t.strip()])

    tags_filter = [t.casefold() for t in tags_filter]

    category_filter = args.category.casefold() if args.category else None

    if category_filter:
        entries = [e for e in entries if (e.category or "").casefold() == category_filter]

    if tags_filter:
        if args.match_any:
            def tag_match_any(e: GlossaryEntry) -> bool:
                entry_tags = [t.casefold() for t in (e.tags or [])]
                return any(t in entry_tags for t in tags_filter)
            entries = [e for e in entries if tag_match_any(e)]
        else:
            def tag_match_all(e: GlossaryEntry) -> bool:
                entry_tags = [t.casefold() for t in (e.tags or [])]
                return all(t in entry_tags for t in tags_filter)
            entries = [e for e in entries if tag_match_all(e)]

    if getattr(args, "query", None):
        q = args.query.casefold()
        entries = [e for e in entries if q in (e.term or "").casefold()]

    entries.sort(key=lambda e: (e.term or "").casefold())

    total = len(entries)

    offset = max(0, args.offset or 0)
    limit = max(0, args.limit or 0)
    if offset:
        entries = entries[offset:]
    if limit:
        entries = entries[:limit]

    if not entries:
        if tags_filter or category_filter or getattr(args, "query", None):
            print("No Entries found using these filters..")
        else:
            print("No Entries found.")
        return

    for i, e in enumerate(entries, start=1 + offset):
        cat = e.category or "-"
        tags_display = ", ".join(e.tags) if e.tags else "-"
        print(f"{i}. {e.term}  [{cat}]  Tags: {tags_display}")

    shown = len(entries)
    if limit:
        print(f"\nShow {shown} entries (offset={offset}, limit={limit}). Overall {total} matches (before Paging).")
    else:
        print(f"\nShow {shown} entries. Overall {total} matches.")


def handle_list_glossaries(args: argparse.Namespace, glossary: Glossary) -> None:
    files = sorted(GLOSSARY_DIR.glob("*.json"))

    if not files:
        print("No glossary entries found.")
        return

    active_filepath = get_active_filepath().resolve()

    print("Available glossaries:")
    for index, path in enumerate(files, start=1):
        full_path = path.resolve()
        is_active = (full_path == active_filepath)
        name = path.name

        if is_active:
            print(f"{index}. {name} (active)")
        else:
            print(f"{index}. {name}")


def handle_checkout(args: argparse.Namespace, glossary: Glossary) -> None:
    filename = f"{args.filename}.json"
    path = GLOSSARY_DIR / filename

    if not path.exists():
        print(f"Glossary file {filename} does not exist in '{GLOSSARY_DIR}'.")
        print("Use 'list-glossaries' to see available glossaries.")
        return

    set_active_filepath(path)

    print(f"Glossary file set to '{path}'.")
    print(f"Entries in this glossary: {len(glossary.entries)}")
