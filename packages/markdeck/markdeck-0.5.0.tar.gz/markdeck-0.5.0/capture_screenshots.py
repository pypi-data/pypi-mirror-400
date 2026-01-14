#!/usr/bin/env python3
"""
Screenshot capture script for MarkDeck.
Captures screenshots of grid view feature and theme variations.
"""

import asyncio

from playwright.async_api import async_playwright


async def capture_screenshots():
    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": 1920, "height": 1080})

        # Navigate to presentation
        await page.goto("http://127.0.0.1:8888/")

        # Wait for slides to load
        await page.wait_for_selector(".slide-content", timeout=10000)
        await asyncio.sleep(2)

        # ===== Grid View Screenshots =====
        print("\n=== Capturing Grid View Screenshots ===")

        # Screenshot 1: Normal presentation view
        print("Capturing normal presentation view...")
        await page.screenshot(path="screenshots/01_normal_view.png")

        # Screenshot 2: Press 'O' to open grid view
        print("Opening grid overview...")
        await page.keyboard.press("o")
        await asyncio.sleep(1)
        await page.screenshot(path="screenshots/02_grid_overview.png")

        # Screenshot 3: Scroll down to see more slides in grid
        print("Capturing scrolled grid view...")
        await page.evaluate('document.querySelector(".grid-overlay").scrollTop = 300')
        await asyncio.sleep(0.5)
        await page.screenshot(path="screenshots/03_grid_scrolled.png")

        # Screenshot 4: Click on a slide to navigate
        print("Clicking on slide 3...")
        await page.evaluate('document.querySelector(".grid-overlay").scrollTop = 0')
        await asyncio.sleep(0.5)
        await page.click(".grid-slide:nth-child(3)")
        await asyncio.sleep(1)
        await page.screenshot(path="screenshots/04_after_navigation.png")

        # Screenshot 5: Open grid again to show current slide indicator
        print("Opening grid again to show current slide highlight...")
        await page.keyboard.press("o")
        await asyncio.sleep(1)
        await page.screenshot(path="screenshots/05_grid_current_highlight.png")

        # Close grid view before theme screenshots
        await page.keyboard.press("Escape")
        await asyncio.sleep(0.5)

        # ===== Theme Screenshots =====
        print("\n=== Capturing Theme Screenshots ===")

        # Screenshot 6: Dark theme (default)
        print("Capturing dark theme screenshot...")
        await page.screenshot(path="screenshots/theme_dark.png")

        # Screenshot 7: Switch to light theme
        print("Switching to light theme...")
        await page.keyboard.press("t")
        await asyncio.sleep(1)
        await page.screenshot(path="screenshots/theme_light.png")

        # Screenshot 8: Light theme with grid view
        print("Capturing light theme with grid view...")
        await page.keyboard.press("o")
        await asyncio.sleep(1)
        await page.screenshot(path="screenshots/theme_light_grid.png")

        # Screenshot 9: Dark theme with grid view
        print("Switching back to dark theme with grid...")
        await page.keyboard.press("Escape")
        await asyncio.sleep(0.5)
        # Press 't' twice to cycle: light -> beige -> dark
        await page.keyboard.press("t")
        await asyncio.sleep(0.5)
        await page.keyboard.press("t")
        await asyncio.sleep(1)
        await page.keyboard.press("o")
        await asyncio.sleep(1)
        await page.screenshot(path="screenshots/theme_dark_grid.png")

        # ===== Wide Slide Example Screenshot =====
        print("\n=== Capturing Wide Slide Example Screenshot ===")

        # Navigate back to beginning
        print("Navigating to wide slide example...")
        await page.goto("http://127.0.0.1:8888/")
        await page.wait_for_selector(".slide-content", timeout=10000)
        await asyncio.sleep(1)

        # Navigate to slide 11 (Wide Table Example)
        for i in range(11):
            await page.keyboard.press("ArrowRight")
            await asyncio.sleep(0.2)

        await asyncio.sleep(1)

        # Screenshot 10: Wide slide example
        print("Capturing wide slide example...")
        await page.screenshot(path="screenshots/wide_slide_example.png")

        # ===== Two-Column Layout Screenshots =====
        print("\n=== Capturing Two-Column Layout Screenshots ===")

        # Navigate back to features.md (already on port 8888)
        print("Navigating to two-column example slide...")
        await page.goto("http://127.0.0.1:8888/")
        await page.wait_for_selector(".slide-content", timeout=10000)
        await asyncio.sleep(1)

        # Navigate to slide 26 (Two-Column Example: Code & Explanation)
        for i in range(26):
            await page.keyboard.press("ArrowRight")
            await asyncio.sleep(0.2)

        await asyncio.sleep(1)

        # Screenshot 11: Two-column layout example
        print("Capturing two-column layout (Code & Explanation)...")
        await page.screenshot(path="screenshots/two_column_example.png")

        await browser.close()
        print("\n✅ All screenshots captured successfully!")
        print("\nScreenshots saved in: screenshots/")
        print("\nGrid View Screenshots:")
        print("  - 01_normal_view.png")
        print("  - 02_grid_overview.png")
        print("  - 03_grid_scrolled.png")
        print("  - 04_after_navigation.png")
        print("  - 05_grid_current_highlight.png")
        print("\nTheme Screenshots:")
        print("  - theme_dark.png")
        print("  - theme_light.png")
        print("  - theme_dark_grid.png")
        print("  - theme_light_grid.png")
        print("\nWide Slide Screenshots:")
        print("  - wide_slide_example.png")
        print("\nTwo-Column Layout Screenshots:")
        print("  - two_column_example.png")


if __name__ == "__main__":
    import os

    os.makedirs("screenshots", exist_ok=True)
    asyncio.run(capture_screenshots())
