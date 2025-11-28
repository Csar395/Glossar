import difflib
from pathlib import Path
import sys

from glossar.helpFunctions import print_single_entry_as_table
from glossar.parser import build_parser
from glossar.pathFunctions import get_active_filepath
from glossar.glossary import Glossary

BASE_DIR = Path(__file__).resolve().parent.parent

GLOSSARY_DIR = BASE_DIR / "glossaries"
GLOSSARY_DIR.mkdir(exist_ok=True)

CURRENT_META_FILE = BASE_DIR / ".current_glossary"


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
