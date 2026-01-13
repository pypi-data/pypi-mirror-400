"""
Debug Runtime Tab - 실제 렌더링된 컨텐츠 확인
"""
import asyncio
from playwright.async_api import async_playwright

async def debug_runtime():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # Navigate to EUI
        await page.goto("http://localhost:3000", wait_until="domcontentloaded")
        await page.wait_for_timeout(3000)

        # Click Runtime Control tab
        print("Clicking Runtime Control tab...")
        await page.click("button:has-text('⚙️ Runtime Control')")
        await page.wait_for_timeout(6000)  # Wait for API data

        # Get all text content
        print("\n" + "="*70)
        print("Page Text Content:")
        print("="*70)
        text_content = await page.text_content("body")
        print(text_content[:2000])  # First 2000 characters

        # Get HTML structure
        print("\n" + "="*70)
        print("Runtime Control Panel HTML:")
        print("="*70)
        runtime_section = await page.query_selector("section")
        if runtime_section:
            html = await runtime_section.inner_html()
            print(html[:2000])  # First 2000 characters

        # Check for specific elements
        print("\n" + "="*70)
        print("Element Checks:")
        print("="*70)

        checks = [
            "💾 Memory",
            "🔥 CPU",
            "📊 Top Processes",
            "🎛️ System Control",
            "Loading runtime control",
            "Runtime Control Panel",
        ]

        for check in checks:
            count = await page.locator(f"text={check}").count()
            print(f"  {check}: {count} found")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(debug_runtime())
