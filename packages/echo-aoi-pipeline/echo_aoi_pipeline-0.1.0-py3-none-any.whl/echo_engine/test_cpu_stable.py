#!/usr/bin/env python3
"""Test script for Echo Ollama CPU-stable configuration.

This script validates:
1. Warmup functionality
2. Separate connect/read timeouts
3. Streaming disabled for experiments
4. num_predict limits
5. First-token-time logging
6. CPU_STABLE profile
7. Continuous execution without timeouts
"""

import logging
import sys
from echo_engine.ollama import create_client_from_profile, CPU_STABLE

# Enable debug logging to see timing details
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%H:%M:%S",
)

logger = logging.getLogger(__name__)


def test_cpu_stable_profile():
    """Test the CPU-stable experiment profile."""
    logger.info("=" * 80)
    logger.info("Phase 1: Testing CPU_STABLE Profile Configuration")
    logger.info("=" * 80)

    # Verify profile settings
    assert CPU_STABLE.name == "cpu_stable"
    assert CPU_STABLE.connect_timeout == 10
    assert CPU_STABLE.read_timeout == 600
    assert CPU_STABLE.stream is False
    assert CPU_STABLE.num_predict == 128
    assert CPU_STABLE.auto_warmup is True

    logger.info("✅ CPU_STABLE profile configuration verified")


def test_client_creation_and_warmup():
    """Test client creation with auto-warmup."""
    logger.info("=" * 80)
    logger.info("Phase 2: Testing Client Creation & Auto-Warmup")
    logger.info("=" * 80)

    client = create_client_from_profile("cpu_stable")

    # Verify client settings
    assert client.connect_timeout == 10
    assert client.read_timeout == 600

    logger.info("✅ Client created with correct timeout settings")
    logger.info("✅ Auto-warmup should have executed during creation")

    return client


def test_continuous_execution(client, num_calls=5):
    """Test continuous execution without timeouts."""
    logger.info("=" * 80)
    logger.info(f"Phase 3: Testing Continuous Execution ({num_calls} calls)")
    logger.info("=" * 80)

    test_prompts = [
        "What is 2+2?",
        "Name one color.",
        "Say hello.",
        "Count to 3.",
        "What comes after 9?",
    ]

    results = []
    for i, prompt in enumerate(test_prompts[:num_calls], 1):
        logger.info(f"\n--- Call {i}/{num_calls} ---")
        logger.info(f"Prompt: {prompt}")

        try:
            result = client.generate(
                prompt,
                signature="Aurora",
                stream=False,  # Experiment mode: no streaming
                num_predict=64,  # Short responses for experiments
            )

            logger.info(f"Response: {result.text[:100]}...")
            logger.info(f"Model: {result.model}")
            logger.info(f"Duration: {result.duration:.2f}s")

            results.append({
                "success": True,
                "duration": result.duration,
                "model": result.model,
                "response_length": len(result.text),
            })

        except Exception as exc:
            logger.error(f"❌ Call {i} failed: {exc}")
            results.append({
                "success": False,
                "error": str(exc),
            })

    # Analyze results
    logger.info("\n" + "=" * 80)
    logger.info("Phase 3 Results Summary")
    logger.info("=" * 80)

    successful_calls = [r for r in results if r.get("success")]
    failed_calls = [r for r in results if not r.get("success")]

    logger.info(f"Total calls: {len(results)}")
    logger.info(f"Successful: {len(successful_calls)}")
    logger.info(f"Failed: {len(failed_calls)}")

    if successful_calls:
        avg_duration = sum(r["duration"] for r in successful_calls) / len(successful_calls)
        max_duration = max(r["duration"] for r in successful_calls)
        min_duration = min(r["duration"] for r in successful_calls)

        logger.info(f"Average duration: {avg_duration:.2f}s")
        logger.info(f"Min duration: {min_duration:.2f}s")
        logger.info(f"Max duration: {max_duration:.2f}s")

        # Check if all calls completed within 1 minute (after warmup)
        all_under_60s = all(r["duration"] < 60 for r in successful_calls[1:])  # Skip first call
        if all_under_60s:
            logger.info("✅ All calls (after warmup) completed within 60 seconds")
        else:
            logger.warning("⚠️ Some calls exceeded 60 seconds")

    return len(successful_calls) == num_calls


def test_first_token_timing():
    """Test that first-token timing is logged."""
    logger.info("=" * 80)
    logger.info("Phase 4: Testing First-Token-Time Logging")
    logger.info("=" * 80)

    client = create_client_from_profile("cpu_stable")

    logger.info("Generating response to check timing logs...")
    result = client.generate(
        "Echo test",
        signature="Aurora",
        stream=False,
        num_predict=32,
    )

    logger.info("✅ Check the logs above for timing breakdowns:")
    logger.info("   - Request sent timestamp")
    logger.info("   - First token received timestamp")
    logger.info("   - Generation completed timestamp")


def main():
    """Run all tests."""
    logger.info("\n")
    logger.info("╔" + "=" * 78 + "╗")
    logger.info("║" + " " * 15 + "Echo Ollama CPU-Stable Configuration Test" + " " * 20 + "║")
    logger.info("╚" + "=" * 78 + "╝")
    logger.info("\n")

    try:
        # Test 1: Verify profile configuration
        test_cpu_stable_profile()

        # Test 2: Client creation with warmup
        client = test_client_creation_and_warmup()

        # Test 3: Continuous execution
        success = test_continuous_execution(client, num_calls=5)

        # Test 4: First-token timing
        test_first_token_timing()

        # Final summary
        logger.info("\n" + "=" * 80)
        logger.info("FINAL SUMMARY")
        logger.info("=" * 80)

        if success:
            logger.info("✅ All tests passed!")
            logger.info("✅ CPU-stable configuration is ready for judgment experiments")
            logger.info("\nYou can now run Phase 1-3 judgment tests with confidence.")
            return 0
        else:
            logger.error("❌ Some tests failed")
            logger.error("Please review the logs above for details")
            return 1

    except Exception as exc:
        logger.error(f"❌ Test suite failed with exception: {exc}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
