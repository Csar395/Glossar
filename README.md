# Glossar CLI

A command-line interface (CLI) tool for managing glossaries.

## Installation

You can install `glossar` using `pip`:

```bash
pip install .
```

Alternatively, if you are developing, you can install it in editable mode:

```bash
pip install -e .
```

## Glossary Entry Structure

Each entry in the glossary has the following structure:

- **Term**: The word or phrase to be defined. (Required)
- **Definition**: The explanation of the term. (Required)
- **Category**: An optional category to group the term.
- **Tags**: A list of optional tags for more granular filtering.

## Managing Glossaries

You can manage multiple glossaries and switch between them.

### Initialize a new Glossary
This command creates a new, empty glossary file in the `glossaries/` directory and sets it as the active glossary.

```bash
glossar init <glossary-name>
```
- `<glossary-name>`: The name for your new glossary (e.g., `my-project`).

Example:
```bash
glossar init programming-terms
```

### List available Glossaries
This command lists all the glossary files you have created.

```bash
glossar list-glossaries
```

### Switch active Glossary
This command allows you to switch which glossary you are working with.

```bash
glossar checkout <glossary-name>
```
- `<glossary-name>`: The name of the glossary to switch to (without the `.json` extension).

Example:
```bash
glossar checkout programming-terms
```

## Managing Entries

### Add an Entry
This command interactively prompts you to add a new term to the currently active glossary.

```bash
glossar add "<term>"
```
- `"<term>"`: The term you want to add. Use quotes for multi-word terms.

You will be prompted to provide the definition, and optionally a category and tags.

### View an Entry
To view a single entry, just type the term.

```bash
glossar "<term>"
```
If a unique match is found, its details will be displayed. If multiple entries match your query, a list of suggestions will be shown.

### List and Filter Entries
This command lists all entries in the active glossary, with powerful filtering options.

```bash
glossar list
```

**Options:**
- `--query <text>`: Search for text within the term.
- `--category <name>`: Filter by a specific category.
- `--tags <tag1,tag2>`: Filter by a comma-separated list of tags (entries must have ALL specified tags).
- `--tag <tag>`: Filter by a specific tag. This can be used multiple times (e.g., `glossar list --tag python --tag cli`).
- `--match-any`: When used with multiple `--tag` flags, it will list entries that have ANY of the tags (instead of all).
- `--limit <number>`: Limit the number of entries displayed.
- `--offset <number>`: Skip a number of entries.

Examples:
```bash
# List all entries
glossar list

# Find entries with "API" in the term
glossar list --query API

# List all entries in the "DevOps" category
glossar list --category "DevOps"

# List entries tagged with both "python" and "cli"
glossar list --tags "python,cli"
```

### Edit an Entry
This command allows you to modify an existing glossary entry.

```bash
glossar edit "<term>" [options]
```
- `"<term>"`: The exact term of the entry you want to edit.

**Options:**
- `--term-new "<new-term>"`: Rename the term.
- `--definition "<new-def>"`: Replace the entire definition.
- `--append-definition "<text>"`: Add text to the end of the current definition.
- `--category "<new-cat>"`: Change the category.
- `--add-tag <tag>`: Add a new tag. Can be used multiple times.
- `--remove-tag <tag>`: Remove a tag. Can be used multiple times.
- `--set-tags <tag1,tag2>`: Replace all existing tags with a new list.
- `--clear-tags`: Remove all tags from the entry.

Example:
```bash
glossar edit "API" --add-tag "web" --category "Web Development"
```

### Remove an Entry
This command deletes an entry from the glossary.

```bash
glossar remove "<term>"
```
- `"<term>"`: The exact term to remove.
- `--force` or `-f`: Use this flag to skip the confirmation prompt.

## Contributing

Contributions are welcome! Please feel free to open issues or pull requests.

## License

This project is licensed under the MIT License.