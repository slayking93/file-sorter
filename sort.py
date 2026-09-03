"""CLI entry point for the file sorter."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from src.sorter import iter_files, plan_moves, run


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="sort",
        description="Sort files in a folder into subfolders by extension.",
    )
    parser.add_argument(
        "folder",
        type=Path,
        help="Path to the folder to sort (top level only by default).",
    )
    parser.add_argument(
        "-r",
        "--recursive",
        action="store_true",
        help="Also sort files in subdirectories. Subdirs themselves are kept.",
    )
    parser.add_argument(
        "-n",
        "--dry-run",
        action="store_true",
        help="Show what would be moved without touching the filesystem.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)

    if not args.folder.exists():
        print(f"error: path does not exist: {args.folder}", file=sys.stderr)
        return 2
    if not args.folder.is_dir():
        print(f"error: not a directory: {args.folder}", file=sys.stderr)
        return 2

    if args.dry_run:
        moves = plan_moves(iter_files(args.folder, args.recursive), args.folder)
        if not moves:
            print("Nothing to move.")
            return 0
        print(f"Would move {len(moves)} file(s):")
        for move in moves:
            print(f"  {move.src} -> {move.target}")
        return 0

    try:
        moved = run(args.folder, recursive=args.recursive)
    except NotADirectoryError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    print(f"Moved {moved} file(s) into subfolders of {args.folder}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())