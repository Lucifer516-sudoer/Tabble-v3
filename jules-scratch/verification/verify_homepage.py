from playwright.sync_api import sync_playwright, expect

def run(playwright):
    browser = playwright.chromium.launch()
    page = browser.new_page()
    page.goto("http://localhost:8000/")

    # Wait for a plausible heading to appear on the page.
    # This ensures the SPA has finished its initial rendering.
    heading = page.get_by_role("heading", name="Welcome to Tabble")
    expect(heading).to_be_visible(timeout=10000) # Wait up to 10 seconds

    page.screenshot(path="jules-scratch/verification/homepage.png")
    browser.close()

with sync_playwright() as playwright:
    run(playwright)
