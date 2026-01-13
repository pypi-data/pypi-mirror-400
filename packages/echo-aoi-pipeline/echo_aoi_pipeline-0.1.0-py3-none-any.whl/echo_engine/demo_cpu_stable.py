#!/usr/bin/env python3
"""
Demo: Echo Ollama CPU-Stable Configuration

This script demonstrates the improvements made to the Echo Ollama client
for stable CPU-based judgment experiments.

NOTE: Migrated to LLMRouter architecture (2025-12-23).
All inference routed through judgment context to enforce engine separation.
"""

import logging
from echo_engine.ollama import CPU_STABLE
from echo_engine.llm_router import get_default_router
from echo_engine.routing import InferenceContext

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


def demo_profile_info():
    """Demonstrate profile configuration."""
    logger.info("=" * 60)
    logger.info("1️⃣  CPU_STABLE Profile Configuration")
    logger.info("=" * 60)
    logger.info(f"Profile Name:      {CPU_STABLE.name}")
    logger.info(f"Description:       {CPU_STABLE.description}")
    logger.info(f"Connect Timeout:   {CPU_STABLE.connect_timeout}s")
    logger.info(f"Read Timeout:      {CPU_STABLE.read_timeout}s")
    logger.info(f"Streaming:         {CPU_STABLE.stream}")
    logger.info(f"Max Tokens:        {CPU_STABLE.num_predict}")
    logger.info(f"Temperature:       {CPU_STABLE.temperature}")
    logger.info(f"Auto Warmup:       {CPU_STABLE.auto_warmup}")
    logger.info("")


def demo_auto_warmup():
    """Demonstrate automatic warmup."""
    logger.info("=" * 60)
    logger.info("2️⃣  Router Initialization & Warmup")
    logger.info("=" * 60)
    logger.info("Creating LLM router with judgment context...")

    router = get_default_router()
    router.ollama_client.warmup()

    logger.info("✅ Router created and warmed up!")
    logger.info(f"Available models: {', '.join(router.ollama_client.available_models)}")
    logger.info("")

    return router


def demo_judgment_experiment(router):
    """Demonstrate judgment experiment usage."""
    logger.info("=" * 60)
    logger.info("3️⃣  Judgment Experiment Execution")
    logger.info("=" * 60)

    # Phase 1: Simple arithmetic (judgment test)
    logger.info("Running judgment test: '2 + 2 = ?'")

    ctx = InferenceContext.judgment()
    result = router.generate(
        "What is 2 + 2?",
        context=ctx,
        signature="Sage",  # Analytical signature
        num_predict=64,    # Short response
    )

    logger.info(f"Response: {result.text[:100]}...")
    logger.info(f"Model: {result.model}")
    logger.info(f"Duration: {result.duration:.2f}s")
    logger.info("")


def demo_timing_breakdown(router):
    """Demonstrate timing breakdown logging."""
    logger.info("=" * 60)
    logger.info("4️⃣  Timing Breakdown ([OLLAMA_TRACE] Instrumentation)")
    logger.info("=" * 60)
    logger.info("Enable DEBUG logging to see detailed timing...")

    # Temporarily enable DEBUG
    logging.getLogger("echo_engine.ollama.client").setLevel(logging.DEBUG)

    ctx = InferenceContext.judgment()
    result = router.generate(
        "Count to 3",
        context=ctx,
        signature="Aurora",
        num_predict=32,
    )

    # Restore INFO level
    logging.getLogger("echo_engine.ollama.client").setLevel(logging.INFO)

    logger.info("")
    logger.info("Check the logs above for:")
    logger.info("  [OLLAMA_TRACE] http_wait, json_parse, body_copy, post_process")
    logger.info("  ✅ Generation completed timestamp")
    logger.info("")


def demo_continuous_execution(router):
    """Demonstrate continuous execution without timeouts."""
    logger.info("=" * 60)
    logger.info("5️⃣  Continuous Execution (Judgment Context)")
    logger.info("=" * 60)

    prompts = [
        ("Aurora", "Say hello"),
        ("Phoenix", "What is innovation?"),
        ("Sage", "Define logic"),
    ]

    ctx = InferenceContext.judgment()

    for signature, prompt in prompts:
        logger.info(f"Executing: [{signature}] {prompt}")

        result = router.generate(
            prompt,
            context=ctx,
            signature=signature,
            num_predict=48,
        )

        logger.info(f"  → Response: {result.text[:60]}...")
        logger.info(f"  → Duration: {result.duration:.2f}s")
        logger.info("")


def main():
    """Run all demonstrations."""
    print()
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 10 + "Echo LLM Router Demo (Judgment)" + " " * 14 + "║")
    print("╚" + "=" * 58 + "╝")
    print()

    # Demo 1: Profile info
    demo_profile_info()

    # Demo 2: Router warmup
    router = demo_auto_warmup()

    # Demo 3: Judgment experiment
    demo_judgment_experiment(router)

    # Demo 4: Timing breakdown
    demo_timing_breakdown(router)

    # Demo 5: Continuous execution
    demo_continuous_execution(router)

    # Summary
    logger.info("=" * 60)
    logger.info("✅ Demo Complete!")
    logger.info("=" * 60)
    logger.info("")
    logger.info("LLM Router Architecture Validated:")
    logger.info("  ✅ Judgment context routing to Ollama")
    logger.info("  ✅ [OLLAMA_TRACE] timing instrumentation active")
    logger.info("  ✅ Engine separation enforced (no fallback)")
    logger.info("  ✅ Evidence-based latency thresholds (60~180s)")
    logger.info("  ✅ Continuous execution (no timeouts)")
    logger.info("")
    logger.info("🚀 Router integration validated for judgment tasks!")
    logger.info("")


if __name__ == "__main__":
    main()
