"""Configuration constants for Polecat."""

# Base URLs
BASE_URL = "https://learn.jbs.cam.ac.uk"
DASHBOARD_URL = f"{BASE_URL}/my/"

# Timezone
TIMEZONE = "Europe/London"

# Current term (hardcoded for now)
CURRENT_TERM = "Lent"

# Playwright settings
BROWSER_TIMEOUT_MS = 60_000  # 60 seconds for page loads
LOGIN_POLL_INTERVAL_MS = 2_000  # 2 seconds between login checks

# Output settings
ICS_FILENAME_TEMPLATE = "JBS_Calendar_{term}_{year}.ics"
