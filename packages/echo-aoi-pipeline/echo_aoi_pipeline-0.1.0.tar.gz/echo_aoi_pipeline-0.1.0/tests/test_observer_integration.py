"""
Integration Tests for Observer Layer

Tests WebSocket server, event emission, parsing, and end-to-end flows.

Usage:
    pytest tests/test_observer_integration.py -v
"""

import asyncio
import json
import os
import sys
from pathlib import Path

import pytest

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

# Import after path setup
from ops.observer.observer_emitter import observer_emit, create_session_id, load_buffer_events
from ops.observer.observer_parser import ObserverParser, parse_regression_queue


@pytest.fixture
def runtime_dirs():
    """Create runtime directories for testing."""
    runtime_observer = Path("runtime/observer")
    runtime_observer.mkdir(parents=True, exist_ok=True)

    artifacts_self_heal = Path("artifacts/self_heal")
    artifacts_self_heal.mkdir(parents=True, exist_ok=True)

    yield

    # Cleanup is optional for debugging
    # Clean up test files if needed


@pytest.fixture
def buffer_file():
    """Get buffer file path."""
    return Path("runtime/observer/event_buffer.jsonl")


class TestObserverEmitter:
    """Test observer event emission."""

    def test_observer_emit_basic(self, runtime_dirs, buffer_file):
        """Test basic event emission."""
        session_id = create_session_id("test")

        event_id = observer_emit(
            session_id=session_id,
            event_type="test.event",
            actor="TestActor",
            step="test_step",
            payload={"test": "data"},
            severity="info",
        )

        assert event_id is not None
        assert len(event_id) > 0

        # Verify event written to buffer
        assert buffer_file.exists()

        events = load_buffer_events(limit=10)
        assert len(events) > 0

        # Find our event
        test_event = next((e for e in events if e.get("event_id") == event_id), None)
        assert test_event is not None
        assert test_event["event_type"] == "test.event"
        assert test_event["actor"] == "TestActor"
        assert test_event["step"] == "test_step"
        assert test_event["payload"]["test"] == "data"

    def test_observer_emit_with_all_fields(self, runtime_dirs):
        """Test event emission with all optional fields."""
        session_id = create_session_id("test_full")

        event_id = observer_emit(
            session_id=session_id,
            event_type="test.full_event",
            actor="TestActor",
            step="full_step",
            payload={"key": "value"},
            diff="/path/to/diff.txt",
            capsule_meta={"scenario": "test", "url": "https://example.com"},
            router={"selected": "test_router"},
            tool_call={"tool": "test_tool", "args": {}},
            reasoning_hint="Test reasoning",
            parent_event_id="parent-123",
            severity="warning",
            tags=["test", "integration"],
        )

        assert event_id is not None

        events = load_buffer_events(limit=10)
        test_event = next((e for e in events if e.get("event_id") == event_id), None)

        assert test_event is not None
        assert test_event["diff"] == "/path/to/diff.txt"
        assert test_event["capsule_meta"]["scenario"] == "test"
        assert test_event["router"]["selected"] == "test_router"
        assert test_event["tool_call"]["tool"] == "test_tool"
        assert test_event["reasoning_hint"] == "Test reasoning"
        assert test_event["parent_event_id"] == "parent-123"
        assert test_event["severity"] == "warning"
        assert "test" in test_event["tags"]

    def test_create_session_id(self):
        """Test session ID generation."""
        session1 = create_session_id("test")
        session2 = create_session_id("test")

        # Should include timestamp, so should be different
        assert session1 != session2
        assert "test" in session1


class TestObserverParser:
    """Test observer event parsing."""

    def test_parse_jsonl_files(self, runtime_dirs):
        """Test parsing JSONL log files."""
        # Create test JSONL file
        test_log = Path("runtime/observer/test_events.jsonl")

        events = [
            {"event_type": "test.event1", "actor": "Actor1", "timestamp": "2025-01-01T00:00:00Z"},
            {"event_type": "test.event2", "actor": "Actor2", "timestamp": "2025-01-01T00:01:00Z"},
        ]

        with test_log.open("w") as f:
            for event in events:
                f.write(json.dumps(event) + "\n")

        parser = ObserverParser()
        parsed = parser.parse_jsonl_files()

        assert len(parsed) >= 2  # At least our test events

        # Cleanup
        test_log.unlink()

    def test_parse_regression_queue(self, runtime_dirs):
        """Test parsing regression queue."""
        queue_file = Path("runtime/self_heal_regression_queue.jsonl")

        queue_items = [
            {
                "scenario": "test_scenario",
                "step": "test_step",
                "diff_path": "/path/to/diff.txt",
                "timestamp": "2025-01-01T00:00:00Z",
            }
        ]

        with queue_file.open("w") as f:
            for item in queue_items:
                f.write(json.dumps(item) + "\n")

        events = parse_regression_queue()

        assert len(events) >= 1

        test_event = next(
            (e for e in events if e.get("payload", {}).get("scenario") == "test_scenario"),
            None
        )

        assert test_event is not None
        assert test_event["event_type"] == "regression.queued"

        # Cleanup
        queue_file.unlink()


@pytest.mark.asyncio
class TestWebSocketIntegration:
    """Test WebSocket server integration."""

    async def test_websocket_connection(self):
        """Test basic WebSocket connection (requires running server)."""
        # This test would require starting the server
        # For now, we'll skip if server is not running
        pytest.skip("Requires running WebSocket server")

    async def test_event_broadcast(self):
        """Test event broadcasting to clients (requires running server)."""
        pytest.skip("Requires running WebSocket server")


class TestEndToEnd:
    """End-to-end integration tests."""

    def test_emit_and_load_workflow(self, runtime_dirs):
        """Test complete emit → buffer → load workflow."""
        session_id = create_session_id("e2e_test")

        # Emit events
        event_ids = []
        for i in range(5):
            event_id = observer_emit(
                session_id=session_id,
                event_type=f"test.e2e_event_{i}",
                actor="E2EActor",
                step=f"step_{i}",
                payload={"index": i},
                severity="info",
            )
            event_ids.append(event_id)

        # Load events
        loaded_events = load_buffer_events(limit=100)

        # Verify all events present
        for event_id in event_ids:
            found = any(e.get("event_id") == event_id for e in loaded_events)
            assert found, f"Event {event_id} not found in loaded events"

    def test_parser_aggregation(self, runtime_dirs):
        """Test parser aggregates all event sources."""
        parser = ObserverParser()

        # Parse all sources
        all_events = parser.parse_all()

        # Should return list
        assert isinstance(all_events, list)

        # Events should have required fields
        for event in all_events:
            assert "event_type" in event or "actor" in event


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])
