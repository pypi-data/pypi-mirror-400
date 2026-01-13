#!/usr/bin/env python3
"""
Open EUI in Playwright Browser
Opens http://localhost:3000 in a Chromium browser window
"""

from playwright.sync_api import sync_playwright
import time

def open_eui_browser():
    """Open EUI in Playwright browser"""
    print("🌐 Opening EUI in Playwright browser...")

    with sync_playwright() as p:
        # Launch browser (headless=False to show window)
        print("  Launching Chromium browser...")
        browser = p.chromium.launch(headless=False, args=['--start-maximized'])

        # Create context and page
        context = browser.new_context(viewport=None)
        page = context.new_page()

        # Navigate to EUI
        print("  Navigating to http://localhost:3000...")
        try:
            page.goto("http://localhost:3000", wait_until="networkidle", timeout=10000)
            print("✅ EUI loaded successfully!")

            # Take screenshot
            screenshot_path = "-heo123-heo123-heo123-heo123-heo123/EchoJudgmentSystem_v10-1/eui/eui_screenshot.png"
            page.screenshot(path=screenshot_path, full_page=True)
            print(f"📸 Screenshot saved: {screenshot_path}")

            # Get page title
            title = page.title()
            print(f"📄 Page title: {title}")

            # Print console messages
            page.on("console", lambda msg: print(f"  [Browser Console] {msg.text}"))

            # Wait for user to close browser
            print("\n🖥️  Browser window opened!")
            print("   Close the browser window to exit this script.")
            print("   Or press Ctrl+C here to close programmatically.")

            # Keep browser open (wait for manual close or timeout)
            try:
                page.wait_for_timeout(300000)  # 5 minutes max
            except KeyboardInterrupt:
                print("\n⚠️  Closing browser...")

        except Exception as e:
            print(f"❌ Error loading EUI: {e}")
            print("   Make sure EUI is running at http://localhost:3000")
            print("   Run: ./run_eui.sh")

        finally:
            browser.close()
            print("✅ Browser closed.")

if __name__ == "__main__":
    open_eui_browser()
