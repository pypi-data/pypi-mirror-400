"""
test_viewer_integration.py - EUI Visualization Engine Integration Tests

Purpose: Test all viewer endpoints and functionality
Philosophy: Ensure environment-independent operation

Version: 1.0.0
Last Updated: 2025-11-27
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from app import app

client = TestClient(app)


class TestViewerEndpoints:
    """Test all viewer API endpoints"""

    def test_health_check(self):
        """Test basic backend health"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"

    def test_viewer_info(self):
        """Test viewer information endpoint"""
        response = client.get("/api/eui/view/info")
        assert response.status_code == 200
        data = response.json()
        assert data["version"] == "1.0.0"
        assert "components" in data
        assert data["environment_independence"] == True

    # ==================== Screen Viewer Tests ====================

    def test_get_screen_capture(self):
        """Test getting screen capture"""
        response = client.get("/api/eui/view/screen")
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "timestamp" in data
        assert data["width"] == 800
        assert data["height"] == 600
        assert data["source"] == "mock"

    def test_capture_screen(self):
        """Test triggering new screen capture"""
        response = client.post("/api/eui/view/screen/capture")
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["source"] == "manual"

    # ==================== Document Viewer Tests ====================

    def test_get_document_markdown(self):
        """Test getting markdown document"""
        response = client.get("/api/eui/view/document/mock-markdown")
        assert response.status_code == 200
        data = response.json()
        assert data["format"] == "markdown"
        assert data["name"] == "echo_os_docs.md"
        assert "content" in data

    def test_get_document_log(self):
        """Test getting log document"""
        response = client.get("/api/eui/view/document/mock-log")
        assert response.status_code == 200
        data = response.json()
        assert data["format"] == "log"
        assert data["name"] == "system.log"

    def test_get_document_excel(self):
        """Test getting excel document"""
        response = client.get("/api/eui/view/document/mock-excel")
        assert response.status_code == 200
        data = response.json()
        assert data["format"] == "excel"
        assert isinstance(data["content"], list)
        assert len(data["content"]) > 0

    def test_get_document_not_found(self):
        """Test document not found"""
        response = client.get("/api/eui/view/document/mock-unknown")
        assert response.status_code == 404

    def test_parse_document(self):
        """Test document parsing"""
        response = client.post("/api/eui/view/document/parse?file_path=/tmp/test.md")
        assert response.status_code == 200
        data = response.json()
        assert "format" in data

    # ==================== Map Viewer Tests ====================

    def test_get_map_tiles(self):
        """Test getting map tiles"""
        response = client.get("/api/eui/view/map/tiles?center_x=0&center_y=0&zoom=1")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

        # Check tile structure
        tile = data[0]
        assert "x" in tile
        assert "y" in tile
        assert "zoom" in tile
        assert "color" in tile

    def test_navigate_map(self):
        """Test map navigation"""
        response = client.post("/api/eui/view/map/navigate", json={
            "center_x": 100,
            "center_y": 200,
            "zoom": 1.5
        })
        assert response.status_code == 200
        data = response.json()
        assert data["center_x"] == 100
        assert data["center_y"] == 200
        assert data["zoom"] == 1.5

    # ==================== Graph Viewer Tests ====================

    def test_get_graph_data(self):
        """Test getting graph data"""
        response = client.get("/api/eui/view/graph/data?chart_type=bar")
        assert response.status_code == 200
        data = response.json()
        assert "labels" in data
        assert "datasets" in data
        assert isinstance(data["labels"], list)
        assert isinstance(data["datasets"], list)
        assert len(data["datasets"]) > 0

    def test_render_graph(self):
        """Test graph rendering"""
        response = client.post("/api/eui/view/graph/render", json={
            "labels": ["A", "B", "C"],
            "datasets": [
                {"label": "Test", "data": [1, 2, 3], "color": "#fff"}
            ]
        })
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "rendered"
        assert data["datasets_count"] == 1

    # ==================== Status Bar Tests ====================

    def test_get_system_status(self):
        """Test getting system status"""
        response = client.get("/api/eui/view/status")
        assert response.status_code == 200
        data = response.json()
        assert "backend_health" in data
        assert "api_latency" in data
        assert "current_signature" in data
        assert "connection_status" in data
        assert "resource_usage" in data

        # Check resource usage structure
        assert "cpu" in data["resource_usage"]
        assert "memory" in data["resource_usage"]

    def test_stream_system_status(self):
        """Test system status stream endpoint exists"""
        # Note: SSE testing requires special handling
        # Just verify endpoint is accessible
        response = client.get("/api/eui/view/status/stream")
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/event-stream; charset=utf-8"


class TestViewerMockMode:
    """Test mock mode functionality"""

    def test_all_endpoints_work_in_mock_mode(self):
        """Verify all endpoints work without external dependencies"""
        endpoints = [
            ("/api/eui/view/info", "get"),
            ("/api/eui/view/screen", "get"),
            ("/api/eui/view/document/mock-markdown", "get"),
            ("/api/eui/view/map/tiles", "get"),
            ("/api/eui/view/graph/data", "get"),
            ("/api/eui/view/status", "get"),
        ]

        for endpoint, method in endpoints:
            if method == "get":
                response = client.get(endpoint)
            else:
                response = client.post(endpoint)

            assert response.status_code == 200, f"Failed: {method.upper()} {endpoint}"


class TestViewerDataConsistency:
    """Test data consistency across requests"""

    def test_map_tiles_are_deterministic(self):
        """Map tiles should be deterministic for same coordinates"""
        response1 = client.get("/api/eui/view/map/tiles?center_x=0&center_y=0&zoom=1")
        response2 = client.get("/api/eui/view/map/tiles?center_x=0&center_y=0&zoom=1")

        assert response1.json() == response2.json()

    def test_graph_data_structure(self):
        """Graph data should have consistent structure"""
        response = client.get("/api/eui/view/graph/data")
        data = response.json()

        assert len(data["labels"]) > 0
        for dataset in data["datasets"]:
            assert "label" in dataset
            assert "data" in dataset
            assert "color" in dataset
            assert len(dataset["data"]) == len(data["labels"])


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
