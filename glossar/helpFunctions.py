import textwrap

from glossar.glossaryEntry import GlossaryEntry


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
