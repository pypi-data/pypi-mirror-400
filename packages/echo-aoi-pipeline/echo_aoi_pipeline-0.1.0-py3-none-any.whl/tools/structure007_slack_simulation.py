"""
Structure #007 — Slack Surface Simulation

Purpose: Demonstrate surface-agnostic judgment traceability

Philosophy: Same enforcement logic, different insertion point
"""

import sys
import json
import uuid
from pathlib import Path
from datetime import datetime, timezone

# Add project root to path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Ledger path (same as audit_snapshot.py)
LEDGER_PATH = ROOT / "echo_engine" / "ledger.jsonl"


def listen_outbound(flow_id: str, action: str, payload: dict) -> str:
    """
    Structure #001: Listen to outbound action

    This is a minimal implementation for demonstration.
    In production, this would import from echo_engine.

    Args:
        flow_id: Surface identifier (mail, slack, etc.)
        action: Action type (send_message, etc.)
        payload: Action metadata

    Returns:
        event_id
    """
    event_id = f"{flow_id}-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:4]}"

    # Write to ledger (Structure #002 - Handoff)
    entry = {
        "structure": "002",
        "action": "HANDOFF_CREATED",
        "event_id": event_id,
        "flow_id": flow_id,
        "actor": None,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "ref": f"{action}::{payload.get('channel', 'unknown')}"
    }

    # Append to ledger
    LEDGER_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(LEDGER_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")

    print(f"[Structure #001] Outbound detected: {flow_id}/{action}")
    print(f"[Structure #002] Handoff created: {event_id}")

    return event_id


def send_slack_message(channel: str, message: str, user: str = "bot") -> dict:
    """
    Simulated Slack message sender (no actual API calls)

    Args:
        channel: Slack channel ID or name
        message: Message text
        user: Sender username

    Returns:
        Simulated API response
    """
    # This is where Structure #001 insertion happens
    # BEFORE actual message send (which is simulated here)

    event_id = listen_outbound(
        flow_id="slack",
        action="send_message",
        payload={
            "channel": channel,
            "message": message[:100],  # Truncate for logging
            "user": user
        }
    )

    # Simulated Slack API call (no actual network)
    # In real implementation, this would be:
    # client.chat_postMessage(channel=channel, text=message)

    print(f"[Slack Simulation] Message sent to #{channel}")
    print(f"[Slack Simulation] Event ID: {event_id}")
    print(f"[Slack Simulation] Message: {message[:80]}...")

    return {
        "ok": True,
        "channel": channel,
        "ts": "1234567890.123456",
        "event_id": event_id  # Traceability link
    }


def conditional_slack_notification(alert_level: str, incident_id: str) -> dict:
    """
    Send conditional Slack notification with wobble message

    This demonstrates the same pattern as mail:
    - Conditional logic (alert_level check)
    - Outbound action (Slack message)
    - Judgment hook insertion (Structure #001)

    Args:
        alert_level: Alert severity (high, medium, low)
        incident_id: Incident identifier

    Returns:
        Slack API response (simulated)
    """
    # Conditional logic (wobble point)
    if alert_level != "high":
        print(f"[Conditional] Alert level {alert_level} - no notification sent")
        return {"ok": False, "reason": "below_threshold"}

    # Compose message
    message = f"""
🚨 **High Priority Alert**

Incident: {incident_id}
Level: {alert_level.upper()}
Action: Immediate review required

Please acknowledge this alert in the incident response channel.
    """.strip()

    # Outbound action with Structure #001 hook
    response = send_slack_message(
        channel="incident-alerts",
        message=message,
        user="alert-bot"
    )

    return response


def main():
    """
    Demonstration: Conditional Slack notification with judgment hook
    """
    print("="*60)
    print("Structure #007 — Slack Surface Simulation")
    print("="*60)
    print()

    print("[Demo] Scenario: High-priority incident alert")
    print()

    # Execute conditional notification
    result = conditional_slack_notification(
        alert_level="high",
        incident_id="INC-2025-001"
    )

    print()
    print("="*60)
    print("Result:")
    print(f"  OK: {result.get('ok')}")
    print(f"  Channel: {result.get('channel')}")
    print(f"  Event ID: {result.get('event_id')}")
    print("="*60)
    print()
    print("[Proof] Check ledger.jsonl for:")
    print("  - flow_id: slack")
    print("  - action: send_message")
    print("  - event_id: (generated)")
    print()
    print("[Next] Query audit API:")
    print(f"  GET /audit/events/{result.get('event_id')}")
    print()


if __name__ == "__main__":
    main()
