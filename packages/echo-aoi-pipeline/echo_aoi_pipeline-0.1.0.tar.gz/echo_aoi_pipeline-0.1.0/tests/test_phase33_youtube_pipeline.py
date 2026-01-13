"""
Phase 33 Extended: YouTube Demo Pipeline Tests

Tests for demo script loading, subtitle generation, and pipeline status.
Does NOT test actual video recording or YouTube upload (requires external services).
"""

import json
import pytest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

# Test paths
PROJECT_ROOT = Path(__file__).parent.parent
DEMO_SCRIPTS_DIR = PROJECT_ROOT / "ops" / "eui" / "backend" / "demo_pipelines" / "demo_scripts"


class TestDemoScriptLoader:
    """Tests for DemoScriptLoader."""

    def test_list_scripts_returns_available_scripts(self):
        """Verify list_scripts returns expected demo scripts."""
        from ops.eui.backend.demo_pipelines import DemoScriptLoader

        loader = DemoScriptLoader()
        scripts = loader.list_scripts()

        assert isinstance(scripts, list)
        # Should have at least the 3 showcase scripts
        expected_scripts = [
            "excel_flow_showcase",
            "flow_designer_showcase",
            "history_similarity_showcase",
        ]
        for script_name in expected_scripts:
            assert script_name in scripts, f"Missing expected script: {script_name}"

    def test_load_valid_script(self):
        """Verify loading a valid demo script returns DemoScript."""
        from ops.eui.backend.demo_pipelines import DemoScriptLoader

        loader = DemoScriptLoader()
        script = loader.load("excel_flow_showcase")

        assert script is not None
        assert script.name == "Excel Flow Showcase"
        assert script.duration_estimate_seconds > 0
        assert len(script.steps) > 0
        assert script.viewport["width"] == 1920
        assert script.viewport["height"] == 1080

    def test_load_invalid_script_returns_none(self):
        """Verify loading non-existent script returns None."""
        from ops.eui.backend.demo_pipelines import DemoScriptLoader

        loader = DemoScriptLoader()
        script = loader.load("non_existent_script_12345")

        assert script is None


class TestSubtitleBuilder:
    """Tests for subtitle generation."""

    def test_generate_srt_from_subtitle_map(self):
        """Verify SRT generation from timestamp map."""
        from ops.eui.backend.demo_pipelines.subtitle_builder import (
            generate_srt,
            parse_subtitle_map,
        )
        import tempfile

        subtitle_map = {
            "0.0": "Welcome to the demo",
            "5.0": "This is the second subtitle",
            "10.5": "Final subtitle",
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".srt", delete=False) as f:
            output_path = Path(f.name)

        try:
            success = generate_srt(subtitle_map, output_path)
            assert success

            content = output_path.read_text()
            assert "Welcome to the demo" in content
            assert "second subtitle" in content
            assert "Final subtitle" in content
            # Check SRT format
            assert "1\n" in content  # Index 1
            assert "-->" in content  # Timestamp separator
        finally:
            output_path.unlink(missing_ok=True)

    def test_parse_subtitle_map_ordering(self):
        """Verify subtitle entries are sorted by timestamp."""
        from ops.eui.backend.demo_pipelines.subtitle_builder import parse_subtitle_map

        subtitle_map = {
            "10.0": "Third",
            "0.0": "First",
            "5.0": "Second",
        }

        entries = parse_subtitle_map(subtitle_map)

        assert len(entries) == 3
        assert entries[0].text == "First"
        assert entries[1].text == "Second"
        assert entries[2].text == "Third"

    def test_subtitle_entry_srt_format(self):
        """Verify SubtitleEntry produces valid SRT format."""
        from ops.eui.backend.demo_pipelines.subtitle_builder import SubtitleEntry

        entry = SubtitleEntry(index=1, start_time=65.5, end_time=70.0, text="Test text")
        srt = entry.to_srt_format()

        assert srt.startswith("1\n")
        assert "00:01:05,500" in srt  # 65.5 seconds
        assert "00:01:10,000" in srt  # 70.0 seconds
        assert "Test text" in srt


class TestVideoTools:
    """Tests for video processing utilities."""

    def test_is_ffmpeg_available(self):
        """Verify FFmpeg availability check works."""
        from ops.eui.backend.utils.video_tools import is_ffmpeg_available

        # Should return True or False based on system
        result = is_ffmpeg_available()
        assert isinstance(result, bool)

    def test_color_to_ass_conversion(self):
        """Verify color name to ASS format conversion."""
        from ops.eui.backend.utils.video_tools import _color_to_ass

        assert _color_to_ass("white") == "FFFFFF"
        assert _color_to_ass("black") == "000000"
        assert _color_to_ass("red") == "0000FF"  # ASS format is BGR
        assert _color_to_ass("unknown") == "FFFFFF"  # Default to white


class TestYouTubeUploader:
    """Tests for YouTube upload utilities."""

    def test_youtube_upload_result_to_dict(self):
        """Verify YouTubeUploadResult serialization."""
        from ops.eui.product.youtube_uploader import YouTubeUploadResult

        result = YouTubeUploadResult(
            success=True,
            video_id="abc123",
            video_url="https://www.youtube.com/watch?v=abc123",
        )

        data = result.to_dict()
        assert data["success"] is True
        assert data["video_id"] == "abc123"
        assert data["video_url"] == "https://www.youtube.com/watch?v=abc123"
        assert data["error"] is None

    def test_youtube_upload_result_failure(self):
        """Verify YouTubeUploadResult for failed upload."""
        from ops.eui.product.youtube_uploader import YouTubeUploadResult

        result = YouTubeUploadResult(
            success=False, error="OAuth credentials not configured"
        )

        data = result.to_dict()
        assert data["success"] is False
        assert data["video_id"] is None
        assert "credentials" in data["error"]


class TestPipelineStatus:
    """Tests for pipeline status enum."""

    def test_pipeline_status_values(self):
        """Verify PipelineStatus enum has expected values."""
        from ops.eui.backend.demo_pipelines.youtube_pipeline import PipelineStatus

        assert PipelineStatus.PENDING.value == "pending"
        assert PipelineStatus.LOADING_SCRIPT.value == "loading_script"
        assert PipelineStatus.RUNNING_DEMO.value == "running_demo"
        assert PipelineStatus.COMPLETED.value == "completed"
        assert PipelineStatus.FAILED.value == "failed"


class TestDemoScriptJSON:
    """Tests for demo script JSON files."""

    @pytest.mark.parametrize(
        "script_name",
        [
            "excel_flow_showcase",
            "flow_designer_showcase",
            "history_similarity_showcase",
        ],
    )
    def test_demo_script_valid_json(self, script_name):
        """Verify demo script JSON files are valid."""
        script_path = DEMO_SCRIPTS_DIR / f"{script_name}.json"

        assert script_path.exists(), f"Script file missing: {script_path}"

        with open(script_path) as f:
            data = json.load(f)

        # Required fields
        assert "name" in data
        assert "description" in data
        assert "steps" in data
        assert "subtitle_map" in data
        assert "viewport" in data
        assert "duration_estimate_seconds" in data

        # Viewport dimensions
        assert data["viewport"]["width"] == 1920
        assert data["viewport"]["height"] == 1080

        # Steps must be non-empty
        assert len(data["steps"]) > 0

        # Subtitle map must have entries
        assert len(data["subtitle_map"]) > 0

    @pytest.mark.parametrize(
        "script_name",
        [
            "excel_flow_showcase",
            "flow_designer_showcase",
            "history_similarity_showcase",
        ],
    )
    def test_demo_script_steps_valid(self, script_name):
        """Verify demo script steps have valid actions."""
        script_path = DEMO_SCRIPTS_DIR / f"{script_name}.json"

        with open(script_path) as f:
            data = json.load(f)

        valid_actions = [
            "navigate",
            "click",
            "upload",
            "type",
            "screenshot",
            "wait",
            "wait_for_analysis",
            "wait_for_network",
        ]

        for i, step in enumerate(data["steps"]):
            assert "action" in step, f"Step {i} missing 'action'"
            assert step["action"] in valid_actions, f"Step {i} has invalid action: {step['action']}"


class TestProductRouterDemoEndpoints:
    """Tests for product router demo endpoints."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        from fastapi.testclient import TestClient
        from ops.eui.product.product_router import router
        from fastapi import FastAPI

        app = FastAPI()
        app.include_router(router, prefix="/product")
        return TestClient(app)

    def test_list_demo_scripts_endpoint(self, client):
        """Verify /product/demo/scripts returns script list."""
        response = client.get("/product/demo/scripts")

        # May return empty if pipeline not available, but should not error
        assert response.status_code == 200
        data = response.json()
        assert "scripts" in data
        assert "total" in data

    def test_get_demo_status_endpoint(self, client):
        """Verify /product/demo/youtube/status returns status."""
        response = client.get("/product/demo/youtube/status")

        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "last_result" in data

    def test_get_last_upload_endpoint(self, client):
        """Verify /product/demo/youtube/last-upload returns upload info."""
        response = client.get("/product/demo/youtube/last-upload")

        assert response.status_code == 200
        data = response.json()
        assert "has_upload" in data
        assert "upload" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
