import difflib
from pathlib import Path
import argparse
import textwrap
import sys
from .glossaryEntry import GlossaryEntry
from .glossary import Glossary

BASE_DIR = Path(__file__).resolve().parent.parent

GLOSSARY_DIR = BASE_DIR / "glossaries"
GLOSSARY_DIR.mkdir(exist_ok=True)

CURRENT_META_FILE = BASE_DIR / ".current_glossary"


def get_active_filepath() -> Path:
    if CURRENT_META_FILE.exists():
        path_str = CURRENT_META_FILE.read_text(encoding="utf-8").strip()
        if path_str:
            return Path(path_str)

    return Path("glossary.json")


def set_active_filepath(path: Path) -> None:
    CURRENT_META_FILE.write_text(str(path), encoding="utf-8")


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
        print(f"Eintrag '{orig_term}' nicht gefunden.")
        sys.exit(1)

    active_path = get_active_filepath()
    glossary.save_to_file(str(active_path))
    print(f"Eintrag '{orig_term}' erfolgreich aktualisiert.")
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
            print("Keine Einträge gefunden, die den Filtern entsprechen.")
        else:
            print("Keine Glossareinträge vorhanden.")
        return

    for i, e in enumerate(entries, start=1 + offset):
        cat = e.category or "-"
        tags_display = ", ".join(e.tags) if e.tags else "-"
        print(f"{i}. {e.term}  [{cat}]  Tags: {tags_display}")

    shown = len(entries)
    if limit:
        print(f"\nZeige {shown} Einträge (offset={offset}, limit={limit}). Insgesamt {total} Treffer (vor Paging).")
    else:
        print(f"\nZeige {shown} Einträge. Insgesamt {total} Treffer.")


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


def build_parser() -> argparse.ArgumentParser:
    epilog = """
    Examples:
      gloss init myglossary
      gloss add "My Term"
      gloss list --tag agile --category "Software Engineering"
      gloss edit "Justus Jonas" --add-tag detektiv
    Note: Subcommands must appear as the first argument; flags may be placed in any order.
    """
    parser = argparse.ArgumentParser(description="Glossary", epilog=epilog,
                                     formatter_class=argparse.RawTextHelpFormatter)

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
    )

    init_parser = subparsers.add_parser("init", help="Initialize glossary entries")
    init_parser.add_argument("name", type=str, help="Name of the glossary entry")
    init_parser.add_argument("-f", "--force", action="store_true", help="Force overwrite of existing glossary file")
    init_parser.set_defaults(func=handle_init)

    add_parser = subparsers.add_parser("add", help="Add glossary entries")
    add_parser.add_argument("term", type=str, help="Term that should be added")
    add_parser.set_defaults(func=handle_add)

    remove_parser = subparsers.add_parser("remove", help="Remove an existing glossary entry")
    remove_parser.add_argument("term", nargs=1, help="Exact term to remove")
    remove_parser.add_argument("-f", "--force", action="store_true", dest="force",
                               help="Remove without confirmation")
    remove_parser.set_defaults(func=handle_remove)

    list_parser = subparsers.add_parser("list", help="List glossary entries")
    list_parser.add_argument("--tag", action="append", dest="tags",
                             help="Filter: require tag (repeatable). Example: --tag ... -tag ...")
    list_parser.add_argument("--tags", dest="tags_csv", help="Filter: comma-separated tags (tag1,tag2)")
    list_parser.add_argument("--category", dest="category", help="Filter: category name")
    list_parser.add_argument("--match-any", action="store_true",
                             help="If set, match entries that have ANY of the provided tags (logical OR). "
                                  "Default is AND.")
    list_parser.add_argument("--query", dest="query",
                             help="Text search in Term (case-insensitive; will be applied after tag/category filtering)")
    list_parser.add_argument("--limit", default=0, type=int,
                             help="Limit the number of entries to display (0 = no Limit)")
    list_parser.add_argument("--offset", default=0, type=int, help="Offset for the entries to display")
    list_parser.set_defaults(func=handle_list)

    lg_parser = subparsers.add_parser("list-glossaries", help="List all available glossaries")
    lg_parser.set_defaults(func=handle_list_glossaries)

    checkout_parser = subparsers.add_parser("checkout", help="Switch active glossary")
    checkout_parser.add_argument("filename", type=str, help="Filename of the glossary (without .json)")
    checkout_parser.set_defaults(func=handle_checkout)

    edit_parser = subparsers.add_parser("edit", help="Edit an existing glossary entry")
    edit_parser.add_argument("term", nargs=1, help="Exact existing term to edit")
    edit_parser.add_argument("--term-new", dest="term_new", help="Rename the term")
    edit_parser.add_argument("--definition", help="Replace the definition (use Quotes)")
    edit_parser.add_argument("--append-definition", help="Append text to the definition")
    edit_parser.add_argument("--category", help="Set category")
    edit_parser.add_argument("--add-tag", action="append", dest="add_tags", help="Add a tag (repeatable)")
    edit_parser.add_argument("--remove-tag", action="append", dest="remove_tags",
                             help="Remove a tag (repeatable)")
    edit_parser.add_argument("--set-tags", help="Replace tags, comma separated (tag1,tag2)")
    edit_parser.add_argument("--clear-tags", action="store_true", dest="clear_tags", help="Clear all tags")
    edit_parser.add_argument("--force", action="store_true", dest="force",
                             help="Force overwrite of existing glossary file")
    edit_parser.set_defaults(func=handle_edit)

    return parser


def print_single_entry_as_table(entry: GlossaryEntry) -> None:
    labels = ["Term", "Definition", "Category", "Tags"]
    values =[
        entry.term,
        entry.definition,
        entry.category or "-",
        ", ".join(entry.tags) if entry.tags else "-",
    ]

    key_width = max(len(label) for label in labels)
    value_width = 70

    rows: list[tuple[str, str]] = []
    for label, value in zip(labels, values):
        wrapped_lines = textwrap.wrap(value, width=value_width) or [""]
        for i, line in enumerate(wrapped_lines):
            rows.append((
                label if i == 0 else "",
                line
            ))

    total_width = 2 + key_width + 3 + value_width + 2

    def print_seperator():
        print("+" + "-" * (key_width + 2) + "+" + "-" * (value_width + 2) + "+")

    def print_row(key: str, value: str) -> None:
        print(f"| {key:<{key_width}} | {value:<{value_width}} |")

    print_seperator()
    for i, (key, value) in enumerate(rows):
        print_row(key, value)

        if i + 1 < len(rows) and rows[i + 1][0] != "":
            print_seperator()

    print_seperator()


def main():
    commands = {"init", "add", "list", "checkout", "list-glossaries", "edit", "help", "remove"}

    argv = sys.argv[1:]

    glossary = Glossary()
    filepath = get_active_filepath()
    glossary.load_from_file(str(filepath))

    if not argv:
        parser = build_parser()
        parser.print_help()
        return

    first = argv[0]
    if first.startswith("-") or first in commands:
        parser = build_parser()
        args = parser.parse_args(argv)

        handler = getattr(args, "func", None)
        if handler:
            handler(args, glossary)
        else:
            parser.print_help()
        return

    term = " ".join(argv).strip()
    entry = glossary.find_by_term(term)
    if entry:
        print_single_entry_as_table(entry)
        return

    results = glossary.search(term)
    if not results:
        term_names = [e.term for e in glossary.entries]
        close = difflib.get_close_matches(term, term_names, n=5, cutoff=0.6)
        if close:
            print(f"No glossary entry with term: '{term}'. Did you mean: ")
            for c in close:
                print(f"- {c}")
            return
        else:
            print(f"No glossary entry found with term '{term}'.")
            return

    if len(results) == 1:
        print(f"Did you mean:")
        print_single_entry_as_table(results[0])
        return

    print(f"There are more than one glossary entry with your typed in: '{term}'.")
    for index, entry in enumerate(results, start=1):
        print(f"{index}. {entry.term}")
    print("Please type in one of the glossary entries.")
    return


if __name__ == "__main__":
    main()
