"""Central LLM routing layer for Echo OS.

Routes inference requests to appropriate engines based on context:
- Judgment/batch → Ollama (60~180s, deep reasoning)
- Interactive → Streaming engine (< 1s, rhythm-critical)

Evidence: [OLLAMA_TRACE] measurements show Ollama unsuitable for interactive use.
Policy: echo_engine/routing/inference_policy.py
"""

from __future__ import annotations

import logging
from typing import Optional

from echo_engine.ollama.client import GenerationResult, OllamaClient
from echo_engine.routing import InferenceContext, select_engine
from echo_engine.routing.inference_policy import EngineType
from echo_engine.strategy.meta_stop_guard import MetaStopContext

logger = logging.getLogger(__name__)


class StreamingEngineNotConfiguredError(RuntimeError):
    """Raised when streaming engine is required but not available."""


class LLMRouter:
    """Central routing layer for LLM inference.

    Design principle: Separate engines by rhythm, not capability.
    - Ollama: judgment engine (slow, deep, batch)
    - Streaming: interaction engine (fast, streaming, real-time)
    """

    def __init__(
        self,
        ollama_host: str = "http://localhost:11434",
        streaming_engine=None,  # type: ignore - TBD
    ):
        """Initialize router with available engines.

        Args:
            ollama_host: Ollama server URL
            streaming_engine: Streaming-capable engine (TBD, currently raises error if needed)
        """
        self.ollama_client = OllamaClient(host=ollama_host)
        self.streaming_engine = streaming_engine

    def generate(
        self,
        prompt: str,
        *,
        context: Optional[InferenceContext] = None,
        signature: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        num_predict: Optional[int] = None,
        guard_context: Optional[MetaStopContext] = None,
    ) -> GenerationResult:
        """Generate completion using appropriate engine.

        Args:
            prompt: User prompt
            context: Inference context (default: judgment)
            signature: Echo signature (Aurora, Phoenix, Sage, Companion)
            model: Model override
            temperature: Sampling temperature
            num_predict: Max tokens to generate
            guard_context: Meta stop guard context

        Returns:
            Generation result from selected engine

        Raises:
            StreamingEngineNotConfiguredError: If interactive context requires streaming
                but streaming engine is not configured
        """
        # Default to judgment context if not specified
        if context is None:
            context = InferenceContext.judgment()
            logger.debug("No context provided, defaulting to judgment context")

        # Select engine based on context
        engine_type = select_engine(context)
        logger.info(
            f"Routing to {engine_type.value} engine for context: "
            f"task_type={context.task_type.value}, interactive={context.interactive}"
        )

        if engine_type == EngineType.OLLAMA:
            return self._generate_ollama(
                prompt,
                signature=signature,
                model=model,
                temperature=temperature,
                num_predict=num_predict,
                guard_context=guard_context,
            )

        elif engine_type == EngineType.STREAMING:
            if self.streaming_engine is None:
                raise StreamingEngineNotConfiguredError(
                    f"Streaming engine required for context {context.task_type.value} "
                    f"(interactive={context.interactive}, streaming_required={context.streaming_required}), "
                    f"but streaming engine is not configured. "
                    f"Do NOT fallback to Ollama (60~180s latency incompatible with user rhythm)."
                )
            return self._generate_streaming(
                prompt,
                signature=signature,
                model=model,
                temperature=temperature,
                num_predict=num_predict,
            )

        else:
            raise ValueError(f"Unknown engine type: {engine_type}")

    def _generate_ollama(
        self,
        prompt: str,
        *,
        signature: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        num_predict: Optional[int] = None,
        guard_context: Optional[MetaStopContext] = None,
    ) -> GenerationResult:
        """Generate using Ollama (judgment engine)."""
        logger.debug("Executing Ollama generation (expected latency: 30~180s)")
        return self.ollama_client.generate(
            prompt,
            signature=signature,
            model=model,
            temperature=temperature,
            stream=False,  # Ollama always turn-based in this architecture
            num_predict=num_predict,
            guard_context=guard_context,
        )

    def _generate_streaming(
        self,
        prompt: str,
        *,
        signature: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        num_predict: Optional[int] = None,
    ) -> GenerationResult:
        """Generate using streaming engine (interaction engine).

        Currently raises error as streaming engine is TBD.
        """
        # TBD: Implement streaming engine integration
        # Options: vLLM, llama.cpp server, Ollama stream=True
        raise NotImplementedError(
            "Streaming engine not yet implemented. "
            "Candidates: vLLM (streaming), llama.cpp server (streaming), Ollama INTERACTIVE profile."
        )


# Convenience factory functions


def create_router(
    ollama_host: str = "http://localhost:11434",
) -> LLMRouter:
    """Create default LLM router with Ollama only.

    Args:
        ollama_host: Ollama server URL

    Returns:
        Configured LLM router

    Example:
        >>> router = create_router()
        >>> ctx = InferenceContext.judgment()
        >>> result = router.generate("Analyze this", context=ctx)
    """
    return LLMRouter(ollama_host=ollama_host)


# Singleton for convenience
_default_router: Optional[LLMRouter] = None


def get_default_router() -> LLMRouter:
    """Get or create default router instance.

    Returns:
        Shared LLM router instance
    """
    global _default_router
    if _default_router is None:
        _default_router = create_router()
    return _default_router


def generate_judgment(
    prompt: str,
    *,
    signature: Optional[str] = None,
    model: Optional[str] = None,
    temperature: float = 0.7,
    num_predict: Optional[int] = None,
) -> GenerationResult:
    """Convenience function for judgment context (Ollama).

    Args:
        prompt: User prompt
        signature: Echo signature
        model: Model override
        temperature: Sampling temperature
        num_predict: Max tokens

    Returns:
        Generation result from Ollama

    Example:
        >>> result = generate_judgment("Evaluate this decision")
    """
    router = get_default_router()
    ctx = InferenceContext.judgment()
    return router.generate(
        prompt,
        context=ctx,
        signature=signature,
        model=model,
        temperature=temperature,
        num_predict=num_predict,
    )


def generate_interactive(
    prompt: str,
    *,
    signature: Optional[str] = None,
    model: Optional[str] = None,
    temperature: float = 0.7,
    max_latency: float = 1.0,
) -> GenerationResult:
    """Convenience function for interactive context (streaming).

    Args:
        prompt: User prompt
        signature: Echo signature
        model: Model override
        temperature: Sampling temperature
        max_latency: Maximum acceptable latency (seconds)

    Returns:
        Generation result from streaming engine

    Raises:
        StreamingEngineNotConfiguredError: Streaming engine not available

    Example:
        >>> result = generate_interactive("Hello!", max_latency=1.0)
    """
    router = get_default_router()
    ctx = InferenceContext.interactive(max_latency=max_latency)
    return router.generate(
        prompt,
        context=ctx,
        signature=signature,
        model=model,
        temperature=temperature,
    )
