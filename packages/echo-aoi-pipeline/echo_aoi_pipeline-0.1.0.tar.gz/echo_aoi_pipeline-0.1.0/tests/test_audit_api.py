import json
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from echo_engine import audit_api
from echo_engine import audit_snapshot


@pytest.fixture
def reset_state(tmp_path, monkeypatch):
    ledger = tmp_path / "ledger.jsonl"
    monkeypatch.setattr(audit_snapshot, "LEDGER_PATH", ledger)
    monkeypatch.setattr(audit_api, "LEDGER_PATH", ledger)
    audit_api._cache.clear()
    audit_api._rate_log.clear()
    return ledger


def _write_entries(ledger: Path, event_id: str = "phase0-test-conditional-001"):
    entries = [
        {
            "structure": "002",
            "action": "HANDOFF_CREATED",
            "event_id": event_id,
            "flow_id": "mail",
            "actor": None,
            "timestamp": "2025-12-20T10:00:00Z",
            "ref": "packet.json",
        },
        {
            "structure": "003",
            "action": "RESUME_ALLOWED",
            "event_id": event_id,
            "flow_id": "mail",
            "actor": "tester",
            "timestamp": "2025-12-20T10:00:01Z",
            "ref": "trace-id",
        },
    ]
    with ledger.open("w", encoding="utf-8") as f:
        for entry in entries:
            f.write(json.dumps(entry) + "\n")


def test_get_event_ok(reset_state):
    ledger = reset_state
    _write_entries(ledger)
    client = TestClient(audit_api.app)

    resp = client.get("/audit/events/phase0-test-conditional-001")
    assert resp.status_code == 200
    payload = resp.json()
    assert payload["snapshot"]["event_id"] == "phase0-test-conditional-001"
    assert payload["hash"]


def test_get_event_not_found(reset_state):
    ledger = reset_state
    _write_entries(ledger, event_id="other-event")
    client = TestClient(audit_api.app)

    resp = client.get("/audit/events/phase0-test-conditional-001")
    assert resp.status_code == 404


def test_get_event_ledger_missing(monkeypatch):
    monkeypatch.setattr(audit_snapshot, "LEDGER_PATH", Path("missing-ledger.jsonl"))
    monkeypatch.setattr(audit_api, "LEDGER_PATH", Path("missing-ledger.jsonl"))
    audit_api._cache.clear()
    audit_api._rate_log.clear()
    client = TestClient(audit_api.app)

    resp = client.get("/audit/events/phase0-test-conditional-001")
    assert resp.status_code == 503


def test_rate_limit(reset_state):
    ledger = reset_state
    _write_entries(ledger)
    client = TestClient(audit_api.app)

    for _ in range(audit_api.RATE_LIMIT_COUNT):
        assert client.get("/audit/events/phase0-test-conditional-001").status_code == 200

    resp = client.get("/audit/events/phase0-test-conditional-001")
    assert resp.status_code == 429
