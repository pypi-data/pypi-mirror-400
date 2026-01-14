"""Playwright browser setup and login handling."""

from playwright.sync_api import sync_playwright, Browser, Page, Playwright

from polecat.config import DASHBOARD_URL, BROWSER_TIMEOUT_MS


def launch_browser(playwright: Playwright) -> Browser:
    """Launch a headful Chromium browser instance."""
    return playwright.chromium.launch(headless=False)


def wait_for_login(page: Page) -> None:
    """
    Navigate to dashboard and wait for user to complete SSO login.

    The user must manually complete the SSO authentication in the browser.
    This function blocks until the dashboard URL is reached.
    """
    print(f"Opening {DASHBOARD_URL}")
    print("Please complete SSO login in the browser window...")
    print()

    page.goto(DASHBOARD_URL, timeout=BROWSER_TIMEOUT_MS)

    # Wait for the dashboard to be reachable (SSO complete)
    # The URL should contain /my/ after successful login
    page.wait_for_url("**/my/**", timeout=300_000)  # 5 min timeout for SSO

    print("Login successful! Dashboard loaded.")


def wait_for_term_selection(page: Page) -> None:
    """
    Prompt user to select the term from the dropdown in the browser.

    Waits for user confirmation in the terminal before proceeding.
    """
    print()
    print("=" * 60)
    print("ACTION REQUIRED:")
    print("  1. In the browser, find the term/course filter dropdown")
    print("  2. Select 'Lent' (or the current term)")
    print("  3. Wait for the page to update with filtered courses")
    print("=" * 60)
    print()

    input("Press Enter here once you've selected the term and courses are visible...")

    # Give the page a moment to settle after any dynamic updates
    page.wait_for_load_state("networkidle", timeout=BROWSER_TIMEOUT_MS)

    print("Term selection confirmed. Proceeding with course discovery...")


def create_page(browser: Browser) -> Page:
    """Create a new browser page with default settings."""
    context = browser.new_context()
    page = context.new_page()
    page.set_default_timeout(BROWSER_TIMEOUT_MS)
    return page
