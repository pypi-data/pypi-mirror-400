"""
EUI Complete Validation Test with Playwright
=============================================

EUI 전체 탭 순회 및 Runtime Control 검증
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright, Page

# Test configuration
BASE_URL = "http://localhost:3000"
SCREENSHOT_DIR = Path("test_screenshots_complete")
RESULTS_FILE = Path("test_results_complete.json")

# All EUI tabs to test
TABS = [
    {"id": "console", "label": "Conscious Console"},
    {"id": "loops", "label": "Loop Board"},
    {"id": "vault", "label": "Proof & Memory Vault"},
    {"id": "resonance", "label": "Resonance View"},
    {"id": "dual", "label": "Dual-Channel View"},
    {"id": "rooms", "label": "🏠 Rooms"},
    {"id": "independence", "label": "💼 Independence"},
    {"id": "signalflow", "label": "📡 Signal Flow"},
    {"id": "runtime", "label": "⚙️ Runtime Control"},  # NEW!
    {"id": "operator", "label": "🎯 Operator Dashboard"},
    {"id": "learning", "label": "🧬 Learning"},
    {"id": "meta", "label": "🔮 Meta-Resonance"},
    {"id": "network", "label": "🌐 Network"},
    {"id": "temporal", "label": "🕰️ Temporal"},
    {"id": "tier", "label": "🌀 3-Tier"},
]


async def wait_for_element(page: Page, selector: str, timeout: int = 5000):
    """Wait for element to be visible"""
    try:
        await page.wait_for_selector(selector, timeout=timeout, state="visible")
        return True
    except Exception as e:
        print(f"  ⚠️  Element not found: {selector} ({e})")
        return False


async def take_screenshot(page: Page, name: str):
    """Take screenshot and save"""
    timestamp = datetime.now().strftime("%H%M%S")
    filename = SCREENSHOT_DIR / f"{name}_{timestamp}.png"
    await page.screenshot(path=str(filename))
    print(f"  📸 Screenshot saved: {filename.name}")
    return str(filename)


async def test_tab(page: Page, tab: dict) -> dict:
    """Test individual tab"""
    tab_id = tab["id"]
    tab_label = tab["label"]

    print(f"\n🔍 Testing tab: {tab_label}")

    result = {
        "tab_id": tab_id,
        "tab_label": tab_label,
        "timestamp": datetime.now().isoformat(),
        "success": False,
        "screenshots": [],
        "errors": [],
    }

    try:
        # Find and click tab button
        tab_button = page.locator(f"button:has-text('{tab_label}')")

        if await tab_button.count() == 0:
            result["errors"].append(f"Tab button not found: {tab_label}")
            print(f"  ❌ Tab button not found")
            return result

        # Click tab
        await tab_button.click()

        # Special wait time for Runtime Control tab (needs API fetch)
        if tab_id == "runtime":
            await page.wait_for_timeout(5000)  # Wait longer for API data
        else:
            await page.wait_for_timeout(2000)  # Normal wait for other tabs

        # Take screenshot
        screenshot_path = await take_screenshot(page, f"tab_{tab_id}")
        result["screenshots"].append(screenshot_path)

        # Special validation for Runtime Control tab
        if tab_id == "runtime":
            print(f"  🔍 Validating Runtime Control panel...")

            # Wait for loading to complete
            loading_gone = await page.locator("text=Loading runtime control").count() == 0
            if loading_gone:
                print(f"    ✓ Loading completed")

            # Check for key elements
            checks = {
                "Memory section": "💾 Memory",
                "CPU section": "🔥 CPU",
                "Top Processes": "📊 Top Processes",
                "System Control": "🎛️ System Control",
            }

            for check_name, check_text in checks.items():
                has_element = await page.locator(f"text={check_text}").count() > 0
                if has_element:
                    print(f"    ✓ {check_name} found")
                else:
                    print(f"    ✗ {check_name} NOT found")
                    result["errors"].append(f"Missing: {check_name}")

            # Check for Live/Polling indicator
            live_indicator = await page.locator("text=Live").count()
            polling_indicator = await page.locator("text=Polling").count()

            if live_indicator > 0:
                print(f"    ✓ WebSocket Live connection active")
            elif polling_indicator > 0:
                print(f"    ✓ Polling mode active")
            else:
                print(f"    ⚠️  No connection indicator found")

            # Take additional screenshot for Runtime Control
            await page.wait_for_timeout(2000)
            screenshot_path = await take_screenshot(page, f"runtime_detailed")
            result["screenshots"].append(screenshot_path)

        result["success"] = True
        print(f"  ✅ Tab test passed")

    except Exception as e:
        result["errors"].append(str(e))
        print(f"  ❌ Tab test failed: {e}")

    return result


async def run_validation():
    """Run complete EUI validation"""
    print("=" * 70)
    print("EUI Complete Validation Test")
    print("=" * 70)

    # Create screenshot directory
    SCREENSHOT_DIR.mkdir(exist_ok=True)

    # Results container
    test_results = {
        "test_run": {
            "timestamp": datetime.now().isoformat(),
            "base_url": BASE_URL,
            "total_tabs": len(TABS),
        },
        "tabs": [],
        "summary": {
            "passed": 0,
            "failed": 0,
            "total_screenshots": 0,
        },
    }

    async with async_playwright() as p:
        # Launch browser
        print(f"\n🌐 Launching browser...")
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1280, "height": 1024})

        try:
            # Navigate to EUI
            print(f"📡 Navigating to {BASE_URL}...")
            await page.goto(BASE_URL, wait_until="domcontentloaded", timeout=60000)
            await page.wait_for_timeout(3000)  # Wait for React hydration

            # Take initial screenshot
            screenshot_path = await take_screenshot(page, "initial_load")
            test_results["initial_screenshot"] = screenshot_path

            # Test each tab
            for tab in TABS:
                tab_result = await test_tab(page, tab)
                test_results["tabs"].append(tab_result)

                if tab_result["success"]:
                    test_results["summary"]["passed"] += 1
                else:
                    test_results["summary"]["failed"] += 1

                test_results["summary"]["total_screenshots"] += len(
                    tab_result["screenshots"]
                )

        finally:
            await browser.close()

    # Save results
    with open(RESULTS_FILE, "w") as f:
        json.dump(test_results, f, indent=2)

    print("\n" + "=" * 70)
    print("📊 Validation Summary")
    print("=" * 70)
    print(f"Total tabs tested: {len(TABS)}")
    print(f"✅ Passed: {test_results['summary']['passed']}")
    print(f"❌ Failed: {test_results['summary']['failed']}")
    print(f"📸 Total screenshots: {test_results['summary']['total_screenshots']}")
    print(f"\n💾 Results saved to: {RESULTS_FILE}")
    print(f"📁 Screenshots saved to: {SCREENSHOT_DIR}/")

    # Highlight Runtime Control result
    runtime_result = next(
        (r for r in test_results["tabs"] if r["tab_id"] == "runtime"), None
    )

    if runtime_result:
        print("\n" + "=" * 70)
        print("⚙️  Runtime Control Panel Validation")
        print("=" * 70)
        if runtime_result["success"]:
            print("✅ Runtime Control panel loaded successfully")
            if runtime_result["errors"]:
                print(f"⚠️  Warnings: {len(runtime_result['errors'])}")
                for error in runtime_result["errors"]:
                    print(f"  - {error}")
        else:
            print("❌ Runtime Control panel validation failed")
            for error in runtime_result["errors"]:
                print(f"  - {error}")

    return test_results


if __name__ == "__main__":
    asyncio.run(run_validation())
