"""
Code State Report Generator.

Produces a neutral report describing what was mechanically verified,
what tests observed, which areas remain unverified, and which domains
were outside the scope of the run.
"""

from __future__ import annotations

import argparse
import ast
import json
import py_compile
import re
import textwrap
from dataclasses import dataclass
from pathlib import Path
from typing import List, Sequence, Set, Tuple


# Keywords that hint at external or recovery logic.
EXTERNAL_CALL_HINTS = ("request", "client", "http", "api", "socket")
RETRY_TIMEOUT_HINTS = ("retry", "timeout", "backoff", "sleep")
KNOWN_UNVERIFIED_DEFAULTS = (
    "Performance ceilings and latency characteristics were not evaluated.",
    "Security posture, threat models, and vulnerability scans were not performed.",
    "Operational environment differences (staging vs production) were not reviewed.",
    "Data distribution changes and drift behavior were not analyzed.",
)
FILE_LINE_PATTERN = re.compile(r"file:\s*(?P<file>[^,]+)(?:,\s*line\s*(?P<line>\d+))?", re.IGNORECASE)


@dataclass
class TestSummary:
    lines: List[str]
    observed_paths: Set[str]
    noted_unexecuted: List[str]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a Code State Report without issuing approvals."
    )
    parser.add_argument(
        "--paths",
        nargs="*",
        default=["."],
        help="Directories or files to inspect for source files (default: current directory).",
    )
    parser.add_argument(
        "--diff",
        type=Path,
        help="Optional unified diff file to scope analysis to changed Python files.",
    )
    parser.add_argument(
        "--test-report",
        type=Path,
        help="Optional JSON or text file describing test execution details.",
    )
    parser.add_argument(
        "--extra-unverified",
        action="append",
        default=[],
        help="Additional statements to add under 'Present but Unverified'.",
    )
    parser.add_argument(
        "--extra-not-evaluated",
        action="append",
        default=[],
        help="Additional domains to list under 'Not Evaluated in This Process'.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional file path to write the report instead of stdout.",
    )
    parser.add_argument(
        "--topic-config",
        type=Path,
        help="Optional JSON file to influence topic selection disclosure (retopic scenarios).",
    )
    return parser.parse_args()


def gather_python_files(paths: Sequence[str], diff_paths: Set[Path] | None = None) -> List[Path]:
    collected: Set[Path] = set()
    for raw in paths:
        target = Path(raw)
        if not target.exists():
            continue
        if target.is_dir():
            for file_path in target.rglob("*.py"):
                if diff_paths and file_path.resolve() not in diff_paths:
                    continue
                collected.add(file_path.resolve())
        elif target.suffix == ".py":
            collected.add(target.resolve())
    if diff_paths:
        # Ensure diff files outside provided directories are included if present.
        for file_path in diff_paths:
            if file_path.suffix == ".py":
                collected.add(file_path)
    return sorted(collected)


def parse_diff_file(diff_file: Path) -> Set[Path]:
    if not diff_file or not diff_file.exists():
        return set()
    result: Set[Path] = set()
    for line in diff_file.read_text().splitlines():
        if line.startswith("+++ b/"):
            rel = line.split("+++ b/", 1)[1].strip()
            if rel != "/dev/null":
                result.add(Path(rel).resolve())
    return result


def run_mechanical_verification(files: Sequence[Path]) -> List[str]:
    entries: List[str] = []
    if not files:
        entries.append("No Python source files were supplied; syntax checks were not executed.")
    else:
        ok_count = 0
        failures: List[str] = []
        for file_path in files:
            try:
                py_compile.compile(str(file_path), doraise=True)
                ok_count += 1
            except Exception as exc:  # noqa: BLE001
                failures.append(f"{file_path}: {exc}")
        entries.append(
            f"Python syntax compilation via py_compile executed on {len(files)} file(s); "
            f"{ok_count} succeeded."
        )
        if failures:
            for failure in failures:
                entries.append(f"- Syntax compilation error: {failure}")
    entries.append("Static type analysis: Not executed (no artifacts supplied).")
    entries.append("Build/interface conformance checks: Not executed (no automation configured).")
    return entries


def load_test_report(report_path: Path | None) -> TestSummary:
    if not report_path:
        return TestSummary(lines=["No tests executed or supplied."], observed_paths=set(), noted_unexecuted=[])
    try:
        raw_text = report_path.read_text()
    except OSError as exc:
        return TestSummary(
            lines=[f"Test artifact could not be loaded ({exc})."],
            observed_paths=set(),
            noted_unexecuted=[],
        )
    try:
        data = json.loads(raw_text)
    except json.JSONDecodeError:
        preview = "\n".join(raw_text.splitlines()[:5])
        lines = [
            "Unstructured test log provided; parser recorded the following sample lines:",
            *[f"- {line}" for line in preview.splitlines() if line],
        ]
        if not preview:
            lines.append("- (log was empty)")
        return TestSummary(lines=lines, observed_paths=set(), noted_unexecuted=[])
    return summarize_structured_tests(data)


def summarize_structured_tests(payload: object) -> TestSummary:
    runs = []
    if isinstance(payload, dict):
        if "runs" in payload and isinstance(payload["runs"], list):
            runs = payload["runs"]
        else:
            runs = [payload]
    elif isinstance(payload, list):
        runs = payload
    lines: List[str] = []
    observed: Set[str] = set()
    noted_unexecuted: List[str] = []
    if not runs:
        return TestSummary(lines=["Structured test artifact contained no runs."], observed_paths=set(), noted_unexecuted=[])
    for idx, run in enumerate(runs, start=1):
        if not isinstance(run, dict):
            lines.append(f"Run {idx}: Unsupported structure (expected object, got {type(run).__name__}).")
            continue
        name = run.get("name") or run.get("command") or f"Run {idx}"
        lines.append(f"{name}:")
        executed = _coerce_list(run.get("executed") or run.get("inputs") or run.get("cases"))
        if executed:
            observed.update(executed)
            lines.extend(f"- Observed input: {item}" for item in executed)
        else:
            lines.append("- No explicit input list provided.")
        failures = _coerce_list(run.get("failures") or run.get("failed"))
        if failures:
            for failure in failures:
                if isinstance(failure, dict):
                    label = failure.get("name") or failure.get("id") or "Unnamed failure"
                    detail = failure.get("detail") or failure.get("message") or "No detail supplied."
                    lines.append(f"- Failure observed: {label} — {detail}")
                else:
                    lines.append(f"- Failure observed: {failure}")
        else:
            lines.append("- No failures recorded in artifact.")
        unexecuted = _coerce_list(run.get("unexecuted") or run.get("unexecuted_paths") or run.get("missing"))
        if unexecuted:
            noted_unexecuted.extend(str(item) for item in unexecuted)
            for path in unexecuted:
                lines.append(f"- Code path not executed: {path}")
        coverage_gaps = _coerce_list(run.get("uncovered") or run.get("excluded"))
        for gap in coverage_gaps:
            lines.append(f"- Coverage gap noted: {gap}")
    return TestSummary(lines=lines, observed_paths=observed, noted_unexecuted=noted_unexecuted)


def _coerce_list(value: object) -> List[str]:
    if not value:
        return []
    if isinstance(value, list):
        return [str(item) for item in value]
    return [str(value)]


def analyze_unverified_regions(
    files: Sequence[Path],
    observed_paths: Set[str],
    test_noted_unexecuted: Sequence[str],
    extra: Sequence[str],
) -> List[str]:
    entries: List[str] = []
    if not files:
        entries.append("No source files were provided, so unverified regions could not be enumerated.")
        entries.extend(extra)
        return entries
    if not observed_paths:
        entries.append("No execution artifacts referenced specific code paths; sections below reflect static inspection only.")
    for noted in test_noted_unexecuted:
        entries.append(f"- Reported as unexecuted by tests: {noted}")
    for feature in extract_structural_features(files):
        if not _path_seen(feature.file, observed_paths):
            entries.append(
                f"- {feature.description} (file: {feature.file}, line {feature.lineno}) remains unobserved."
            )
    if not entries:
        entries.append("Static inspection found no obvious exception, retry, or external-call blocks.")
    entries.extend(extra)
    return entries


@dataclass
class StructuralFeature:
    file: Path
    lineno: int
    description: str


@dataclass
class SimulationScenario:
    assumption: str
    observable_path: str
    affected_units: str
    uncertainty: str


@dataclass
class RiskEntry:
    trigger: str
    impact: str
    alternatives: List[str]


@dataclass
class TopicDisclosure:
    selected_topics: List[Tuple[str, str]]
    excluded_topics: List[str]
    priority_statement: str



def extract_structural_features(files: Sequence[Path]) -> List[StructuralFeature]:
    features: List[StructuralFeature] = []
    for file_path in files:
        try:
            source = file_path.read_text()
            tree = ast.parse(source)
        except (OSError, SyntaxError):
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Try):
                for handler in node.handlers:
                    typ = _describe_exception_type(handler.type)
                    features.append(
                        StructuralFeature(
                            file=file_path,
                            lineno=getattr(handler, "lineno", 0),
                            description=f"Exception handler for {typ or 'generic error'}",
                        )
                    )
            elif isinstance(node, ast.Call):
                call_name = _call_name(node)
                normalized_name = call_name.lower()
                if any(hint in normalized_name for hint in RETRY_TIMEOUT_HINTS):
                    features.append(
                        StructuralFeature(
                            file=file_path,
                            lineno=getattr(node, "lineno", 0),
                            description=f"Retry/timeout logic via call `{call_name}`",
                        )
                    )
                if any(hint in normalized_name for hint in EXTERNAL_CALL_HINTS):
                    features.append(
                        StructuralFeature(
                            file=file_path,
                            lineno=getattr(node, "lineno", 0),
                            description=f"External/system call `{call_name}`",
                        )
                    )
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                module_name = _import_name(node)
                if module_name and any(hint in module_name for hint in EXTERNAL_CALL_HINTS):
                    features.append(
                        StructuralFeature(
                            file=file_path,
                            lineno=getattr(node, "lineno", 0),
                            description=f"External dependency import `{module_name}`",
                        )
                    )
    return features


def _describe_exception_type(node: ast.AST | None) -> str:
    if node is None:
        return ""
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return f"{_describe_exception_type(node.value)}.{node.attr}".strip(".")
    if isinstance(node, ast.Tuple):
        return ", ".join(_describe_exception_type(elt) for elt in node.elts)
    return ""


def _call_name(node: ast.Call) -> str:
    func = node.func
    if isinstance(func, ast.Name):
        return func.id
    if isinstance(func, ast.Attribute):
        return _attr_chain(func)
    return "unknown_call"


def _attr_chain(node: ast.Attribute) -> str:
    value = node.value
    if isinstance(value, ast.Attribute):
        return f"{_attr_chain(value)}.{node.attr}"
    if isinstance(value, ast.Name):
        return f"{value.id}.{node.attr}"
    return node.attr


def _import_name(node: ast.AST) -> str:
    if isinstance(node, ast.Import):
        return ", ".join(alias.name for alias in node.names)
    if isinstance(node, ast.ImportFrom):
        module = node.module or ""
        names = ", ".join(alias.name for alias in node.names)
        return f"{module}.{names}".strip(".")
    return ""


def _path_seen(file_path: Path, observed_paths: Set[str]) -> bool:
    return any(str(file_path) in path for path in observed_paths)


def build_not_evaluated_section(extra: Sequence[str]) -> List[str]:
    statements = list(KNOWN_UNVERIFIED_DEFAULTS)
    statements.extend(extra)
    return list(dict.fromkeys(statements))  # preserve order, remove duplicates


def render_report(
    mechanical: Sequence[str],
    tests: Sequence[str],
    unverified: Sequence[str],
    not_evaluated: Sequence[str],
) -> str:
    sections = [
        ("Mechanically Verified Behavior", mechanical),
        ("Observed via Tests", tests),
        ("Present but Unverified", unverified),
        ("Not Evaluated in This Process", not_evaluated),
    ]
    lines = ["Code State Report", ""]
    for title, body in sections:
        lines.append(f"{title}")
        lines.append("")
        if body:
            for item in body:
                wrapped = textwrap.wrap(item, width=100)
                if not wrapped:
                    continue
                lines.append(f"- {wrapped[0]}")
                for continuation in wrapped[1:]:
                    lines.append(f"  {continuation}")
        else:
            lines.append("- No entries.")
        lines.append("")
    lines.append(
        "This report does not approve execution. It only describes observed states and explicitly lists "
        "unobserved states."
    )
    return "\n".join(lines).rstrip() + "\n"


def generate_simulation_scenarios(
    unverified_entries: Sequence[str], not_evaluated_entries: Sequence[str]
) -> List[SimulationScenario]:
    scenarios: List[SimulationScenario] = []
    for entry in unverified_entries:
        text = entry.lstrip("- ").strip()
        if not text:
            continue
        scenarios.append(_scenario_from_unverified(text))
    for entry in not_evaluated_entries:
        text = entry.lstrip("- ").strip()
        if not text:
            continue
        scenarios.append(_scenario_from_not_evaluated(text))
    if not scenarios:
        scenarios.append(
            SimulationScenario(
                assumption="Assume uninstrumented code paths receive unexpected inputs.",
                observable_path="Not instrumented (no files inspected).",
                affected_units="Unknown modules.",
                uncertainty="Behavioral outcome cannot be inferred because no evidence exists.",
            )
        )
    return scenarios


def _scenario_from_unverified(text: str) -> SimulationScenario:
    file_hint, line_hint = _extract_file_and_line(text)
    assumption = _build_assumption_from_text(text)
    observable = file_hint or "Not instrumented (static statement only)."
    if line_hint:
        observable = f"{observable}:{line_hint}" if observable else f"Line {line_hint}"
    affected = _derive_affected_unit(file_hint)
    uncertainty = "Result is undefined because this branch never executed during reporting."
    return SimulationScenario(
        assumption=assumption,
        observable_path=observable or "Not specified in report.",
        affected_units=affected,
        uncertainty=uncertainty,
    )


def _scenario_from_not_evaluated(text: str) -> SimulationScenario:
    lower = text.lower()
    if "performance" in lower or "latency" in lower:
        assumption = "Assume load increases beyond current capacity envelopes."
        affected = "Throughput-sensitive services."
        observable = "Global execution paths under sustained concurrency."
    elif "security" in lower or "vulnerability" in lower:
        assumption = "Assume unpatched dependency exposes inputs that require validation."
        affected = "Interfaces handling external data."
        observable = "Request parsing flows."
    elif "operational" in lower or "environment" in lower:
        assumption = "Assume production configuration diverges from tested environment variables."
        affected = "Boot/config loaders."
        observable = "Deployment initialization paths."
    elif "data" in lower or "distribution" in lower:
        assumption = "Assume incoming data distribution shifts away from test fixtures."
        affected = "Parsing and validation routines."
        observable = "Normalization layer functions."
    else:
        assumption = f"Assume conditions related to '{text}' change unexpectedly."
        affected = "Related subsystems noted in Code State Report."
        observable = "Not instrumented (not evaluated category)."
    uncertainty = "Impact cannot be quantified because the domain was explicitly not evaluated."
    return SimulationScenario(
        assumption=assumption,
        observable_path=observable,
        affected_units=affected,
        uncertainty=uncertainty,
    )


def _extract_file_and_line(text: str) -> tuple[str, str]:
    match = FILE_LINE_PATTERN.search(text)
    if not match:
        return "", ""
    file_hint = (match.group("file") or "").strip().rstrip(").")
    line_hint = (match.group("line") or "").strip()
    return file_hint, line_hint


def _build_assumption_from_text(text: str) -> str:
    lower = text.lower()
    if "exception handler" in lower:
        return "Assume the referenced exception path is triggered by unexpected input."
    if "retry" in lower or "timeout" in lower:
        return "Assume upstream latency surpasses configured retry thresholds."
    if "external/system call" in lower or "external dependency" in lower:
        return "Assume external services respond slowly or with malformed payloads."
    if "unexecuted" in lower:
        return "Assume the unexecuted branch begins running under new conditions."
    return f"Assume the unverified statement '{text}' encounters altered runtime conditions."


def _derive_affected_unit(file_hint: str) -> str:
    if not file_hint:
        return "Module unspecified."
    path = Path(file_hint)
    return path.stem or str(path)


def render_simulation_report(scenarios: Sequence[SimulationScenario]) -> str:
    lines = ["Simulation Preview Report", ""]
    for scenario in scenarios:
        lines.append(f"- Assumption: {scenario.assumption}")
        lines.append(f"  Observable Path: {scenario.observable_path}")
        lines.append(f"  Affected Units: {scenario.affected_units}")
        lines.append(f"  Uncertainty: {scenario.uncertainty}")
        lines.append("")
    lines.append(
        "These simulations describe assumption-based thought experiments. They do not predict outcomes "
        "or approve execution."
    )
    return "\n".join(lines).rstrip() + "\n"


def generate_risk_entries(scenarios: Sequence[SimulationScenario]) -> List[RiskEntry]:
    entries: List[RiskEntry] = []
    for scenario in scenarios:
        trigger = scenario.assumption
        observable = scenario.observable_path or "Not instrumented."
        affected = scenario.affected_units or "Unspecified modules."
        impact = (
            f"When this condition occurs, execution can traverse {observable} and involve {affected}. "
            f"{scenario.uncertainty}"
        )
        alternatives = [
            f"Design additional tests to observe {observable} while the condition is present.",
            f"Introduce guard logic so the condition halts execution before {affected} runs.",
            f"Limit execution scope touching {affected} until evidence exists under this condition.",
            f"Insert a human approval checkpoint for operations involving {affected} when this condition is detected.",
        ]
        entries.append(RiskEntry(trigger=trigger, impact=impact, alternatives=alternatives))
    if not entries:
        entries.append(
            RiskEntry(
                trigger="Assume unobserved code paths receive unexpected input.",
                impact="Behavioral impact cannot be described because no files were inspected.",
                alternatives=[
                    "Map the codebase to identify which modules would run under the assumed condition.",
                    "Limit execution to previously observed modules until mapping completes.",
                    "Stage an approval checkpoint before running unobserved modules.",
                ],
            )
        )
    return entries


def render_risk_report(entries: Sequence[RiskEntry]) -> str:
    lines = ["Risk & Alternatives Report", ""]
    for entry in entries:
        lines.append("<details>")
        lines.append(f"<summary>Risk Trigger Condition: {entry.trigger}</summary>")
        lines.append("")
        lines.append(f"- Observed or Simulated Impact: {entry.impact}")
        lines.append("- Available Alternatives:")
        for alt in entry.alternatives:
            lines.append(f"  * {alt}")
        lines.append("")
        lines.append("</details>")
        lines.append("")
    lines.append(
        "This layer lists conditions, impacts, and available human actions. It does not approve execution or "
        "remove risk."
    )
    return "\n".join(lines).rstrip() + "\n"


def build_topic_disclosure(
    unverified_entries: Sequence[str],
    not_evaluated_entries: Sequence[str],
    scenarios: Sequence[SimulationScenario],
    topic_config: dict[str, object] | None,
) -> TopicDisclosure:
    selected: List[Tuple[str, str]] = []
    seen_topics: Set[str] = set()
    for entry in unverified_entries:
        text = entry.lstrip("- ").strip()
        if not text:
            continue
        topic = _topic_label_from_unverified(text)
        if topic not in seen_topics:
            reason = _reason_for_unverified_topic(text)
            selected.append((topic, reason))
            seen_topics.add(topic)
    for scenario in scenarios:
        topic = scenario.affected_units or scenario.observable_path or scenario.assumption
        topic = topic.strip()
        if topic and topic not in seen_topics:
            selected.append((topic, "Simulation highlighted this area despite missing direct observation."))
            seen_topics.add(topic)
    excluded: List[str] = []
    for entry in not_evaluated_entries:
        text = entry.lstrip("- ").strip()
        if text:
            excluded.append(text)
    priority_statement = (
        "Topics were prioritized where chain reactions or wide impact radius could occur without prior observation."
    )
    if topic_config:
        manual_topics = topic_config.get("manual_topics") or []
        for item in manual_topics:
            label = str(item.get("label", "")).strip()
            reason = str(item.get("reason", "Manually selected topic via configuration.")).strip()
            if label and label not in seen_topics:
                selected.append((label, reason))
                seen_topics.add(label)
        if topic_config.get("priority_statement"):
            priority_statement = str(topic_config["priority_statement"])
    if not selected:
        selected.append(
            ("No specific topics selected", "No unverified or simulated areas were identified in this run.")
        )
    if topic_config and topic_config.get("excluded_topics"):
        excluded = [str(item) for item in topic_config["excluded_topics"]]
    elif not excluded:
        excluded.append("No explicit exclusions noted beyond standard 'Not Evaluated' declarations.")
    return TopicDisclosure(
        selected_topics=selected,
        excluded_topics=excluded,
        priority_statement=priority_statement,
    )


def _topic_label_from_unverified(text: str) -> str:
    if "file:" in text:
        file_hint, _ = _extract_file_and_line(text)
        if file_hint:
            return file_hint
    return text[:80]


def _reason_for_unverified_topic(text: str) -> str:
    lower = text.lower()
    if "exception handler" in lower:
        return "Exception handling path has never been observed."
    if "retry" in lower or "timeout" in lower:
        return "Retry/timeout logic depends on external conditions that were not exercised."
    if "external" in lower:
        return "External dependency could propagate failures without evidence."
    if "unexecuted" in lower:
        return "Code path has zero runtime observations."
    return "Area lacks observation evidence."


def render_topic_disclosure(disclosure: TopicDisclosure) -> str:
    lines = ["Topic Selection Disclosure", ""]
    lines.append("Selected Topics:")
    for topic, reason in disclosure.selected_topics:
        lines.append("<details>")
        lines.append(f"<summary>{topic}</summary>")
        lines.append("")
        lines.append(f"- Rationale: {reason}")
        lines.append("")
        lines.append("</details>")
    lines.append("")
    lines.append("Excluded Topic Types:")
    for item in disclosure.excluded_topics:
        lines.append(f"- {item}")
    lines.append("")
    lines.append(f"Priority Criteria: {disclosure.priority_statement}")
    lines.append("")
    lines.append(
        "Declaration: This report's risks and alternatives are valid only under the selected topics. "
        "Other perspectives may surface different risks and alternatives."
    )
    return "\n".join(lines).rstrip() + "\n"


def load_topic_config(config_path: Path | None) -> dict[str, object] | None:
    if not config_path:
        return None
    if not config_path.exists():
        return None
    try:
        return json.loads(config_path.read_text())
    except (OSError, json.JSONDecodeError):
        return None


def main() -> None:
    args = parse_args()
    diff_paths = parse_diff_file(args.diff) if args.diff else None
    python_files = gather_python_files(args.paths, diff_paths)
    mechanical = run_mechanical_verification(python_files)
    test_summary = load_test_report(args.test_report)
    unverified = analyze_unverified_regions(
        files=python_files,
        observed_paths=test_summary.observed_paths,
        test_noted_unexecuted=test_summary.noted_unexecuted,
        extra=args.extra_unverified,
    )
    not_evaluated = build_not_evaluated_section(args.extra_not_evaluated)
    report = render_report(mechanical, test_summary.lines, unverified, not_evaluated)
    scenarios = generate_simulation_scenarios(unverified, not_evaluated)
    simulation_report = render_simulation_report(scenarios)
    risk_entries = generate_risk_entries(scenarios)
    risk_report = render_risk_report(risk_entries)
    topic_config = load_topic_config(args.topic_config)
    disclosure = build_topic_disclosure(unverified, not_evaluated, scenarios, topic_config)
    disclosure_report = render_topic_disclosure(disclosure)
    bundle = report + "\n" + simulation_report + "\n" + risk_report + "\n" + disclosure_report
    if args.output:
        args.output.write_text(bundle)
    else:
        print(bundle)


if __name__ == "__main__":
    main()
