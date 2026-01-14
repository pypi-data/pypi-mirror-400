from __future__ import annotations

import re
from pathlib import Path


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def slugify(text: str) -> str:
    lowered = text.strip().lower()
    # Replace non-alphanumeric with hyphens
    slug = re.sub(r"[^a-z0-9]+", "-", lowered)
    # Collapse multiple hyphens and trim
    slug = re.sub(r"-{2,}", "-", slug).strip("-")
    return slug or "adr"


def parse_adr_filename(name: str) -> tuple[int, str, str] | None:
    """
    Parse filenames like '001-database-selection.md' -> (1, 'database-selection', 'md')
    Supports both .md and .docx extensions.
    """
    m = re.match(r"^(\d{3,})-([a-z0-9-]+)\.(md|docx)$", name)
    if not m:
        return None
    return int(m.group(1)), m.group(2), m.group(3)


def get_existing_adrs(adr_dir: Path, extension: str | None = None) -> list[tuple[int, str, Path]]:
    """
    Get existing ADRs from the directory.

    Args:
        adr_dir: Directory containing ADR files
        extension: Optional filter by extension ('md' or 'docx'). If None, returns all.

    Returns:
        List of (index, slug, path) tuples sorted by index
    """
    results: list[tuple[int, str, Path]] = []
    if not adr_dir.exists():
        return results

    # Scan both .md and .docx files
    for pattern in ["*.md", "*.docx"]:
        for p in adr_dir.glob(pattern):
            parsed = parse_adr_filename(p.name)
            if parsed:
                idx, slug, ext = parsed
                if extension is None or ext == extension:
                    results.append((idx, slug, p))

    # Remove duplicates (same index) keeping first occurrence, then sort
    seen_indices: set[int] = set()
    unique_results: list[tuple[int, str, Path]] = []
    ext_priority = {".md": 0, ".docx": 1}
    for item in sorted(results, key=lambda t: (t[0], ext_priority.get(t[2].suffix, 9))):
        if item[0] not in seen_indices:
            seen_indices.add(item[0])
            unique_results.append(item)

    return unique_results


def next_index(adr_dir: Path) -> int:
    existing = get_existing_adrs(adr_dir)
    if not existing:
        return 1
    return existing[-1][0] + 1


def format_index(n: int) -> str:
    return f"{n:03d}"



