#!/usr/bin/env python3
"""
Test EUI Console Interaction with Playwright
Sends messages to Console and captures responses
"""

from playwright.sync_api import sync_playwright
import time

def test_console_interaction():
    """Test Console → Echo Judgment Bridge interaction"""
    print("🧪 Testing EUI Console Interaction...")

    with sync_playwright() as p:
        # Launch browser
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()

        # Navigate to EUI
        print("  Navigating to http://localhost:3000...")
        page.goto("http://localhost:3000", wait_until="networkidle")
        print("✅ EUI loaded")

        # Wait for Console to be ready
        page.wait_for_selector('textarea', timeout=5000)
        print("✅ Console ready")

        # Test messages
        test_messages = [
            "안녕하세요 Echo!",
            "부산 금정구 노인 복지 정책이 어떤가요?",
            "AI 윤리 가이드라인에 대해 알려주세요"
        ]

        for i, message in enumerate(test_messages, 1):
            print(f"\n{'='*60}")
            print(f"Test {i}/{len(test_messages)}: {message}")
            print('-'*60)

            # Fill textarea
            textarea = page.locator('textarea')
            textarea.fill(message)
            print(f"  ✍️  Input filled: {message}")

            # Take screenshot before send
            page.screenshot(path=f"-heo123-heo123-heo123-heo123-heo123/EchoJudgmentSystem_v10-1/eui/console_before_{i}.png")

            # Click Send button
            send_button = page.locator('button:has-text("Send")')
            send_button.click()
            print("  📤 Send button clicked")

            # Wait for response (network request to complete)
            page.wait_for_timeout(2000)

            # Take screenshot after send
            page.screenshot(path=f"-heo123-heo123-heo123-heo123-heo123/EchoJudgmentSystem_v10-1/eui/console_after_{i}.png", full_page=True)
            print(f"  📸 Screenshots saved")

            # Try to extract response from page
            try:
                # Look for message elements (adjust selector based on actual DOM)
                messages = page.locator('[role="echo"], .message, .response').all()
                if messages:
                    print(f"  💬 Found {len(messages)} message elements")
                    for msg in messages[-3:]:  # Last 3 messages
                        text = msg.inner_text()
                        if text:
                            print(f"     → {text[:100]}...")
            except Exception as e:
                print(f"  ⚠️  Could not extract messages: {e}")

            # Wait before next message
            if i < len(test_messages):
                print("  ⏳ Waiting 3 seconds...")
                page.wait_for_timeout(3000)

        print(f"\n{'='*60}")
        print("✅ All tests completed!")
        print(f"📸 Screenshots saved in: -heo123-heo123-heo123-heo123-heo123/EchoJudgmentSystem_v10-1/eui/")
        print("   - console_before_*.png")
        print("   - console_after_*.png")

        # Keep browser open for manual inspection
        print("\n🖥️  Browser will stay open for 30 seconds for inspection...")
        page.wait_for_timeout(30000)

        browser.close()
        print("✅ Test complete")

if __name__ == "__main__":
    test_console_interaction()
