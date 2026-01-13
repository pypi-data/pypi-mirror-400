#!/usr/bin/env python3
"""
EUI Playwright Full Verification

Uses Playwright to automate full EUI verification with screenshots.

Version: 1.0
Author: Claude Code
"""

import asyncio
import json
from pathlib import Path
from datetime import datetime, timezone
from playwright.async_api import async_playwright


async def verify_eui_full():
    """Full EUI verification with Playwright automation."""

    print("=" * 80)
    print("EUI Playwright Full Verification")
    print("=" * 80)
    print()

    results = []
    screenshot_dir = Path("runtime/eui_screenshots")
    screenshot_dir.mkdir(parents=True, exist_ok=True)

    async with async_playwright() as p:
        # Launch browser
        print("🚀 Launching browser...")
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        try:
            # Step 1: Navigate to EUI
            print("\n1. Navigating to http://localhost:3000")
            await page.goto("http://localhost:3000", wait_until="networkidle", timeout=30000)

            screenshot_path = screenshot_dir / "01_landing_page.png"
            await page.screenshot(path=str(screenshot_path))
            print(f"   ✓ Screenshot saved: {screenshot_path}")

            # Check title
            title = await page.title()
            print(f"   Title: {title}")

            if "Echo" in title or "EUI" in title:
                results.append({"step": "Landing Page", "status": "PASS", "title": title})
            else:
                results.append({"step": "Landing Page", "status": "FAIL", "title": title})

            await asyncio.sleep(2)

            # Step 2: Check for main navigation
            print("\n2. Checking main navigation")
            try:
                # Look for navigation elements (adjust selectors based on actual UI)
                nav_elements = await page.query_selector_all("nav, [role='navigation']")
                print(f"   Found {len(nav_elements)} navigation elements")

                screenshot_path = screenshot_dir / "02_navigation.png"
                await page.screenshot(path=str(screenshot_path))

                if len(nav_elements) > 0:
                    results.append({"step": "Navigation", "status": "PASS", "count": len(nav_elements)})
                else:
                    results.append({"step": "Navigation", "status": "WARN", "count": 0})
            except Exception as e:
                results.append({"step": "Navigation", "status": "FAIL", "error": str(e)})

            await asyncio.sleep(2)

            # Step 3: Check for Multi-Agent panel
            print("\n3. Looking for Multi-Agent panel")
            try:
                # Try to find Multi-Agent text or button
                multi_agent_button = await page.query_selector("text=Multi-Agent") or \
                                   await page.query_selector("text=multi-agent") or \
                                   await page.query_selector("[data-testid='multi-agent']")

                if multi_agent_button:
                    print("   ✓ Multi-Agent panel found")
                    await multi_agent_button.click()
                    await asyncio.sleep(2)

                    screenshot_path = screenshot_dir / "03_multi_agent_panel.png"
                    await page.screenshot(path=str(screenshot_path))

                    results.append({"step": "Multi-Agent Panel", "status": "PASS"})
                else:
                    print("   ⚠ Multi-Agent panel not found (may need to navigate)")
                    screenshot_path = screenshot_dir / "03_no_multi_agent.png"
                    await page.screenshot(path=str(screenshot_path))
                    results.append({"step": "Multi-Agent Panel", "status": "WARN"})
            except Exception as e:
                results.append({"step": "Multi-Agent Panel", "status": "FAIL", "error": str(e)})

            await asyncio.sleep(2)

            # Step 4: Check console errors
            print("\n4. Checking console logs")
            console_errors = []

            def handle_console_msg(msg):
                if msg.type == "error":
                    console_errors.append(msg.text)

            page.on("console", handle_console_msg)

            # Wait a bit to capture console messages
            await asyncio.sleep(3)

            if console_errors:
                print(f"   ⚠ Found {len(console_errors)} console errors")
                for err in console_errors[:5]:  # Show first 5
                    print(f"     - {err}")
                results.append({"step": "Console Errors", "status": "WARN", "errors": console_errors})
            else:
                print("   ✓ No console errors")
                results.append({"step": "Console Errors", "status": "PASS"})

            # Step 5: Check API connectivity
            print("\n5. Checking API connectivity")
            try:
                # Navigate to API docs or test endpoint
                api_response = await page.goto("http://localhost:8000/docs", wait_until="networkidle", timeout=10000)

                screenshot_path = screenshot_dir / "05_api_docs.png"
                await page.screenshot(path=str(screenshot_path))

                if api_response.status == 200:
                    print("   ✓ Backend API accessible")
                    results.append({"step": "Backend API", "status": "PASS"})
                else:
                    print(f"   ✗ Backend API returned status {api_response.status}")
                    results.append({"step": "Backend API", "status": "FAIL", "status_code": api_response.status})
            except Exception as e:
                results.append({"step": "Backend API", "status": "FAIL", "error": str(e)})

            # Final screenshot
            screenshot_path = screenshot_dir / "06_final_state.png"
            await page.screenshot(path=str(screenshot_path), full_page=True)
            print(f"\n   Final screenshot: {screenshot_path}")

        except Exception as e:
            print(f"\n✗ Error during verification: {e}")
            results.append({"step": "Overall", "status": "FAIL", "error": str(e)})

        finally:
            # Keep browser open for manual inspection
            print("\n🔍 Browser kept open for manual inspection...")
            print("   Press Ctrl+C to close and complete verification...")

            try:
                await asyncio.sleep(300)  # Wait 5 minutes
            except KeyboardInterrupt:
                print("\n   Closing browser...")

            await browser.close()

    # Summary
    print("\n" + "=" * 80)
    print("Verification Summary")
    print("=" * 80)

    passed = sum(1 for r in results if r["status"] == "PASS")
    warned = sum(1 for r in results if r["status"] == "WARN")
    failed = sum(1 for r in results if r["status"] == "FAIL")

    for result in results:
        status_symbol = "✓" if result["status"] == "PASS" else ("⚠" if result["status"] == "WARN" else "✗")
        print(f"{status_symbol} {result['step']}: {result['status']}")
        if "error" in result:
            print(f"  Error: {result['error']}")

    print()
    print(f"Total: {len(results)} checks")
    print(f"Passed: {passed}")
    print(f"Warnings: {warned}")
    print(f"Failed: {failed}")
    print()

    # Save report
    report_path = Path("runtime/eui_playwright_verification.json")
    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "overall_status": "PASS" if failed == 0 else ("WARN" if warned > 0 else "FAIL"),
        "results": results,
        "summary": {
            "total": len(results),
            "passed": passed,
            "warned": warned,
            "failed": failed
        },
        "screenshots": [str(p) for p in screenshot_dir.glob("*.png")]
    }

    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)

    print(f"Report saved: {report_path}")
    print(f"Screenshots saved in: {screenshot_dir}")
    print()

    return failed == 0


if __name__ == "__main__":
    try:
        success = asyncio.run(verify_eui_full())
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\nVerification interrupted by user")
        exit(0)
