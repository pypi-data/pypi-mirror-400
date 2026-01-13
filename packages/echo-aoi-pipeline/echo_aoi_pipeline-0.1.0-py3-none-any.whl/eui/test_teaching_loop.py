from __future__ import annotations

import json
from pathlib import Path

from eui.backend.teaching.analyzer import TeachingAnalyzer
from eui.backend.teaching.feedback_engine import FeedbackEngine, SNAPSHOT_DIR
from eui.backend.session_memory import SessionMemoryManager, SessionMemoryConfig


def _write_trace(path: Path, records: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record) + "\n")


def test_analyze_recent_turns(tmp_path: Path) -> None:
    trace = tmp_path / "trace.jsonl"
    records = [
        {
            "trace_id": "t1",
            "signature": "Aurora",
            "cognitive_pattern": "empathic",
            "influence": {"influence_score": 0.8},
            "drift_self_align": {"level": 0},
            "cognitive_drift": False,
        },
        {
            "trace_id": "t2",
            "signature": "Selene",
            "cognitive_pattern": "reflective",
            "influence": {"influence_score": 0.4},
            "drift_self_align": {"level": 1},
            "cognitive_drift": True,
        },
    ]
    _write_trace(trace, records)
    analyzer = TeachingAnalyzer(trace_path=trace)
    turns = analyzer.recent_turns(limit=2)
    assert len(turns) == 2
    assert turns[0]["trace_id"] == "t1"
    summary = analyzer.summary(limit=2)
    assert summary["pattern_counts"]["empathic"] == 1
    assert summary["cognitive_drift_rate"] == 0.5


def test_generate_feedback_template(tmp_path: Path) -> None:
    trace = tmp_path / "trace.jsonl"
    feedback = tmp_path / "feedback.yaml"
    records = [
        {
            "trace_id": "trace-001",
            "observation": {"intent": "self_blame"},
        }
    ]
    _write_trace(trace, records)
    engine = FeedbackEngine(trace_path=trace, feedback_path=feedback, session_memory=None)
    entries = engine.seed_templates(trace_id="trace-001")
    assert entries
    data = feedback.read_text(encoding="utf-8")
    assert "trace-001" in data


def test_apply_feedback(tmp_path: Path, monkeypatch) -> None:
    trace = tmp_path / "trace.jsonl"
    feedback = tmp_path / "feedback.yaml"
    config = tmp_path / "config.yaml"
    _write_trace(trace, [])
    feedback.write_text(
        "feedback:\n"
        "- id: fb_0001\n"
        "  trace_id: trace-001\n"
        "  user_label:\n"
        "    cognitive_pattern: empathic\n",
        encoding="utf-8",
    )
    config.write_text(
        "tone_curve:\n  self_blame_warmth_bonus: 0.2\n"
        "influence:\n  self_blame_bias: 0.1\n",
        encoding="utf-8",
    )
    session_cfg_path = tmp_path / "session_config.yaml"
    session_cfg_path.write_text(
        "storage:\n"
        "  path: \""
        + str(tmp_path / "memory.db").replace("\\", "\\\\")
        + "\"\n"
        "  backup:\n"
        "    enabled: false\n",
        encoding="utf-8",
    )
    manager = SessionMemoryManager(SessionMemoryConfig(session_cfg_path))
    monkeypatch.setattr("eui.backend.teaching.feedback_engine.SNAPSHOT_DIR", tmp_path / "snapshots")

    engine = FeedbackEngine(
        trace_path=trace,
        feedback_path=feedback,
        config_path=config,
        session_memory=manager,
    )
    result = engine.apply_feedback(dry_run=False)
    assert result["applied"] is True
    new_config = config.read_text(encoding="utf-8")
    assert "self_blame_warmth_bonus: 0.22" in new_config


def test_auto_tuning_pipeline(tmp_path: Path, monkeypatch) -> None:
    trace = tmp_path / "trace.jsonl"
    feedback = tmp_path / "feedback.yaml"
    config = tmp_path / "config.yaml"
    _write_trace(
        trace,
        [
            {
                "trace_id": "trace-1",
                "signature": "Aurora",
                "cognitive_pattern": "responsible",
                "influence": {"influence_score": 0.9},
                "drift_self_align": {"level": 0},
            }
        ],
    )
    feedback.write_text(
        "feedback:\n- id: fb_0001\n  trace_id: trace-1\n  user_label:\n    tone: 조"
        "금 덜 부드럽게, 더 명료하게\n",
        encoding="utf-8",
    )
    config.write_text("tone_curve:\n  clarity_to_directness: 0.3\n", encoding="utf-8")
    session_cfg_path = tmp_path / "session_config2.yaml"
    session_cfg_path.write_text(
        "storage:\n"
        "  path: \""
        + str(tmp_path / "memory2.db").replace("\\", "\\\\")
        + "\"\n"
        "  backup:\n"
        "    enabled: false\n",
        encoding="utf-8",
    )
    manager = SessionMemoryManager(SessionMemoryConfig(session_cfg_path))
    monkeypatch.setattr("eui.backend.teaching.feedback_engine.SNAPSHOT_DIR", tmp_path / "snapshots2")
    engine = FeedbackEngine(
        trace_path=trace,
        feedback_path=feedback,
        config_path=config,
        session_memory=manager,
    )
    result = engine.apply_feedback(dry_run=False)
    assert result["applied"] is True
