#!/usr/bin/env python3
"""
Router-Lite Engine for Phase 28.

Features:
- Asyncio queue based dispatch
- Round-robin node selection loaded from config/router_nodes.yaml
- Automatic retries with backoff
- Transmission logging to proof/router_transmission_log.yaml
"""

from __future__ import annotations

import argparse
import asyncio
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
import math
import random
import uuid

import yaml

CONFIG_PATH = Path("config/router_nodes.yaml")
LOG_PATH = Path("proof/router_transmission_log.yaml")


@dataclass
class RouterNode:
    name: str
    endpoint: str
    latency_ms: int = 40
    failure_rate: float = 0.0

    @classmethod
    def from_mapping(cls, data: Dict[str, Any]) -> "RouterNode":
        try:
            name = data["name"]
            endpoint = data["endpoint"]
        except KeyError as exc:  # pragma: no cover - defensive
            raise ValueError(f"router node missing field: {exc}") from exc
        latency = int(data.get("latency_ms", 40))
        failure_rate = float(data.get("failure_rate", 0.0))
        failure_rate = max(0.0, min(1.0, failure_rate))
        return cls(name=name, endpoint=endpoint, latency_ms=latency, failure_rate=failure_rate)


def load_nodes(config_path: Path) -> List[RouterNode]:
    if not config_path.exists():
        raise FileNotFoundError(f"router config not found: {config_path}")
    raw = yaml.safe_load(config_path.read_text()) or {}
    nodes = raw.get("nodes") if isinstance(raw, dict) else None
    if not nodes or not isinstance(nodes, list):
        raise ValueError(f"router config {config_path} missing 'nodes' list")
    return [RouterNode.from_mapping(item) for item in nodes]


class RouterLiteEngine:
    def __init__(
        self,
        nodes: List[RouterNode],
        log_path: Path,
        retry_limit: int = 3,
        retry_interval: float = 1.0,
        worker_count: int = 1,
        seed: Optional[int] = None,
    ) -> None:
        if not nodes:
            raise ValueError("RouterLiteEngine requires at least one node")
        self.nodes = nodes
        self.log_path = log_path
        self.retry_limit = max(1, retry_limit)
        self.retry_interval = max(0.1, retry_interval)
        self.worker_count = max(1, worker_count)
        self.queue: asyncio.Queue[Dict[str, Any]] = asyncio.Queue()
        self._next_index = 0
        self._log_lock = asyncio.Lock()
        self._random = random.Random(seed)

    def _next_node(self) -> RouterNode:
        node = self.nodes[self._next_index]
        self._next_index = (self._next_index + 1) % len(self.nodes)
        return node

    async def enqueue_message(self, payload: Dict[str, Any]) -> str:
        """Place a message onto the routing queue."""
        if "id" not in payload:
            payload = {**payload, "id": uuid.uuid4().hex}
        await self.queue.put(payload)
        return payload["id"]

    async def drain(self) -> None:
        """Process queued messages with the configured worker count."""
        workers = [asyncio.create_task(self._worker(i)) for i in range(self.worker_count)]
        await self.queue.join()
        for worker in workers:
            worker.cancel()
        await asyncio.gather(*workers, return_exceptions=True)

    async def _worker(self, worker_id: int) -> None:
        while True:
            message = await self.queue.get()
            try:
                await self._dispatch(message, worker_id)
            finally:
                self.queue.task_done()

    async def _dispatch(self, message: Dict[str, Any], worker_id: int) -> None:
        attempt = 0
        while attempt < self.retry_limit:
            attempt += 1
            node = self._next_node()
            try:
                latency_ms = await self._simulate_send(node, message)
                await self._log_result(
                    message_id=message["id"],
                    node=node,
                    status="success",
                    latency_ms=latency_ms,
                    attempts=attempt,
                    worker_id=worker_id,
                )
                return
            except Exception as exc:  # pragma: no cover - safety
                if attempt >= self.retry_limit:
                    await self._log_result(
                        message_id=message["id"],
                        node=node,
                        status="failed",
                        latency_ms=None,
                        attempts=attempt,
                        worker_id=worker_id,
                        error=str(exc),
                    )
                    return
                await asyncio.sleep(self.retry_interval)

    async def _simulate_send(self, node: RouterNode, message: Dict[str, Any]) -> int:
        """Simulate a network hop with latency and optional failure."""
        base_latency = max(5, node.latency_ms)
        jitter = self._random.uniform(-0.1, 0.1) * base_latency
        latency_ms = int(max(5, base_latency + jitter))
        await asyncio.sleep(latency_ms / 1000.0)
        failure_chance = node.failure_rate
        if self._random.random() < failure_chance:
            raise RuntimeError(f"node {node.name} rejected message")
        return latency_ms

    async def _log_result(
        self,
        *,
        message_id: str,
        node: RouterNode,
        status: str,
        latency_ms: Optional[int],
        attempts: int,
        worker_id: int,
        error: Optional[str] = None,
    ) -> None:
        entry = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "message_id": message_id,
            "node": node.name,
            "endpoint": node.endpoint,
            "status": status,
            "latency_ms": latency_ms,
            "attempts": attempts,
            "worker_id": worker_id,
        }
        if error:
            entry["error"] = error

        async with self._log_lock:
            log_entries: List[Dict[str, Any]] = []
            if self.log_path.exists():
                data = yaml.safe_load(self.log_path.read_text()) or []
                if isinstance(data, dict):
                    data = [data]
                log_entries = data
            log_entries.append(entry)
            self.log_path.parent.mkdir(parents=True, exist_ok=True)
            self.log_path.write_text(yaml.safe_dump(log_entries, sort_keys=False))


async def _run_test(args: argparse.Namespace) -> None:
    nodes = load_nodes(Path(args.config))
    engine = RouterLiteEngine(
        nodes=nodes,
        log_path=Path(args.log_path),
        retry_limit=args.retry_limit,
        retry_interval=args.retry_interval,
        worker_count=args.workers,
        seed=args.seed,
    )

    for idx in range(args.messages):
        payload = {
            "id": f"test-{idx+1}",
            "payload": {
                "kind": "diagnostic",
                "sequence": idx + 1,
            },
        }
        await engine.enqueue_message(payload)

    await engine.drain()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Phase 28 Router-Lite engine")
    parser.add_argument("--config", default=CONFIG_PATH, help="Router nodes config path")
    parser.add_argument(
        "--log-path",
        default=LOG_PATH,
        help="Transmission log path (YAML)",
    )
    parser.add_argument("--retry-limit", type=int, default=3, help="Max retries per message")
    parser.add_argument(
        "--retry-interval",
        type=float,
        default=1.0,
        help="Seconds to wait between retries",
    )
    parser.add_argument("--workers", type=int, default=1, help="Number of async workers")
    parser.add_argument("--seed", type=int, default=27, help="Deterministic seed")
    parser.add_argument("--messages", type=int, default=25, help="Message count for --test runs")
    parser.add_argument(
        "--test",
        action="store_true",
        help="Run a built-in diagnostic loop using synthetic messages",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    if not args.test:
        parser.error("This module currently supports --test mode for manual execution.")
    asyncio.run(_run_test(args))


if __name__ == "__main__":
    main()
