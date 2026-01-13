"""
Unit tests for Remote Cluster Mode.

Tests the cluster configuration loading, health monitoring,
and routing logic independently from EUE integration.
"""

import pytest
from ops.eue.remote_cluster import (
    load_cluster_config,
    ClusterHealthMonitor,
    ClusterRouter,
    resolve_cluster_endpoint,
    ClusterStrategy,
    ClusterConfig,
    ClusterNode,
)


def test_load_cluster_config(tmp_path):
    """Test loading cluster configuration from YAML."""
    yaml_content = """\
version: 1.0.0
cluster:
  mode: active_pool
  default_browser: chromium
  strategy:
    type: round_robin
nodes:
  - id: n1
    endpoint: ws://n1:3000
  - id: n2
    endpoint: ws://n2:3000
routing:
  intents:
    smoke:
      strategy_override: round_robin
"""
    spec = tmp_path / "cluster.yaml"
    spec.write_text(yaml_content, encoding="utf-8")

    cfg = load_cluster_config(str(spec))
    assert cfg.mode == "active_pool"
    assert cfg.default_browser == "chromium"
    assert len(cfg.nodes) == 2
    assert "smoke" in cfg.intents


def test_cluster_node_defaults():
    """Test ClusterNode default values."""
    node = ClusterNode(
        id="test-node",
        browser="chromium",
        endpoint="ws://localhost:3000"
    )

    assert node.id == "test-node"
    assert node.browser == "chromium"
    assert node.endpoint == "ws://localhost:3000"
    assert node.healthy is True
    assert node.weight == 1.0
    assert node.last_latency_ms is None


def test_health_monitor_record_result():
    """Test health monitor recording results."""
    nodes = [
        ClusterNode(id="n1", browser="chromium", endpoint="ws://n1:3000"),
        ClusterNode(id="n2", browser="chromium", endpoint="ws://n2:3000"),
    ]
    strategy = ClusterStrategy()
    monitor = ClusterHealthMonitor(nodes, strategy)

    # Record successful result
    monitor.record_result("n1", latency_ms=100)

    node1 = monitor.nodes["n1"]
    assert node1.last_latency_ms == 100
    assert node1.healthy is True
    assert node1.last_error is None

    # Record failed result
    monitor.record_result("n2", latency_ms=0, error="Connection failed")

    node2 = monitor.nodes["n2"]
    assert node2.last_error == "Connection failed"
    assert node2.healthy is False


def test_health_monitor_summary():
    """Test health monitor summary calculation."""
    nodes = [
        ClusterNode(id="n1", browser="chromium", endpoint="ws://n1:3000", healthy=True),
        ClusterNode(id="n2", browser="chromium", endpoint="ws://n2:3000", healthy=True),
        ClusterNode(id="n3", browser="chromium", endpoint="ws://n3:3000", healthy=False),
    ]
    strategy = ClusterStrategy(min_healthy_ratio=0.5)
    monitor = ClusterHealthMonitor(nodes, strategy)

    summary = monitor.get_health_summary()

    assert summary["total"] == 3
    assert summary["healthy"] == 2
    assert summary["healthy_ratio"] == pytest.approx(2/3)
    assert summary["min_healthy_ratio"] == 0.5


def test_latency_weighted_routing_prefers_faster_node():
    """Test that latency_weighted strategy prefers faster nodes."""
    nodes = [
        ClusterNode(id="fast", browser="chromium", endpoint="ws://fast:3000", weight=1.0),
        ClusterNode(id="slow", browser="chromium", endpoint="ws://slow:3000", weight=1.0),
    ]
    strategy = ClusterStrategy(type="latency_weighted")
    cfg = ClusterConfig(
        mode="active_pool",
        default_browser="chromium",
        strategy=strategy,
        nodes=nodes,
        intents={},
    )
    health = ClusterHealthMonitor(nodes, strategy)
    router = ClusterRouter(cfg, health)

    # Record synthetic latencies: fast node is much faster
    health.record_result("fast", latency_ms=50)
    health.record_result("slow", latency_ms=500)

    # Run multiple selections and verify fast node is preferred
    picks = [router.choose_node()[0].id for _ in range(50)]
    fast_ratio = picks.count("fast") / len(picks)

    # With latency_weighted, fast node should be selected most of the time
    # (10x faster = 10x higher weight in weighted random selection)
    assert fast_ratio > 0.6, f"Expected fast node to be chosen most of the time, got {fast_ratio}"


def test_round_robin_strategy():
    """Test round_robin strategy distributes evenly."""
    nodes = [
        ClusterNode(id="n1", browser="chromium", endpoint="ws://n1:3000"),
        ClusterNode(id="n2", browser="chromium", endpoint="ws://n2:3000"),
        ClusterNode(id="n3", browser="chromium", endpoint="ws://n3:3000"),
    ]
    strategy = ClusterStrategy(type="round_robin")
    cfg = ClusterConfig(
        mode="active_pool",
        default_browser="chromium",
        strategy=strategy,
        nodes=nodes,
        intents={},
    )
    health = ClusterHealthMonitor(nodes, strategy)
    router = ClusterRouter(cfg, health)

    # Pick 9 nodes (3 full cycles)
    picks = [router.choose_node()[0].id for _ in range(9)]

    # Each node should be selected exactly 3 times
    assert picks.count("n1") == 3
    assert picks.count("n2") == 3
    assert picks.count("n3") == 3


def test_random_strategy():
    """Test random strategy is non-deterministic."""
    nodes = [
        ClusterNode(id="n1", browser="chromium", endpoint="ws://n1:3000"),
        ClusterNode(id="n2", browser="chromium", endpoint="ws://n2:3000"),
    ]
    strategy = ClusterStrategy(type="random")
    cfg = ClusterConfig(
        mode="active_pool",
        default_browser="chromium",
        strategy=strategy,
        nodes=nodes,
        intents={},
    )
    health = ClusterHealthMonitor(nodes, strategy)
    router = ClusterRouter(cfg, health)

    # Pick many nodes
    picks = [router.choose_node()[0].id for _ in range(100)]

    # Both nodes should be selected (very high probability)
    assert "n1" in picks
    assert "n2" in picks

    # Distribution should be reasonably balanced (not perfectly equal)
    n1_count = picks.count("n1")
    assert 30 < n1_count < 70, f"Random distribution seems biased: {n1_count}/100"


def test_intent_filtering_by_tags():
    """Test intent-based filtering by node tags."""
    from ops.eue.remote_cluster import ClusterIntent

    nodes = [
        ClusterNode(id="primary1", browser="chromium", endpoint="ws://p1:3000", tags=["primary"]),
        ClusterNode(id="primary2", browser="chromium", endpoint="ws://p2:3000", tags=["primary"]),
        ClusterNode(id="backup1", browser="chromium", endpoint="ws://b1:3000", tags=["backup"]),
    ]
    strategy = ClusterStrategy(type="round_robin")
    cfg = ClusterConfig(
        mode="active_pool",
        default_browser="chromium",
        strategy=strategy,
        nodes=nodes,
        intents={
            "smoke": ClusterIntent(
                name="smoke",
                allowed_tags=["primary"]
            )
        },
    )
    health = ClusterHealthMonitor(nodes, strategy)
    router = ClusterRouter(cfg, health)

    # Without intent: all nodes eligible
    picks_default = [router.choose_node()[0].id for _ in range(6)]
    assert "primary1" in picks_default
    assert "primary2" in picks_default
    assert "backup1" in picks_default

    # Reset round robin counter
    router._rr_index = 0

    # With "smoke" intent: only primary nodes eligible
    picks_smoke = [router.choose_node(intent="smoke")[0].id for _ in range(6)]
    assert "primary1" in picks_smoke
    assert "primary2" in picks_smoke
    assert "backup1" not in picks_smoke


def test_unhealthy_nodes_excluded():
    """Test that unhealthy nodes are excluded from routing."""
    nodes = [
        ClusterNode(id="healthy", browser="chromium", endpoint="ws://h:3000", healthy=True),
        ClusterNode(id="unhealthy", browser="chromium", endpoint="ws://u:3000", healthy=False),
    ]
    strategy = ClusterStrategy()
    cfg = ClusterConfig(
        mode="active_pool",
        default_browser="chromium",
        strategy=strategy,
        nodes=nodes,
        intents={},
    )
    health = ClusterHealthMonitor(nodes, strategy)
    router = ClusterRouter(cfg, health)

    # Only healthy node should be selected
    picks = [router.choose_node()[0].id for _ in range(10)]
    assert all(p == "healthy" for p in picks)


def test_no_healthy_nodes_returns_none():
    """Test that router returns None when no healthy nodes available."""
    nodes = [
        ClusterNode(id="n1", browser="chromium", endpoint="ws://n1:3000", healthy=False),
        ClusterNode(id="n2", browser="chromium", endpoint="ws://n2:3000", healthy=False),
    ]
    strategy = ClusterStrategy()
    cfg = ClusterConfig(
        mode="active_pool",
        default_browser="chromium",
        strategy=strategy,
        nodes=nodes,
        intents={},
    )
    health = ClusterHealthMonitor(nodes, strategy)
    router = ClusterRouter(cfg, health)

    node, info = router.choose_node()

    assert node is None
    assert info["reason"] == "no_healthy_nodes"
    assert info["summary"]["healthy"] == 0


def test_resolve_cluster_endpoint_no_spec():
    """Test resolve_cluster_endpoint with no spec file."""
    browser, endpoint, info = resolve_cluster_endpoint(spec_path=None)

    assert browser is None
    assert endpoint is None
    assert info.get("reason") == "no_spec"


def test_resolve_cluster_endpoint_with_spec(tmp_path):
    """Test resolve_cluster_endpoint with valid spec file."""
    yaml_content = """\
version: 1.0.0
cluster:
  mode: active_pool
  default_browser: chromium
  strategy:
    type: round_robin
nodes:
  - id: n1
    endpoint: ws://n1:3000
  - id: n2
    endpoint: ws://n2:3000
routing:
  intents: {}
"""
    spec = tmp_path / "cluster.yaml"
    spec.write_text(yaml_content, encoding="utf-8")

    browser, endpoint, info = resolve_cluster_endpoint(spec_path=str(spec))

    assert browser == "chromium"
    assert endpoint in ["ws://n1:3000", "ws://n2:3000"]
    assert info["reason"] == "selected"


def test_node_weight_affects_selection():
    """Test that node weight affects selection probability."""
    nodes = [
        ClusterNode(id="heavy", browser="chromium", endpoint="ws://h:3000", weight=10.0),
        ClusterNode(id="light", browser="chromium", endpoint="ws://l:3000", weight=1.0),
    ]
    strategy = ClusterStrategy(type="latency_weighted")
    cfg = ClusterConfig(
        mode="active_pool",
        default_browser="chromium",
        strategy=strategy,
        nodes=nodes,
        intents={},
    )
    health = ClusterHealthMonitor(nodes, strategy)
    router = ClusterRouter(cfg, health)

    # No latency data, so routing falls back to static weights
    picks = [router.choose_node()[0].id for _ in range(100)]
    heavy_ratio = picks.count("heavy") / len(picks)

    # Heavy node (10x weight) should be selected much more often
    assert heavy_ratio > 0.7, f"Expected heavy node to dominate, got {heavy_ratio}"
