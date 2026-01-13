#!/usr/bin/env python3
"""
Self-Heal Double Failure Scenario Test

Tests Self-Heal with multiple consecutive failures to demonstrate:
1. First attempt fails
2. Second attempt also fails
3. Diff generated between attempts
4. Third attempt succeeds
5. Regression queue updated with diff
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

# Global counter to simulate failure on first two attempts
attempt_counter = {"count": 0}


async def double_flaky_executor():
    """
    Executor that fails on first TWO attempts, succeeds on third.

    This ensures:
    - Attempt 1: Fails → Capsule created
    - Attempt 2: Fails → Capsule created → Diff generated
    - Attempt 3: Succeeds
    """
    attempt_counter["count"] += 1
    current_attempt = attempt_counter["count"]

    logger.info("[DoubleFlakyExecutor] Attempt %d starting...", current_attempt)

    # Fail on first TWO attempts
    if current_attempt <= 2:
        logger.warning(
            "[DoubleFlakyExecutor] Simulating failure on attempt %d",
            current_attempt,
        )
        # Different error messages to create different states
        if current_attempt == 1:
            raise RuntimeError("Simulated transient failure - network timeout")
        else:
            raise RuntimeError("Simulated transient failure - rate limit exceeded")

    # Succeed on third attempt
    logger.info("[DoubleFlakyExecutor] Attempt %d - executing successfully", current_attempt)

    bridge = MCPPlaywrightBridge(auto_verify=True)
    await bridge.initialize(headless=True)
    await bridge.navigate("https://example.com")

    screenshot_path = Path("artifacts/test_double_flaky_screenshot.png")
    await bridge.screenshot(str(screenshot_path))

    dom_html = await bridge.dom_snapshot()
    await bridge.cleanup()

    logger.info("[DoubleFlakyExecutor] Execution completed successfully on attempt %d", current_attempt)

    return {
        "attempt": current_attempt,
        "screenshot": str(screenshot_path),
        "dom_length": len(dom_html),
        "success": True,
    }


async def main():
    """Run the double failure scenario test."""
    logger.info("=" * 80)
    logger.info("Self-Heal Double Failure Scenario Test - Starting")
    logger.info("=" * 80)

    # Create orchestrator with higher max_attempts
    orchestrator = create_orchestrator(
        scenario="self_heal_double_failure_test",
        metadata={
            "priority": "critical",
            "test_type": "regression_validation",
            "max_attempts": 5,  # Override to allow 3 attempts
        },
    )

    logger.info(
        "[TEST] Orchestrator configured: max_attempts=%d, timecapsule=%s",
        orchestrator.config.max_attempts,
        orchestrator.config.enable_timecapsule,
    )

    # Define workflow with double-flaky step
    steps = [
        {
            "name": "double_flaky_network_operation",
            "executor": double_flaky_executor,
            "url": "https://example.com",
            "notes": "Testing Self-Heal with TWO consecutive failures for diff generation",
            "allow_failure": False,
        },
    ]

    logger.info("[TEST] Running workflow with %d steps...", len(steps))

    # Run workflow
    result = await orchestrator.run_workflow_async(steps)

    logger.info("=" * 80)
    logger.info("Self-Heal Double Failure Scenario Test - Results")
    logger.info("=" * 80)
    logger.info("Overall Success: %s", result.success)
    logger.info("Completed Steps: %d / %d", result.metadata["completed_steps"], result.metadata["total_steps"])
    logger.info("Regression Queue: %s", result.regression_queue_path)

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
            if attempt.reset_report:
                logger.info("    Reset Report: ✓")
            if attempt.fixture_report:
                logger.info("    Fixture Report: ✓")
            if attempt.capsule_dir:
                logger.info("    Capsule Dir: %s", attempt.capsule_dir)
            if attempt.diff_path:
                logger.info("    Diff Path: %s", attempt.diff_path)

    # Export report
    report_path = Path("artifacts/auto_demo/self_heal/double_failure_test_report.json")
    orchestrator.export_report(report_path)
    logger.info("\n[TEST] Report exported to: %s", report_path)

    # Check if regression queue was created
    if result.regression_queue_path:
        queue_path = Path(result.regression_queue_path)
        if queue_path.exists():
            logger.info("[TEST] Regression queue file created: %s", queue_path)
            logger.info("[TEST] Queue size: %d bytes", queue_path.stat().st_size)
            # Show first few lines
            with queue_path.open("r") as f:
                lines = f.readlines()[:5]
                logger.info("[TEST] First %d entries:", len(lines))
                for line in lines:
                    logger.info("  %s", line.strip())
        else:
            logger.warning("[TEST] Regression queue path specified but file not found: %s", queue_path)
    else:
        logger.warning("[TEST] No regression queue path specified")

    logger.info("=" * 80)
    logger.info("Self-Heal Double Failure Scenario Test - Complete")
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
