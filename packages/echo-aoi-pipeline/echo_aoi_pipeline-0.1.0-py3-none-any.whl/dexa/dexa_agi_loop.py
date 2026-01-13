"""
Dexa AGI loop coordinator.

Ensures every Excel action runs through the Existential Reasoning Proxy:
1) Capture UI + structural state via Playwright.
2) Publish the snapshot to the proxy for Echo.
3) Wait for Echo's echo_command.
4) Execute the command verbatim and log the outcome.
"""

from __future__ import annotations

import json
import logging
import time
from typing import Any, Dict, List, Optional

from dexa.dexa_mcp_bridge import DexaMCPBridge
from dexa.existential_reasoning_proxy import (
    ProxyState,
    acknowledge_command,
    read_proxy,
    record_execution,
    write_proxy,
)

logger = logging.getLogger(__name__)


class EchoCommandTimeoutError(RuntimeError):
    """Raised when Echo does not issue a command before timeout."""


class DexaAGILoop:
    """High-level orchestrator for Dexa's Excel AGI flow."""

    def __init__(
        self,
        bridge: Optional[DexaMCPBridge] = None,
        poll_interval: float = 2.0,
        wait_timeout: float = 90.0,
    ) -> None:
        self.bridge = bridge or DexaMCPBridge()
        self.poll_interval = poll_interval
        self.wait_timeout = wait_timeout
        self._last_command_signature: Optional[str] = None

    def synchronize_state(
        self,
        chat_history: Optional[List[Dict[str, str]]] = None,
        triggers: Optional[List[str]] = None,
        user_intent_overrides: Optional[Dict[str, Any]] = None,
    ) -> ProxyState:
        """
        Capture Playwright state and publish it to the existential proxy.
        """
        payload = self.bridge.snapshot_for_proxy(chat_history=chat_history)
        if user_intent_overrides:
            payload["user_intent_overrides"] = user_intent_overrides
        state = write_proxy(payload, triggers=triggers)
        logger.debug(
            "Proxy synchronized (%s rows, triggers=%s)",
            state.ui_state.get("row_count"),
            triggers,
        )
        return state

    def await_echo_command(self, timeout: Optional[float] = None) -> Optional[Dict[str, Any]]:
        """
        Poll the proxy until Echo populates echo_command.
        """
        deadline = time.time() + (timeout or self.wait_timeout)
        while time.time() < deadline:
            state = read_proxy()
            if not state or not state.echo_command:
                time.sleep(self.poll_interval)
                continue
            signature = json.dumps(state.echo_command, sort_keys=True)
            if signature == self._last_command_signature:
                time.sleep(self.poll_interval)
                continue
            self._last_command_signature = signature
            return state.echo_command
        return None

    def execute_cycle(
        self,
        chat_history: Optional[List[Dict[str, str]]] = None,
        triggers: Optional[List[str]] = None,
        user_intent_overrides: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Full Dexa→Proxy→Echo→Dexa execution.
        """
        self.synchronize_state(
            chat_history=chat_history,
            triggers=triggers,
            user_intent_overrides=user_intent_overrides,
        )
        echo_command = self.await_echo_command(timeout=timeout)
        if not echo_command:
            raise EchoCommandTimeoutError("Echo did not issue echo_command in time")

        result = self.bridge.execute_echo_command(echo_command)
        record_execution(
            action=echo_command.get("action") or echo_command.get("name") or "echo_command",
            status=result.get("status", "unknown"),
            detail=json.dumps(result, ensure_ascii=False),
            metadata={"command": echo_command},
            echo_command_id=echo_command.get("command_id"),
        )
        acknowledge_command(echo_command)
        logger.info("Echo command executed: %s → %s", echo_command.get("action"), result["status"])
        return result


__all__ = ["DexaAGILoop", "EchoCommandTimeoutError"]
