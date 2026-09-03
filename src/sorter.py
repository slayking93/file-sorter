"""File sorting by extension. Pure logic, no CLI concerns."""
from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Iterator

NO_EXTENSION = "no_extension"


@dataclass(frozen=True)
class Move:
    src: Path
    target: Path


def classify(path: Path) -> str:
    """Return the destination folder name for a file based on its extension.

    Rules:
      - Extension is lowercased, leading dot stripped ("a.JPG" -> "jpg").
      - Files without an extension go to "no_extension".
      - Dotted names without a real suffix (e.g. "Makefile") also go to "no_extension".
    """
    suffix = path.suffix.lower()
    return suffix[1:] if suffix else NO_EXTENSION


def resolve_collision(target_dir: Path, name: str) -> Path:
    """Return a non-conflicting path inside target_dir for the given filename.

    On conflict, append "_1", "_2", ... before the extension until the
    name is free. The original file is never overwritten.
    """
    candidate = target_dir / name
    if not candidate.exists():
        return candidate

    stem = Path(name).stem
    suffix = Path(name).suffix
    n = 1
    while (candidate := target_dir / f"{stem}_{n}{suffix}").exists():
        n += 1
    return candidate


def iter_files(root: Path, recursive: bool) -> Iterator[Path]:
    """Yield files under root. Top level only unless recursive=True."""
    if recursive:
        yield from (p for p in root.rglob("*") if p.is_file())
    else:
        yield from (p for p in root.iterdir() if p.is_file())


def plan_moves(files: Iterable[Path], dest_root: Path) -> list[Move]:
    """Build a list of planned file moves without touching disk."""
    moves: list[Move] = []
    for src in files:
        ext = classify(src)
        target_dir = dest_root / ext
        target = resolve_collision(target_dir, src.name)
        moves.append(Move(src=src, target=target))
    return moves


def run(src_dir: Path, recursive: bool = False) -> int:
    """Sort files in src_dir into subdirs by extension.

    Returns the number of files moved. Raises NotADirectoryError if
    src_dir does not exist or is not a directory.
    """
    if not src_dir.is_dir():
        raise NotADirectoryError(f"{src_dir} is not a directory")

    moved = 0
    for move in plan_moves(iter_files(src_dir, recursive), src_dir):
        move.target.parent.mkdir(exist_ok=True)
        shutil.move(str(move.src), str(move.target))
        moved += 1
    return moved