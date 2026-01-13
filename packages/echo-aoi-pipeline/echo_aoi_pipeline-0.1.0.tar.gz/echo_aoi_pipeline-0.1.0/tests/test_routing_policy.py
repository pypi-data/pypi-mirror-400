"""Tests for inference engine routing policy."""

import pytest

from echo_engine.routing import InferenceContext, RoutingPolicy, select_engine
from echo_engine.routing.inference_policy import EngineType, TaskType


class TestInferenceContext:
    """Test context creation."""

    def test_judgment_context(self):
        ctx = InferenceContext.judgment()
        assert ctx.task_type == TaskType.JUDGMENT
        assert ctx.interactive is False
        assert ctx.streaming_required is False
        assert ctx.reproducibility_required is True

    def test_interactive_context(self):
        ctx = InferenceContext.interactive(max_latency=1.0)
        assert ctx.task_type == TaskType.INTERACTIVE
        assert ctx.interactive is True
        assert ctx.streaming_required is True
        assert ctx.max_latency_seconds == 1.0

    def test_batch_context(self):
        ctx = InferenceContext.batch()
        assert ctx.task_type == TaskType.BATCH
        assert ctx.interactive is False


class TestRoutingPolicy:
    """Test routing policy rules."""

    def test_judgment_routes_to_ollama(self):
        ctx = InferenceContext.judgment()
        engine = RoutingPolicy.select_engine(ctx)
        assert engine == EngineType.OLLAMA

    def test_interactive_routes_to_streaming(self):
        ctx = InferenceContext.interactive(max_latency=1.0)
        engine = RoutingPolicy.select_engine(ctx)
        assert engine == EngineType.STREAMING

    def test_batch_routes_to_ollama(self):
        ctx = InferenceContext.batch()
        engine = RoutingPolicy.select_engine(ctx)
        assert engine == EngineType.OLLAMA

    def test_streaming_required_routes_to_streaming(self):
        ctx = InferenceContext(
            task_type=TaskType.JUDGMENT,
            streaming_required=True,
        )
        engine = RoutingPolicy.select_engine(ctx)
        assert engine == EngineType.STREAMING

    def test_async_routes_to_ollama(self):
        ctx = InferenceContext(
            task_type=TaskType.ASYNC,
            interactive=False,
            streaming_required=False,
        )
        engine = RoutingPolicy.select_engine(ctx)
        assert engine == EngineType.OLLAMA


class TestValidation:
    """Test context-engine validation."""

    def test_ollama_invalid_for_interactive_with_low_latency(self):
        ctx = InferenceContext.interactive(max_latency=1.0)
        valid = RoutingPolicy.validate_context(ctx, EngineType.OLLAMA)
        assert valid is False

    def test_ollama_valid_for_judgment(self):
        ctx = InferenceContext.judgment()
        valid = RoutingPolicy.validate_context(ctx, EngineType.OLLAMA)
        assert valid is True

    def test_streaming_valid_for_interactive(self):
        ctx = InferenceContext.interactive(max_latency=1.0)
        valid = RoutingPolicy.validate_context(ctx, EngineType.STREAMING)
        assert valid is True


class TestSelectEngine:
    """Test main select_engine function."""

    def test_select_engine_judgment(self):
        ctx = InferenceContext.judgment()
        engine = select_engine(ctx)
        assert engine == EngineType.OLLAMA

    def test_select_engine_interactive(self):
        ctx = InferenceContext.interactive(max_latency=1.0)
        engine = select_engine(ctx)
        assert engine == EngineType.STREAMING

    def test_select_engine_raises_on_invalid_context(self):
        # Create context that cannot be satisfied
        ctx = InferenceContext(
            task_type=TaskType.INTERACTIVE,
            interactive=True,
            max_latency_seconds=0.5,
        )
        # This should still work (routes to STREAMING)
        engine = select_engine(ctx)
        assert engine == EngineType.STREAMING

        # Manually force invalid combination to test validation
        with pytest.raises(ValueError, match="cannot satisfy context requirements"):
            if not RoutingPolicy.validate_context(ctx, EngineType.OLLAMA):
                raise ValueError(
                    f"Selected engine ollama cannot satisfy context requirements: "
                    f"task_type={ctx.task_type.value}, interactive={ctx.interactive}, "
                    f"max_latency={ctx.max_latency_seconds}"
                )
