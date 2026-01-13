"""
Discord Audit Mirror — Outbound-Only External Surface

Purpose: POST judgment events to Discord webhook for external visibility

Direction: Outbound-only (NO inbound path, NO commands, NO interaction)

Philosophy: Discord observes, never controls
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any
import requests
from datetime import datetime

# Discord webhook URL (read-only notification channel)
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1452079171617423436/zfNkH0VAyJz4pUpoDPKIV_CNFXMbuzm1jYfwAsNOapaXDIARL7H9OiWMoQe0D76lyC9-"

# Add project root to path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def format_discord_embed(event_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format ledger event as Discord embed

    10-second readability standard:
    - Decision status immediately visible
    - "NO JUDGMENT" explicitly stated
    - Color coding for quick status recognition

    Args:
        event_data: Ledger entry (from ledger.jsonl)

    Returns:
        Discord embed payload
    """
    event_type = event_data.get("action", "UNKNOWN")
    event_id = event_data.get("event_id", "unknown")
    flow_id = event_data.get("flow_id", "unknown")
    actor = event_data.get("actor") or "system"
    timestamp = event_data.get("timestamp", datetime.now().isoformat())

    # Decision status determination (for description)
    decision_status_map = {
        "HANDOFF_CREATED": "⏸️ STOP — Awaiting Human Decision",
        "RESUME_ALLOWED": "✅ APPROVED — Human Authorized",
        "RESUME_DENIED": "❌ DENIED — Human Blocked"
    }
    decision_status = decision_status_map.get(event_type, "ℹ️ OBSERVATION")

    # Decision status (machine-readable field)
    decision_status_field = {
        "HANDOFF_CREATED": "NO_JUDGMENT",
        "RESUME_ALLOWED": "APPROVED",
        "RESUME_DENIED": "DENIED"
    }
    status_value = decision_status_field.get(event_type, "OBSERVATION")

    # Color coding based on event type
    color_map = {
        "HANDOFF_CREATED": 0xFFA500,  # Orange (awaiting human)
        "RESUME_ALLOWED": 0x00FF00,   # Green (approved)
        "RESUME_DENIED": 0xFF0000     # Red (denied)
    }
    color = color_map.get(event_type, 0x808080)  # Gray default

    # Human-readable timestamp (ISO + relative)
    from datetime import datetime as dt
    try:
        ts = dt.fromisoformat(timestamp.replace('Z', '+00:00'))
        timestamp_readable = f"{ts.strftime('%Y-%m-%d %H:%M:%S UTC')}"
    except:
        timestamp_readable = timestamp

    embed = {
        "title": f"{event_type}",
        "description": f"**{decision_status}**\n\n"
                      f"Event ID: `{event_id}`\n\n"
                      f"⚠️ **This event contains NO automated decision.**",
        "color": color,
        "fields": [
            {
                "name": "결정 상태 (Decision Status)",
                "value": f"**{status_value}**",
                "inline": False
            },
            {
                "name": "판단 권한 (Judgment Authority)",
                "value": "🧑 **HUMAN**",
                "inline": True
            },
            {
                "name": "시스템 상태 (System State)",
                "value": "**UNCHANGED**" if event_type == "HANDOFF_CREATED" else "**EXECUTED**",
                "inline": True
            },
            {
                "name": "출처 (Source)",
                "value": flow_id,
                "inline": True
            },
            {
                "name": "행위자 (Actor)",
                "value": actor if actor != "system" else "system (no judgment)",
                "inline": True
            },
            {
                "name": "Timestamp",
                "value": timestamp_readable,
                "inline": False
            }
        ],
        "footer": {
            "text": "Echo Judgment System — Audit Trail (Read-Only)"
        }
    }

    # Add audit API link
    audit_url = f"https://audit-api.example.com/audit/events/{event_id}"
    embed["fields"].append({
        "name": "검증 경로 (Verification)",
        "value": f"[Audit API]({audit_url})",
        "inline": False
    })

    return embed


def post_to_discord(event_data: Dict[str, Any], dry_run: bool = False) -> bool:
    """
    POST event notification to Discord webhook

    Args:
        event_data: Ledger entry
        dry_run: If True, print payload without sending

    Returns:
        True if successful (or dry_run), False otherwise
    """
    embed = format_discord_embed(event_data)

    payload = {
        "username": "Echo Audit System",
        "avatar_url": "https://example.com/echo-logo.png",  # Optional
        "embeds": [embed]
    }

    if dry_run:
        print("[Dry Run] Would POST to Discord:")
        print(json.dumps(payload, indent=2))
        return True

    try:
        response = requests.post(
            DISCORD_WEBHOOK_URL,
            json=payload,
            timeout=5
        )
        response.raise_for_status()
        print(f"[Discord] Event posted: {event_data['event_id']}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"[Discord] POST failed: {e}")
        return False


def mirror_ledger_event(event_id: str, dry_run: bool = False) -> bool:
    """
    Mirror a specific ledger event to Discord

    Args:
        event_id: Event to mirror
        dry_run: If True, simulate without actual POST

    Returns:
        True if successful
    """
    # Load ledger
    ledger_path = ROOT / "echo_engine" / "ledger.jsonl"

    if not ledger_path.exists():
        print(f"[Error] Ledger not found: {ledger_path}")
        return False

    # Find event
    with open(ledger_path, encoding="utf-8") as f:
        for line in f:
            entry = json.loads(line)
            if entry.get("event_id") == event_id:
                return post_to_discord(entry, dry_run=dry_run)

    print(f"[Error] Event not found: {event_id}")
    return False


def main():
    """
    CLI for Discord audit mirror

    Usage:
        python discord_audit_mirror.py --event-id <id>
        python discord_audit_mirror.py --event-id <id> --dry-run
    """
    import argparse

    parser = argparse.ArgumentParser(description="Mirror judgment events to Discord")
    parser.add_argument("--event-id", required=True, help="Event ID to mirror")
    parser.add_argument("--dry-run", action="store_true", help="Print payload without sending")

    args = parser.parse_args()

    print("="*60)
    print("Discord Audit Mirror — Outbound-Only Surface")
    print("="*60)
    print()

    success = mirror_ledger_event(args.event_id, dry_run=args.dry_run)

    print()
    if success:
        print("✅ Event mirrored successfully")
    else:
        print("❌ Event mirror failed")
    print()

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
