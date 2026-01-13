#!/usr/bin/env python3
"""Quick viewer for cpsm_module3_judgment_db.md entries."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import re
import sys
from typing import Dict, List

DB_PATH = Path("cpsm_module3_judgment_db.md")


@dataclass
class Entry:
    ident: str
    title: str
    body: str
    alias: str | None = None
    source: str = "기존"  # "기존" or "시뮬레이션"
    date: str = ""  # YYYY-MM-DD format


ENTRY_HEADER_RE = re.compile(
    r"^## 🧠 기록 (?P<id>[\w\-]+)\s*\n\n\| 항목 \| 내용 \|\n\| --- \| --- \|\n\| 문제 ID \| (?P<name>.+?) \|\n",
    re.MULTILINE,
)


def load_entries(db_path: Path) -> Dict[str, Entry]:
    try:
        text = db_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        print(f"[error] {db_path} not found. Run from repo root.", file=sys.stderr)
        sys.exit(1)

    matches = list(ENTRY_HEADER_RE.finditer(text))
    entries: Dict[str, Entry] = {}

    for idx, match in enumerate(matches):
        ident = match.group("id").strip()
        title_field = match.group("name").strip()
        alias_match = re.match(r"([0-9A-Za-z\-]+)", title_field)
        alias = alias_match.group(1) if alias_match else None
        start = match.start()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
        body = text[start:end].strip()

        # Extract metadata from body
        source = "기존"  # default
        date_str = ""

        # Try to extract date from header (e.g., "2025-02-XX")
        date_match = re.search(r"기록 (20\d{2}-\d{2}-\d{2})", body)
        if date_match:
            date_str = date_match.group(1).replace("XX", "01")  # Normalize XX to 01

        # Check if it's from simulation (can add markers later)
        if "시뮬레이션" in body or "자동생성" in body:
            source = "시뮬레이션"

        entries[ident] = Entry(
            ident=ident,
            title=title_field,
            body=body,
            alias=alias,
            source=source,
            date=date_str
        )

    # Add alias keys if present (e.g., 202502XX-LB001)
    alias_map: Dict[str, Entry] = {}
    for entry in entries.values():
        if entry.alias and entry.alias not in entries:
            alias_map[entry.alias] = entry

    entries.update(alias_map)

    return entries


def list_entries(entries: Dict[str, Entry], sort_by: str = "newest", filter_source: str = "") -> None:
    print("Available entries:")
    seen: set[str] = set()
    unique_entries = []

    for entry in entries.values():
        if entry.ident not in seen:
            seen.add(entry.ident)
            unique_entries.append(entry)

    # Filter by source
    if filter_source:
        unique_entries = [e for e in unique_entries if e.source == filter_source]

    # Sort
    if sort_by == "newest":
        unique_entries.sort(key=lambda e: e.date or "9999", reverse=True)
    elif sort_by == "oldest":
        unique_entries.sort(key=lambda e: e.date or "0000")
    elif sort_by == "id":
        unique_entries.sort(key=lambda e: e.alias or e.ident)

    for entry in unique_entries:
        label = entry.alias or entry.ident
        source_tag = f"[{entry.source}]" if entry.source else ""
        date_tag = f"({entry.date})" if entry.date else ""
        print(f" - {label}: {entry.title} {source_tag} {date_tag}")


def show_entry(entry: Entry) -> None:
    print(entry.body)


def interactive_mode(entries: Dict[str, Entry]) -> None:
    list_entries(entries)
    try:
        choice = input("\nEnter entry ID to view (or blank to exit): ").strip()
    except (EOFError, KeyboardInterrupt):
        print()
        return
    if not choice:
        return
    entry = entries.get(choice)
    if not entry:
        print(f"[warn] Unknown ID '{choice}'.")
        return
    print()
    show_entry(entry)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="View entries from cpsm_module3_judgment_db.md quickly."
    )
    parser.add_argument("--list", action="store_true", help="List all entry IDs.")
    parser.add_argument(
        "--id",
        metavar="ENTRY_ID",
        help="Show a specific entry (e.g., 202502XX-LB010).",
    )
    parser.add_argument(
        "--sort",
        choices=["newest", "oldest", "id"],
        default="newest",
        help="Sort order: newest (default), oldest, or id",
    )
    parser.add_argument(
        "--source",
        choices=["기존", "시뮬레이션"],
        help="Filter by source: 기존 or 시뮬레이션",
    )
    parser.add_argument(
        "--db-path",
        default=DB_PATH,
        type=Path,
        help="Path to cpsm_module3_judgment_db.md (default: repo root).",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    entries = load_entries(args.db_path)

    if args.list:
        list_entries(entries, sort_by=args.sort, filter_source=args.source or "")
        return

    if args.id:
        entry = entries.get(args.id)
        if not entry:
            print(f"[error] Unknown ID '{args.id}'. Use --list to see options.")
            sys.exit(1)
        show_entry(entry)
        return

    interactive_mode(entries)


if __name__ == "__main__":
    main()
