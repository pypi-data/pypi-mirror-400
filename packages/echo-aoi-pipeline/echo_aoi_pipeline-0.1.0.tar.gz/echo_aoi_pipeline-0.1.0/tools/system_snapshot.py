#!/usr/bin/env python3
"""System snapshot command for on-demand status queries."""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Callable, Iterable

try:
    import yaml
except Exception:  # pragma: no cover
    yaml = None

ROOT = Path(__file__).resolve().parents[1]


def count_files(patterns: Iterable[str]) -> int:
    total = 0
    for pattern in patterns:
        total += sum(1 for _ in ROOT.rglob(pattern))
    return total


def latest_mtime(paths: Iterable[Path]) -> datetime | None:
    mtimes = [p.stat().st_mtime for p in paths if p.exists()]
    if not mtimes:
        return None
    return datetime.fromtimestamp(max(mtimes))


def load_yaml(path: Path) -> dict | None:
    if not path.exists() or yaml is None:
        return None
    try:
        return yaml.safe_load(path.read_text())
    except Exception:  # pragma: no cover
        return None


def section_docs(detail: bool = False, list_mode: bool = False) -> dict:
    md = count_files(["*.md"])
    yaml = count_files(["*.yaml", "*.yml"])
    last_update = latest_mtime(ROOT.glob("**/*.md"))
    return {
        "markdown": md,
        "yaml_yml": yaml,
        "python_files": count_files(["*.py"]),
        "last_doc_update": last_update.strftime("%Y-%m-%d") if last_update else "N/A",
    }


def section_loops(detail: bool = False, list_mode: bool = False) -> dict:
    loops = list(ROOT.rglob("*LOOP*.yaml"))
    registry = load_yaml(ROOT / "loop_registry.yaml")
    if registry and isinstance(registry.get("loop_registry"), list):
        entries = registry["loop_registry"]
        judgment_loops = sum(1 for entry in entries if entry.get("type") == "judgment")
        total = len(entries)
    else:
        judgment_loops = sum(1 for p in loops if "judgment" in p.name.lower() or "forget" in p.name.lower())
        total = len(loops)
    ratio = round(judgment_loops / total, 2) if total else 0
    data = {
        "total_loops": total,
        "judgment_loops": judgment_loops,
        "judgment_ratio": ratio,
    }
    if detail and registry and isinstance(registry.get("loop_registry"), list):
        data["details"] = [
            f"{entry.get('path')} [{entry.get('type')} / {entry.get('scope')} / {entry.get('maturity')}]"
            for entry in registry["loop_registry"]
        ]
    elif detail:
        data["details"] = [str(p.relative_to(ROOT)) for p in loops]
    if list_mode:
        if registry and isinstance(registry.get("loop_registry"), list):
            data["list_entries"] = [
                f"{Path(entry.get('path')).stem}: {entry.get('type')}"
                for entry in registry["loop_registry"]
            ]
        else:
            data["list_entries"] = [p.stem for p in loops]
    return data


def count_subdirectories(path: Path) -> int:
    if not path.exists():
        return 0
    return sum(1 for _ in path.iterdir() if _.is_dir() or _.suffix)


def section_features(detail: bool = False, list_mode: bool = False) -> dict:
    tools_dir = ROOT / "tools"
    ops_dir = ROOT / "ops"
    return {
        "tools_entries": count_subdirectories(tools_dir),
        "ops_entries": count_subdirectories(ops_dir),
    }


def section_projects(detail: bool = False, list_mode: bool = False) -> dict:
    project_dirs = [d for d in (ROOT / "project_vault").iterdir()] if (ROOT / "project_vault").exists() else []
    status_file = load_yaml(ROOT / "project_vault" / "PROJECT_STATUS.yaml")
    status_counts = {}
    if status_file and isinstance(status_file.get("projects"), list):
        for project in status_file["projects"]:
            status = project.get("status", "unknown")
            status_counts[status] = status_counts.get(status, 0) + 1
    data = {"project_entries": len(project_dirs), "status_counts": status_counts}
    if detail and status_file and isinstance(status_file.get("projects"), list):
        data["details"] = [
            f"{proj.get('name')}: {proj.get('status')} (last={proj.get('last_review')}, next={proj.get('next_decision')})"
            for proj in status_file["projects"]
        ]
    if list_mode and status_file and isinstance(status_file.get("projects"), list):
        data["list_entries"] = [
            f"{proj.get('name')}: {proj.get('status')}"
            for proj in status_file["projects"]
        ]
    return data


def section_core(detail: bool = False, list_mode: bool = False) -> dict:
    world_map = ROOT / "world" / "atlas" / "echo_world_atlas" / "echo_world_atlas_v1" / "01_WORLD_OVERVIEW.md"
    world_update = world_map.stat().st_mtime if world_map.exists() else None
    constitution = ROOT / "docs" / "system" / "SYSTEM_CONST.yaml"
    constitution_present = constitution.exists()
    return {
        "constitution_present": constitution_present,
        "world_map_update": datetime.fromtimestamp(world_update).strftime("%Y-%m-%d") if world_update else "N/A",
    }


def section_summary(detail: bool = False, list_mode: bool = False) -> dict:
    docs_count = count_files(["*.md", "*.yaml", "*.yml"])
    loops_count = len(list(ROOT.rglob("*LOOP*.yaml")))
    tools_count = count_subdirectories(ROOT / "tools")
    registry = load_yaml(ROOT / "loop_registry.yaml")
    if registry and isinstance(registry.get("loop_registry"), list):
        judgments = sum(1 for entry in registry["loop_registry"] if entry.get("type") == "judgment")
    else:
        judgments = sum(1 for p in ROOT.rglob("*LOOP*.yaml") if "judgment" in p.name.lower())
    ratio = round(judgments / loops_count, 2) if loops_count else 0
    return {
        "docs": docs_count,
        "loops": loops_count,
        "judgment_ratio": ratio,
        "tools": tools_count,
        "status": "STABLE",
    }


SECTIONS = {
    "docs": section_docs,
    "loops": section_loops,
    "features": section_features,
    "projects": section_projects,
    "core": section_core,
    "summary": section_summary,
}


def main() -> None:
    parser = argparse.ArgumentParser(description="System Snapshot")
    parser.add_argument("--section", action="append", choices=SECTIONS.keys(), help="Sections to display.")
    parser.add_argument("--json", action="store_true", help="Output JSON instead of text.")
    parser.add_argument("--detail", action="append", choices=SECTIONS.keys(), help="Sections to show detail for.")
    parser.add_argument("--list", action="append", choices=["loops", "projects"], help="Sections to list names/status.")
    args = parser.parse_args()

    sections = args.section or ["summary"]
    list_sections = set(args.list or [])
    for name in list_sections:
        if name not in sections:
            sections.append(name)
    output = {}

    for name in sections:
        detail = args.detail and name in args.detail
        output[name] = SECTIONS[name](bool(detail), name in list_sections)

    if args.json:
        print(json.dumps(output, indent=2))
    else:
        for section_name in sections:
            header = section_name.upper()
            if section_name in list_sections:
                header += " (list)"
            print(header)
            for key, value in output[section_name].items():
                if key == "details":
                    print("- Details:")
                    for item in value:
                        print(f"  • {item}")
                    continue
                if key == "list_entries":
                    print("- Items:")
                    for item in value:
                        print(f"  • {item}")
                    continue
                print(f"- {key.replace('_', ' ').title()}: {value}")
            print()


if __name__ == "__main__":
    main()
