import argparse

from glossar.handleFunctions import handle_init, handle_add, handle_remove, handle_list, handle_list_glossaries, \
    handle_checkout, handle_edit


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
