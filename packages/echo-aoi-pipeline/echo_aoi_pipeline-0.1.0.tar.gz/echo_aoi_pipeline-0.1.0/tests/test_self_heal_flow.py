#!/usr/bin/env python3
"""
Self-Heal Flow Test Script - MIGRATED TO EUE v1.0

Tests the complete Self-Heal workflow using EUE:
1. Execute with EUE (with self-heal enabled)
2. Automatic retry on failure
3. Generate timecapsule diffs
4. Update regression queue
5. Generate proof capsule

Migration Date: 2025-12-04
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

# EUE v1.0 Migration
from ops.eue import get_eue, EUEConfig, EUEMode

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


async def failing_step_executor():
    """
    Executor that navigates to example.com using EUE.

    Before (Old Way):
        - Created MCPPlaywrightBridge directly
        - Manual initialize, navigate, screenshot, cleanup

    After (New Way - EUE):
        - Use EUE integrated interface
        - Automatic proof collection
        - Built-in self-heal support
    """
    logger.info("[FailingExecutor] Attempting to execute...")

    # Use EUE instead of direct MCPPlaywrightBridge
    eue = get_eue(EUEConfig(scenario="failing_step_test"))

    try:
        # Navigate to test page
        result = await eue.navigate("https://example.com", with_cursor=True)

        if not result.success:
            raise Exception(f"Navigation failed: {result.error}")

        # Record timecapsule
        record_result = await eue.record_capsule(
            url="https://example.com",
            notes="Failing executor test"
        )

        logger.info("[FailingExecutor] Execution completed successfully")

        return {
            "screenshot": record_result.screenshot_path,
            "capsule": record_result.capsule_path,
            "success": True,
        }

    finally:
        await eue.cleanup()


async def successful_step_executor():
    """Simple executor that always succeeds."""
    logger.info("[SuccessfulExecutor] Executing...")
    await asyncio.sleep(0.5)
    return {"status": "success"}


async def main():
    """Run the complete Self-Heal flow test using EUE."""
    logger.info("=" * 80)
    logger.info("Self-Heal Flow Test - Starting (EUE v1.0)")
    logger.info("=" * 80)

    # EUE Configuration with Self-Heal enabled
    config = EUEConfig(
        scenario="self_heal_test",
        mode=EUEMode.SELF_HEAL,
        enable_self_heal=True,
        enable_timecapsule=True,
        enable_proof=True,
        enable_video=True,
        max_attempts=4
    )

    eue = get_eue(config)

    logger.info(
        "[TEST] EUE created with mode=%s, max_attempts=%d, timecapsule=%s",
        config.mode.value,
        config.max_attempts,
        config.enable_timecapsule,
    )

    # Define workflow steps
    steps = [
        {
            "name": "playwright_mcp_test",
            "executor": failing_step_executor,
            "url": "https://example.com",
            "notes": "Testing Playwright MCP integration with Self-Heal via EUE",
        },
        {
            "name": "verification_step",
            "executor": successful_step_executor,
            "notes": "Verification step",
        },
    ]

    logger.info("[TEST] Running workflow with %d steps...", len(steps))

    results = []
    total_attempts = 0

    try:
        # Run each step with EUE self-heal
        for step in steps:
            logger.info("\n" + "-" * 40)
            logger.info("Step: %s", step["name"])
            logger.info("-" * 40)

            if "url" in step:
                # Execute with self-heal
                result = await eue.execute_with_self_heal(
                    step_name=step["name"],
                    executor=step["executor"],
                    url=step["url"],
                    notes=step.get("notes")
                )
            else:
                # Execute directly (no URL needed)
                exec_result = await step["executor"]()
                # Wrap in EUEResult-like object
                result = type('Result', (), {
                    'success': exec_result.get('status') == 'success',
                    'attempts': 1,
                    'error': None,
                    'data': exec_result
                })()

            results.append(result)
            total_attempts += getattr(result, 'attempts', 1)

            logger.info("Step Result: %s", "SUCCESS" if result.success else "FAILED")
            logger.info("Attempts: %d", getattr(result, 'attempts', 1))

            if not result.success:
                logger.error("Step failed: %s", result.error if hasattr(result, 'error') else 'Unknown')
                break

        # Summary
        logger.info("\n" + "=" * 80)
        logger.info("Self-Heal Flow Test - Results (EUE v1.0)")
        logger.info("=" * 80)

        overall_success = all(r.success for r in results)
        logger.info("Overall Success: %s", overall_success)
        logger.info("Completed Steps: %d / %d", len(results), len(steps))
        logger.info("Total Attempts: %d", total_attempts)

        # Check for generated artifacts
        logger.info("\nArtifacts:")
        logger.info("  Timecapsules: artifacts/timecapsules/self_heal_test/")
        logger.info("  Videos: playwright_videos/")
        logger.info("  Proof: proof/eue/")

        return 0 if overall_success else 1

    except Exception as e:
        logger.error("Test failed with exception: %s", e, exc_info=True)
        return 1

    finally:
        await eue.cleanup()


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
