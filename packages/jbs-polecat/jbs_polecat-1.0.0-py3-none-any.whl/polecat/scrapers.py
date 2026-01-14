"""BeautifulSoup scrapers for extracting course and date information.

See docs/dev/SITE_STRUCTURE.md for details on the JBS Moodle site layout.

CRITICAL: Dates must be extracted from TWO sources:
1. Key Dates table (if exists) - may have quizzes/exams not on assignment pages
2. Assignment pages (all courses) - Opens/Due dates

If conflicts: prioritize Assignment pages, but flag for user.
"""

import re
from dataclasses import dataclass
from typing import Optional

from bs4 import BeautifulSoup
from playwright.sync_api import Page

from polecat.config import BASE_URL


@dataclass
class Course:
    """Represents a course extracted from the dashboard."""

    name: str
    url: str


@dataclass
class ExtractedDate:
    """Represents a date extracted from a course page."""

    course_name: str
    title: str  # e.g., "Assignment Due", "Unit 1 Release"
    date_text: str  # Raw date text before parsing
    source: str  # "key_dates" or "assignment"
    url: Optional[str] = None  # Deep link
    notes: Optional[str] = None  # Any additional context


# Date pattern for extraction from Key Dates table
DATE_PATTERN = re.compile(
    r'\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}',
    re.IGNORECASE
)


def clean_title(text: str) -> str:
    """
    Clean up title text from scraped content.

    Fixes common issues:
    - Missing space after colon (e.g., "Unit 2:Creating" -> "Unit 2: Creating")
    - Multiple spaces
    - Leading/trailing whitespace

    Args:
        text: Raw title text

    Returns:
        Cleaned title text
    """
    if not text:
        return text

    # Add space after colon if missing (but not for time patterns like "9:00")
    text = re.sub(r':([A-Za-z])', r': \1', text)

    # Normalize multiple spaces to single space
    text = re.sub(r'\s+', ' ', text)

    # Strip leading/trailing whitespace
    text = text.strip()

    return text


def extract_courses(page: Page) -> list[Course]:
    """
    Extract all visible course cards from the dashboard.

    Args:
        page: Playwright page object on the dashboard

    Returns:
        List of Course objects with name and URL
    """
    html = page.content()
    soup = BeautifulSoup(html, "html.parser")

    courses: list[Course] = []

    # Moodle typically uses course cards or course list items
    # Try multiple selector strategies for resilience
    course_links = soup.select(
        ".coursebox a.aalink, "  # Classic Moodle
        ".course-card a, "  # Card-based theme
        "[data-region='course-content'] a, "  # Modern Moodle
        ".course-listitem a.aalink"  # List view
    )

    seen_urls: set[str] = set()

    for link in course_links:
        href = link.get("href", "")
        name = link.get_text(strip=True)

        # Skip empty or duplicate entries
        if not href or not name or href in seen_urls:
            continue

        # Only include actual course links
        if "/course/view.php" not in href:
            continue

        # Normalize URL
        if href.startswith("/"):
            href = BASE_URL + href

        seen_urls.add(href)
        courses.append(Course(name=name, url=href))

    if not courses:
        print("WARNING: No courses found on dashboard.")
        print("  - Make sure you've selected the correct term filter")
        print("  - The page structure may have changed")

    return courses


def find_key_dates_link(soup: BeautifulSoup) -> Optional[str]:
    """
    Find the Key Dates link on a course page.

    Args:
        soup: BeautifulSoup object of course page

    Returns:
        URL to Key Dates page, or None if not found
    """
    for link in soup.find_all("a"):
        text = link.get_text(strip=True).lower()
        if text == "key dates":
            href = link.get("href", "")
            if href:
                if href.startswith("/"):
                    href = BASE_URL + href
                return href
    return None


def extract_key_dates(page: Page, course: Course) -> list[ExtractedDate]:
    """
    Extract dates from the Key Dates table (if it exists).

    Key Dates table format (5 columns):
    - Column 1: Unit/Activity name
    - Column 2: Unit release date
    - Column 3: Live session date (often "w/c" or "N/A")
    - Column 4: Online open book assessment (quiz) opens
    - Column 5: Online open book assessment (quiz) closes

    Args:
        page: Playwright page on course page
        course: The course being scraped

    Returns:
        List of ExtractedDate objects from Key Dates table
    """
    html = page.content()
    soup = BeautifulSoup(html, "html.parser")

    # Find Key Dates link
    key_dates_url = find_key_dates_link(soup)

    if not key_dates_url:
        return []  # No Key Dates for this course

    print(f"    Found Key Dates page")

    # Navigate to Key Dates page
    page.goto(key_dates_url)
    page.wait_for_load_state("networkidle")

    kd_html = page.content()
    kd_soup = BeautifulSoup(kd_html, "html.parser")

    dates: list[ExtractedDate] = []

    # Pattern for quiz dates like "09.00am 5 January 2026" or "09:00am 5 January 2026"
    QUIZ_DATE_PATTERN = re.compile(
        r'(\d{1,2}[.:]\d{2}\s*(?:am|pm)?\s*\d{1,2}\s+\w+\s+\d{4})',
        re.IGNORECASE
    )

    # Find all tables
    tables = kd_soup.find_all("table")

    for table in tables:
        rows = table.find_all("tr")

        # Skip header row
        for row in rows[1:]:
            cells = row.find_all(["td", "th"])

            if len(cells) >= 2:
                activity_name = cells[0].get_text(strip=True)
                date_cell = cells[1].get_text(strip=True)

                # Skip rows that don't have actual dates
                if not activity_name or not date_cell:
                    continue

                # Skip header-like rows
                if date_cell.lower() in ["date", "submission date", "release date", "assessment submission date", "unit release date"]:
                    continue

                # Extract date from cell (column 2 - unit release)
                date_match = DATE_PATTERN.search(date_cell)
                if date_match:
                    dates.append(
                        ExtractedDate(
                            course_name=course.name,
                            title=clean_title(activity_name),
                            date_text=date_match.group(0),
                            source="key_dates",
                            url=key_dates_url,
                        )
                    )

            # Column 3: Live session dates (w/c format)
            if len(cells) >= 3:
                activity_name = cells[0].get_text(strip=True)
                live_session = cells[2].get_text(strip=True)

                # Extract "w/c" dates (week commencing)
                wc_match = re.search(r'w/c\s*(\d{1,2}\s+\w+\s+\d{4})', live_session, re.IGNORECASE)
                if wc_match:
                    dates.append(
                        ExtractedDate(
                            course_name=course.name,
                            title=clean_title(f"{activity_name} - Live Session"),
                            date_text=wc_match.group(1),
                            source="key_dates",
                            url=key_dates_url,
                            notes="Week commencing",
                        )
                    )

            # Column 4: Quiz opens dates
            if len(cells) >= 4:
                activity_name = cells[0].get_text(strip=True)
                quiz_opens = cells[3].get_text(strip=True)

                # Skip N/A or empty
                if quiz_opens and quiz_opens.lower() not in ["n/a", ""]:
                    quiz_match = QUIZ_DATE_PATTERN.search(quiz_opens)
                    if quiz_match:
                        # Normalize the date format (09.00am -> 09:00am)
                        quiz_date = quiz_match.group(1).replace(".", ":")
                        dates.append(
                            ExtractedDate(
                                course_name=course.name,
                                title=clean_title(f"{activity_name} - Quiz Opens"),
                                date_text=quiz_date,
                                source="key_dates",
                                url=key_dates_url,
                                notes="Online open book assessment",
                            )
                        )

            # Column 5: Quiz closes dates
            if len(cells) >= 5:
                activity_name = cells[0].get_text(strip=True)
                quiz_closes = cells[4].get_text(strip=True)

                # Skip N/A or empty
                if quiz_closes and quiz_closes.lower() not in ["n/a", ""]:
                    quiz_match = QUIZ_DATE_PATTERN.search(quiz_closes)
                    if quiz_match:
                        # Normalize the date format (09.00am -> 09:00am)
                        quiz_date = quiz_match.group(1).replace(".", ":")
                        dates.append(
                            ExtractedDate(
                                course_name=course.name,
                                title=clean_title(f"{activity_name} - Quiz Closes"),
                                date_text=quiz_date,
                                source="key_dates",
                                url=key_dates_url,
                                notes="Online open book assessment deadline",
                            )
                        )

    return dates


def find_assignment_links(soup: BeautifulSoup) -> list[tuple[str, str]]:
    """
    Find all assignment links on a course page.

    Args:
        soup: BeautifulSoup object of course page

    Returns:
        List of (assignment_name, assignment_url) tuples
    """
    assignments: list[tuple[str, str]] = []
    seen_urls: set[str] = set()

    # Find all links to assignment pages
    assign_links = soup.find_all("a", href=lambda h: h and "/mod/assign/" in h)

    for link in assign_links:
        href = link.get("href", "")
        name = link.get_text(strip=True)

        # Skip duplicates and empty
        if not href or not name or href in seen_urls:
            continue

        # Normalize URL
        if href.startswith("/"):
            href = BASE_URL + href

        seen_urls.add(href)
        assignments.append((name, href))

    return assignments


def extract_dates_near_assignment_link(soup: BeautifulSoup, course: Course, assignment_name: str, assignment_url: str) -> list[ExtractedDate]:
    """
    Extract dates shown on the course page near an assignment link.

    On some pages, dates like "Opens: Monday, 12 January 2026, 9:00 AM" appear
    right below or near the assignment link (e.g., on section pages).

    Args:
        soup: BeautifulSoup object of course page
        course: The parent course
        assignment_name: Name of the assignment
        assignment_url: URL of the assignment page

    Returns:
        List of ExtractedDate objects found near the link
    """
    dates: list[ExtractedDate] = []

    # Find the assignment link element
    assign_link = soup.find("a", href=lambda h: h and assignment_url.replace(BASE_URL, "") in h)

    if not assign_link:
        return dates

    # Look in the parent activity/module container for dates
    # Moodle typically wraps activities in li.activity or div.activityinstance
    parent = assign_link.find_parent(["li", "div"], class_=lambda c: c and ("activity" in c or "activityinstance" in c or "modtype" in c))

    if parent:
        text = parent.get_text(separator=" ", strip=True)
    else:
        # Fallback: look at siblings and parent container
        container = assign_link.find_parent(["li", "div"])
        if container:
            text = container.get_text(separator=" ", strip=True)
        else:
            return dates

    # Flexible date pattern: day name (optional), day number, month name, year, time (optional)
    date_pattern = r"(?:[A-Za-z]+,?\s+)?(\d{1,2}\s+[A-Za-z]+\s+\d{4})(?:[,\s]+(\d{1,2}:\d{2}\s*(?:AM|PM)))?"

    # Extract "Opens:" date
    opens_match = re.search(r"Opens:\s*" + date_pattern, text, re.IGNORECASE)
    if opens_match:
        date_str = opens_match.group(1)
        time_str = opens_match.group(2)
        full_date = f"{date_str}, {time_str}" if time_str else date_str
        dates.append(
            ExtractedDate(
                course_name=course.name,
                title=f"{assignment_name} - Opens",
                date_text=full_date.strip(),
                source="assignment",
                url=assignment_url,
            )
        )

    # Extract "Due:" date
    due_match = re.search(r"Due:\s*" + date_pattern, text, re.IGNORECASE)
    if due_match:
        date_str = due_match.group(1)
        time_str = due_match.group(2)
        full_date = f"{date_str}, {time_str}" if time_str else date_str
        dates.append(
            ExtractedDate(
                course_name=course.name,
                title=f"{assignment_name} - Due",
                date_text=full_date.strip(),
                source="assignment",
                url=assignment_url,
            )
        )

    return dates


def extract_assignment_dates(page: Page, course: Course, assignment_name: str, assignment_url: str) -> list[ExtractedDate]:
    """
    Extract Opens and Due dates from an assignment page.

    The dates are found near the top of the page or in completion requirements:
    - Opens: Monday, 12 January 2026, 9:00 AM
    - Due: Friday, 6 March 2026, 9:00 AM

    Args:
        page: Playwright page object
        course: The parent course
        assignment_name: Name of the assignment
        assignment_url: URL of the assignment page

    Returns:
        List of ExtractedDate objects (typically 1-2: opens and due dates)
    """
    dates: list[ExtractedDate] = []

    # Navigate to assignment page
    page.goto(assignment_url)
    page.wait_for_load_state("networkidle")

    html = page.content()
    soup = BeautifulSoup(html, "html.parser")

    # Get the full page text for searching
    text = soup.get_text(separator=" ", strip=True)

    # More flexible regex patterns for date extraction
    # Pattern captures: day name (optional), day number, month name, year, time (optional)
    # Examples:
    #   "Monday, 12 January 2026, 9:00 AM"
    #   "12 January 2026, 9:00 AM"
    #   "Friday, 6 March 2026, 9:00 AM"
    date_pattern = r"(?:[A-Za-z]+,?\s+)?(\d{1,2}\s+[A-Za-z]+\s+\d{4})(?:[,\s]+(\d{1,2}:\d{2}\s*(?:AM|PM)))?"

    # Extract "Opens:" date
    opens_match = re.search(r"Opens:\s*" + date_pattern, text, re.IGNORECASE)
    if opens_match:
        date_str = opens_match.group(1)
        time_str = opens_match.group(2)
        full_date = f"{date_str}, {time_str}" if time_str else date_str
        dates.append(
            ExtractedDate(
                course_name=course.name,
                title=f"{assignment_name} - Opens",
                date_text=full_date.strip(),
                source="assignment",
                url=assignment_url,
            )
        )

    # Extract "Due:" date
    due_match = re.search(r"Due:\s*" + date_pattern, text, re.IGNORECASE)
    if due_match:
        date_str = due_match.group(1)
        time_str = due_match.group(2)
        full_date = f"{date_str}, {time_str}" if time_str else date_str
        dates.append(
            ExtractedDate(
                course_name=course.name,
                title=f"{assignment_name} - Due",
                date_text=full_date.strip(),
                source="assignment",
                url=assignment_url,
            )
        )

    return dates


def scrape_course_dates(page: Page, course: Course) -> list[ExtractedDate]:
    """
    Navigate to a course page and extract dates from BOTH sources:
    1. Key Dates table (if exists)
    2. Assignment links (course page first, then individual pages as fallback)

    Args:
        page: Playwright page object
        course: The course to scrape

    Returns:
        List of ExtractedDate objects from all sources
    """
    print(f"  Scraping: {course.name}")

    # Navigate to the course page
    page.goto(course.url)
    page.wait_for_load_state("networkidle")

    all_dates: list[ExtractedDate] = []

    # === SOURCE 1: Key Dates table ===
    key_dates = extract_key_dates(page, course)
    if key_dates:
        print(f"    Key Dates: {len(key_dates)} date(s)")
        all_dates.extend(key_dates)
    else:
        print(f"    Key Dates: not found for this course")

    # Navigate back to course page for assignment extraction
    page.goto(course.url)
    page.wait_for_load_state("networkidle")

    # === SOURCE 2: Assignment dates ===
    html = page.content()
    soup = BeautifulSoup(html, "html.parser")
    assignments = find_assignment_links(soup)

    if assignments:
        print(f"    Assignments: {len(assignments)} found")
        for assign_name, assign_url in assignments:
            # First try: extract dates from course page near the assignment link
            dates = extract_dates_near_assignment_link(soup, course, assign_name, assign_url)

            # Fallback: if no dates found on course page, check individual assignment page
            if not dates:
                dates = extract_assignment_dates(page, course, assign_name, assign_url)
                # Navigate back to course page for next iteration
                page.goto(course.url)
                page.wait_for_load_state("networkidle")
                html = page.content()
                soup = BeautifulSoup(html, "html.parser")

            all_dates.extend(dates)

            if dates:
                print(f"      - {assign_name}: {len(dates)} date(s)")
            else:
                print(f"      - {assign_name}: no dates found")
    else:
        print(f"    Assignments: none found")

    if not all_dates:
        print(f"    WARNING: No dates found from any source for {course.name}")

    return all_dates
