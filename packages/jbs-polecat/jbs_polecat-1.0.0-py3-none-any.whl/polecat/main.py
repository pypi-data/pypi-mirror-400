"""CLI orchestrator for Polecat."""

import re
from datetime import datetime, date
from playwright.sync_api import sync_playwright

from polecat.browser import launch_browser, create_page, wait_for_login, wait_for_term_selection
from polecat.scrapers import extract_courses, scrape_course_dates, ExtractedDate
from polecat.parsers import parse_extracted_date, merge_events, ParsedEvent
from polecat.calendar_gen import generate_ics
from polecat.config import CURRENT_TERM


# Event type patterns for categorization
DEADLINE_PATTERNS = [
    r"\b(exam|examination)\b",
    r"\b(assignment|submission)\b",
    r"\b(quiz|assessment)\b",
    r"\b(deadline|due)\b",
    r"\b(report|document)\b",
    r"\b(consent\s*form)\b",
]

UNIT_RELEASE_PATTERNS = [
    r"^(module\s+overview|unit\s+\d+)",
    r"live\s+session",
]


def is_deadline_event(event: ParsedEvent) -> bool:
    """
    Check if an event is a deadline (exam, assignment, quiz, submission).

    Args:
        event: The event to check

    Returns:
        True if this is a deadline event
    """
    title_lower = event.title.lower()

    # Check if it matches deadline patterns
    for pattern in DEADLINE_PATTERNS:
        if re.search(pattern, title_lower, re.IGNORECASE):
            return True

    # Events from assignment source are always deadlines
    if event.source == "assignment":
        return True

    return False


def is_opens_event(event: ParsedEvent) -> bool:
    """
    Check if an event is an "Opens" event (not a deadline).

    Args:
        event: The event to check

    Returns:
        True if this is an "Opens" event
    """
    return "- Opens" in event.title or "Opens" in event.title


def is_quiz_event(event: ParsedEvent) -> bool:
    """
    Check if an event is a quiz/assessment (these should always be included).

    Quiz events include both "Quiz Opens" and "Quiz Closes" dates.

    Args:
        event: The event to check

    Returns:
        True if this is a quiz event
    """
    title_lower = event.title.lower()

    # Check title for quiz patterns
    if re.search(r"\b(quiz|open\s*book\s*assessment)\b", title_lower, re.IGNORECASE):
        return True

    # Check notes for quiz indicator
    if event.notes and "open book assessment" in event.notes.lower():
        return True

    return False


def filter_events(
    events: list[ParsedEvent],
    include_unit_releases: bool = False,
    include_opens: bool = False,
) -> list[ParsedEvent]:
    """
    Filter events based on user preferences.

    Default behavior:
    - Include all deadlines (exams, assignments, submissions, quizzes)
    - Include quiz Opens dates (they're time-sensitive)
    - Exclude unit release dates
    - Exclude non-quiz "Opens" dates

    Args:
        events: All parsed events
        include_unit_releases: If True, include unit release dates
        include_opens: If True, include all "Opens" dates

    Returns:
        Filtered list of events
    """
    filtered = []

    for event in events:
        # Always include quiz events (both Opens and Due)
        if is_quiz_event(event):
            filtered.append(event)
            continue

        # Check if it's an "Opens" event
        if is_opens_event(event):
            if include_opens:
                filtered.append(event)
            continue

        # Check if it's a deadline event
        if is_deadline_event(event):
            filtered.append(event)
            continue

        # It's likely a unit release or live session
        if include_unit_releases:
            filtered.append(event)

    return filtered


def get_filter_preferences() -> tuple[bool, bool]:
    """
    Ask user for filtering preferences.

    Returns:
        Tuple of (include_unit_releases, include_opens)
    """
    print()
    print("=" * 60)
    print("CALENDAR OPTIONS")
    print("=" * 60)
    print()
    print("By default, only important dates are saved to the calendar:")
    print("  - Exams and quizzes (including Opens dates for quizzes)")
    print("  - Assignment/submission deadlines (Due dates)")
    print()

    # Ask about Opens dates
    include_opens = False
    while True:
        response = input("Include assignment 'Opens' dates? (y/n) [n]: ").strip().lower()
        if response in ("", "n", "no"):
            include_opens = False
            break
        elif response in ("y", "yes"):
            include_opens = True
            break
        else:
            print("Please enter 'y' or 'n'")

    # Ask about unit releases
    include_unit_releases = False
    while True:
        response = input("Include unit releases and live sessions? (y/n) [n]: ").strip().lower()
        if response in ("", "n", "no"):
            include_unit_releases = False
            break
        elif response in ("y", "yes"):
            include_unit_releases = True
            break
        else:
            print("Please enter 'y' or 'n'")

    return include_unit_releases, include_opens


def print_banner() -> None:
    """Print the Polecat banner."""
    print()
    print("=" * 60)
    print("  POLECAT - JBS Learning Platform Calendar Generator")
    print(f"  Term: {CURRENT_TERM}")
    print("=" * 60)
    print()


def print_summary_table(events: list[ParsedEvent]) -> None:
    """
    Print a compact summary table of events for user verification.

    Args:
        events: List of ParsedEvent objects sorted by date
    """
    if not events:
        print("No events found.")
        return

    print()
    print("-" * 80)
    print(f"{'Date':<20} {'Course':<25} {'Event':<20} {'Source':<10}")
    print("-" * 80)

    for event in events:
        # Format date
        if isinstance(event.start_dt, datetime):
            date_str = event.start_dt.strftime("%Y-%m-%d %H:%M")
        else:
            date_str = event.start_dt.strftime("%Y-%m-%d") + " (all day)"

        # Truncate long names
        course = event.course_name[:23] + ".." if len(event.course_name) > 25 else event.course_name
        title = event.title[:18] + ".." if len(event.title) > 20 else event.title

        # Source indicator
        source = f"[{event.source}]"
        if event.conflict:
            source += " ⚠️"

        print(f"{date_str:<20} {course:<25} {title:<20} {source:<10}")

    print("-" * 80)
    print(f"Total: {len(events)} event(s)")

    # Show conflict warning if any
    conflicts = [e for e in events if e.conflict]
    if conflicts:
        print()
        print(f"⚠️  {len(conflicts)} event(s) had conflicts between sources (Source B prioritized)")

    print()


def get_user_confirmation() -> bool:
    """
    Ask user to confirm the extracted dates.

    Returns:
        True if user confirms, False otherwise
    """
    while True:
        response = input("Do these dates look correct? (y/n): ").strip().lower()
        if response in ("y", "yes"):
            return True
        elif response in ("n", "no"):
            return False
        else:
            print("Please enter 'y' or 'n'")


def run() -> None:
    """Main entry point for Polecat."""
    print_banner()

    with sync_playwright() as playwright:
        # Launch browser
        print("Launching browser...")
        browser = launch_browser(playwright)
        page = create_page(browser)

        try:
            # Step 1: Wait for SSO login
            wait_for_login(page)

            # Step 2: Wait for term selection
            wait_for_term_selection(page)

            # Step 3: Discover courses
            print()
            print("Discovering courses...")
            courses = extract_courses(page)

            if not courses:
                print("ERROR: No courses found. Exiting.")
                return

            print(f"Found {len(courses)} course(s):")
            for course in courses:
                print(f"  - {course.name}")

            # Step 4: Extract dates from each course
            print()
            print("Extracting dates from courses...")
            all_extracted: list[ExtractedDate] = []

            for course in courses:
                extracted = scrape_course_dates(page, course)
                all_extracted.extend(extracted)

            if not all_extracted:
                print()
                print("WARNING: No dates found in any course.")
                print("The page structure may have changed, or there are no key dates for this term.")
                return

            # Step 5: Parse and merge events
            print()
            print("Parsing dates...")
            all_events: list[ParsedEvent] = []

            for extracted in all_extracted:
                parsed = parse_extracted_date(extracted)
                all_events.extend(parsed)

            if not all_events:
                print("WARNING: Could not parse any dates from the extracted content.")
                return

            # Merge and deduplicate
            merged_events = merge_events(all_events)

            # Step 6: Show summary and ask for confirmation
            print_summary_table(merged_events)

            if not get_user_confirmation():
                print("Cancelled. No calendar file generated.")
                return

            # Step 7: Get filter preferences
            include_unit_releases, include_opens = get_filter_preferences()

            # Step 8: Filter events
            filtered_events = filter_events(
                merged_events,
                include_unit_releases=include_unit_releases,
                include_opens=include_opens,
            )

            print()
            print(f"Filtered: {len(filtered_events)} event(s) will be saved to calendar")
            print(f"  (excluded {len(merged_events) - len(filtered_events)} unit releases/opens dates)")

            if not filtered_events:
                print()
                print("WARNING: No events to save after filtering.")
                return

            # Step 9: Generate ICS file
            print()
            print("Generating calendar...")
            filepath = generate_ics(filtered_events)

            print()
            print("=" * 60)
            print("SUCCESS! Calendar file created:")
            print()
            print(f"  {filepath.absolute()}")
            print()
            print("You can import this file into Google Calendar, Outlook,")
            print("Apple Calendar, or any other calendar application.")
            print("=" * 60)
            print()

        finally:
            # Clean up
            browser.close()


def main() -> None:
    """Entry point with error handling."""
    try:
        run()
    except KeyboardInterrupt:
        print("\n\nCancelled by user.")
    except Exception as e:
        print(f"\nERROR: {e}")
        print("If this persists, please check the page structure or report the issue.")
        raise


if __name__ == "__main__":
    main()
