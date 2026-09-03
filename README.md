# File Sorter by Extension

Small CLI utility that sorts files in a folder into subfolders by extension. Useful for tidying up a `Downloads/` directory or any other messy folder.

## Quick start

Run directly without installing:

```bash
python sort.py <path_to_folder>
```

Example:

```bash
python sort.py ./messy-folder
```

Result: `messy-folder/jpg/`, `messy-folder/pdf/`, `messy-folder/no_extension/`, …

Or install as a package and use the `sort` command anywhere:

```bash
pip install -e .
sort ./messy-folder
```

## Flags

| Flag | Short | Description |
| --- | --- | --- |
| `--recursive` | `-r` | Also sort files in subdirectories. The subdirectories themselves are kept; their files are moved to the matching category folders at the top level. |
| `--dry-run` | `-n` | Show what would be moved without touching the filesystem. |

Typical workflow:

```bash
sort ./Downloads --dry-run         # preview
sort ./Downloads                   # commit
sort ./Downloads --recursive       # recurse into subdirs too
```

## Rules

- Top level only by default. Pass `--recursive` to descend.
- Extension is lowercased, leading dot stripped (`a.JPG` → `jpg/`).
- Files without a real extension go to `no_extension/`.
- On name collision inside the target subfolder, a suffix `_1`, `_2`, … is appended. Originals are never overwritten.
- Files are **moved** (not copied).

## Exit codes

- `0` — success.
- `2` — path does not exist or is not a directory (error message on stderr).

## Development

Install dev dependencies and run tests:

```bash
pip install -r requirements-dev.txt
pytest -q
```

See `SPEC.md` for the full specification.