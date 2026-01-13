from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import JSONResponse

from echo_engine.audit_snapshot import (
    LEDGER_PATH,
    build_snapshot,
    snapshot_hash,
)

API_CACHE_TTL = 30.0  # seconds
RATE_LIMIT_WINDOW = 60.0  # seconds
RATE_LIMIT_COUNT = 60

_cache: Dict[str, Dict[str, Any]] = {}
_rate_log: Dict[str, Dict[str, Any]] = {}

ACCESS_LOG_DIR = Path("artifacts/structure003_phase4")
ACCESS_LOG_DIR.mkdir(parents=True, exist_ok=True)
ACCESS_LOG_PATH = ACCESS_LOG_DIR / "api_access.jsonl"

app = FastAPI(title="Structure #003 Audit API", version="1.0")


def _log_access(entry: Dict[str, Any]) -> None:
    entry.setdefault("timestamp", time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    with ACCESS_LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def _check_rate_limit(client_ip: str) -> None:
    now = time.time()
    state = _rate_log.get(client_ip, {"start": now, "count": 0})
    if now - state["start"] >= RATE_LIMIT_WINDOW:
        state = {"start": now, "count": 0}
    state["count"] += 1
    _rate_log[client_ip] = state
    if state["count"] > RATE_LIMIT_COUNT:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")


def _get_snapshot(event_id: str) -> Dict[str, Any]:
    cached = _cache.get(event_id)
    now = time.time()
    if cached and now - cached["ts"] <= API_CACHE_TTL:
        cached["cache_hit"] = True
        return cached
    snapshot = build_snapshot(event_id)
    hash_value = snapshot_hash(snapshot)
    cached = {"snapshot": snapshot, "hash": hash_value, "ts": now, "cache_hit": False}
    _cache[event_id] = cached
    return cached


@app.get("/audit/health")
def audit_health() -> Dict[str, Any]:
    try:
        exists = LEDGER_PATH.exists()
        if not exists:
            raise FileNotFoundError(str(LEDGER_PATH))
        LEDGER_PATH.open("r", encoding="utf-8").close()
        return {"status": "ok", "ledger_path": str(LEDGER_PATH)}
    except Exception as exc:
        _log_access({"endpoint": "/audit/health", "status": 503, "error": str(exc)})
        raise HTTPException(status_code=503, detail="Ledger unavailable")


@app.get("/audit/events/{event_id}")
async def get_audit_event(event_id: str, request: Request) -> Response:
    client_ip = request.client.host if request.client else "unknown"
    try:
        _check_rate_limit(client_ip)
        cached = _get_snapshot(event_id)
    except HTTPException as exc:
        _log_access(
            {
                "endpoint": f"/audit/events/{event_id}",
                "status": exc.status_code,
                "event_id": event_id,
                "client_ip": client_ip,
                "cache_hit": False,
            }
        )
        raise
    except ValueError:
        _log_access(
            {
                "endpoint": f"/audit/events/{event_id}",
                "status": 404,
                "event_id": event_id,
                "client_ip": client_ip,
                "cache_hit": False,
            }
        )
        raise HTTPException(status_code=404, detail="Event not found")
    except Exception as exc:
        _log_access(
            {
                "endpoint": f"/audit/events/{event_id}",
                "status": 503,
                "event_id": event_id,
                "client_ip": client_ip,
                "cache_hit": False,
                "error": str(exc),
            }
        )
        raise HTTPException(status_code=503, detail="Ledger unavailable")

    snapshot = cached["snapshot"]
    payload = {"hash": cached["hash"], "snapshot": snapshot}
    _log_access(
        {
            "endpoint": f"/audit/events/{event_id}",
            "status": 200,
            "event_id": event_id,
            "client_ip": client_ip,
            "cache_hit": cached["cache_hit"],
        }
    )
    return JSONResponse(payload)
