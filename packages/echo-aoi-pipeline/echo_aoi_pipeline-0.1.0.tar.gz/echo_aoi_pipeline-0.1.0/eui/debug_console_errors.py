"""
Debug Console Errors - 브라우저 콘솔 에러 확인
"""
import asyncio
from playwright.async_api import async_playwright

async def debug_console():
    errors = []
    warnings = []
    logs = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # Capture console messages
        page.on("console", lambda msg: logs.append(f"{msg.type}: {msg.text}"))
        page.on("pageerror", lambda err: errors.append(str(err)))

        # Navigate to EUI
        print("Navigating to EUI...")
        await page.goto("http://localhost:3000", wait_until="domcontentloaded")
        await page.wait_for_timeout(3000)

        # Click Runtime Control tab
        print("Clicking Runtime Control tab...")
        try:
            await page.click("button:has-text('⚙️ Runtime Control')", timeout=5000)
            await page.wait_for_timeout(6000)
        except Exception as e:
            print(f"Error clicking: {e}")

        # Print collected logs
        print("\n" + "="*70)
        print("Console Logs:")
        print("="*70)
        for log in logs:
            print(f"  {log}")

        print("\n" + "="*70)
        print("Page Errors:")
        print("="*70)
        for err in errors:
            print(f"  {err}")

        # Check network requests
        print("\n" + "="*70)
        print("Checking API accessibility from browser:")
        print("="*70)

        # Try to fetch from the API
        try:
            response = await page.evaluate("""
                async () => {
                    try {
                        const res = await fetch('http://localhost:8510/api/runtime/status');
                        return {
                            status: res.status,
                            ok: res.ok,
                            data: await res.json()
                        };
                    } catch (error) {
                        return { error: error.message };
                    }
                }
            """)
            print(f"  API fetch result: {response}")
        except Exception as e:
            print(f"  API fetch error: {e}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(debug_console())
