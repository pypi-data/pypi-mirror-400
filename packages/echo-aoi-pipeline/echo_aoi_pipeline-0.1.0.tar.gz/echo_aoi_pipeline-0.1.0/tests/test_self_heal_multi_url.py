#!/usr/bin/env python3
"""
Self-Heal Multi-URL Scenario Test

Tests Self-Heal with different URLs per attempt to generate meaningful diffs.
This ensures regression queue contains actual DOM differences.
"""

import asyncio
import logging
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from ops.mcp.playwright.self_heal_orchestrator import create_orchestrator
from ops.mcp.playwright.mcp_bridge import MCPPlaywrightBridge

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# Test URLs for generating different DOM states
TEST_URLS = [
    "https://example.com",
    "https://example.org",
    "https://www.iana.org/domains/reserved",
]

attempt_counter = {"count": 0}


async def multi_url_executor():
    """
    Executor that visits different URLs on each attempt.

    This ensures:
    - Attempt 1: example.com → Fails
    - Attempt 2: example.org → Fails (different DOM)
    - Attempt 3: iana.org → Succeeds
    """
    attempt_counter["count"] += 1
    current_attempt = attempt_counter["count"]

    logger.info("[MultiURLExecutor] Attempt %d starting...", current_attempt)

    # Select URL based on attempt number
    url_index = min(current_attempt - 1, len(TEST_URLS) - 1)
    target_url = TEST_URLS[url_index]

    # Fail on first TWO attempts
    if current_attempt <= 2:
        logger.warning(
            "[MultiURLExecutor] Simulating failure on attempt %d with URL: %s",
            current_attempt,
            target_url,
        )
        # Navigate before failing to capture different DOM states
        bridge = MCPPlaywrightBridge(auto_verify=True)
        await bridge.initialize(headless=True)
        await bridge.navigate(target_url)

        screenshot_path = Path(f"artifacts/test_multi_url_attempt_{current_attempt}.png")
        await bridge.screenshot(str(screenshot_path))
        await bridge.cleanup()

        raise RuntimeError(f"Simulated failure at {target_url}")

    # Succeed on third attempt
    logger.info("[MultiURLExecutor] Attempt %d - executing successfully at %s", current_attempt, target_url)

    bridge = MCPPlaywrightBridge(auto_verify=True)
    await bridge.initialize(headless=True)
    await bridge.navigate(target_url)

    screenshot_path = Path("artifacts/test_multi_url_success.png")
    await bridge.screenshot(str(screenshot_path))

    dom_html = await bridge.dom_snapshot()
    await bridge.cleanup()

    logger.info("[MultiURLExecutor] Execution completed successfully on attempt %d", current_attempt)

    return {
        "attempt": current_attempt,
        "url": target_url,
        "screenshot": str(screenshot_path),
        "dom_length": len(dom_html),
        "success": True,
    }


async def main():
    """Run the multi-URL scenario test."""
    logger.info("=" * 80)
    logger.info("Self-Heal Multi-URL Scenario Test - Starting")
    logger.info("=" * 80)

    # Create orchestrator
    orchestrator = create_orchestrator(
        scenario="self_heal_multi_url_test",
        metadata={
            "priority": "critical",
            "test_type": "regression_validation",
            "max_attempts": 5,
        },
    )

    logger.info(
        "[TEST] Orchestrator configured: max_attempts=%d, timecapsule=%s",
        orchestrator.config.max_attempts,
        orchestrator.config.enable_timecapsule,
    )

    # Define workflow
    steps = [
        {
            "name": "multi_url_navigation",
            "executor": multi_url_executor,
            "url": TEST_URLS[0],  # Base URL for first attempt
            "notes": "Testing Self-Heal with different URLs for meaningful diff generation",
            "allow_failure": False,
        },
    ]

    logger.info("[TEST] Running workflow with %d steps...", len(steps))

    # Run workflow
    result = await orchestrator.run_workflow_async(steps)

    logger.info("=" * 80)
    logger.info("Self-Heal Multi-URL Scenario Test - Results")
    logger.info("=" * 80)
    logger.info("Overall Success: %s", result.success)
    logger.info("Completed Steps: %d / %d", result.metadata["completed_steps"], result.metadata["total_steps"])

    # Print detailed attempt information
    for idx, step_result in enumerate(result.step_results, 1):
        logger.info("\n--- Step %d: %s ---", idx, "SUCCESS" if step_result.success else "FAILED")
        logger.info("Total Attempts: %d", len(step_result.attempts))

        for attempt in step_result.attempts:
            logger.info(
                "  Attempt %d: %s (timestamp=%s)",
                attempt.attempt,
                "SUCCESS" if attempt.success else "FAILED",
                attempt.timestamp,
            )
            if attempt.error:
                logger.info("    Error: %s", attempt.error)
            if attempt.capsule_dir:
                logger.info("    Capsule Dir: %s", attempt.capsule_dir)
            if attempt.diff_path:
                logger.info("    Diff Path: %s", attempt.diff_path)
                # Check diff file size
                diff_file = Path(attempt.diff_path)
                if diff_file.exists():
                    size = diff_file.stat().st_size
                    logger.info("    Diff Size: %d bytes", size)

    # Export report
    report_path = Path("artifacts/auto_demo/self_heal/multi_url_test_report.json")
    orchestrator.export_report(report_path)
    logger.info("\n[TEST] Report exported to: %s", report_path)

    logger.info("=" * 80)
    logger.info("Self-Heal Multi-URL Scenario Test - Complete")
    logger.info("=" * 80)

    return result


if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        sys.exit(0 if result.success else 1)
    except KeyboardInterrupt:
        logger.info("\n[TEST] Interrupted by user")
        sys.exit(130)
    except Exception as exc:
        logger.exception("[TEST] Fatal error: %s", exc)
        sys.exit(1)
