"""Date and text parsing utilities."""

import re
from dataclasses import dataclass
from datetime import datetime, date
from typing import Optional

import dateparser

from polecat.config import TIMEZONE


@dataclass
class ParsedEvent:
    """A normalized calendar event ready for ICS generation."""

    course_name: str
    title: str
    start_dt: datetime | date
    end_dt: Optional[datetime | date] = None
    all_day: bool = False
    source: str = ""  # "assignment" or "key_dates"
    url: Optional[str] = None
    notes: Optional[str] = None
    conflict: bool = False  # True if this conflicts with another source


# Common date patterns in academic contexts
DATE_PATTERNS = [
    # "Monday 10 February 2025 at 14:00"
    r"(\w+day\s+\d{1,2}\s+\w+\s+\d{4}(?:\s+at\s+\d{1,2}[:.]\d{2})?)",
    # "10 February 2025, 2:00 PM"
    r"(\d{1,2}\s+\w+\s+\d{4}(?:[,\s]+\d{1,2}[:.]\d{2}\s*(?:AM|PM|am|pm))?)",
    # "10/02/2025 14:00"
    r"(\d{1,2}/\d{1,2}/\d{4}(?:\s+\d{1,2}[:.]\d{2})?)",
    # "2025-02-10T14:00"
    r"(\d{4}-\d{2}-\d{2}(?:T\d{2}:\d{2})?)",
    # "February 10, 2025"
    r"(\w+\s+\d{1,2},?\s+\d{4})",
]

# Patterns to identify event types
EVENT_TYPE_PATTERNS = {
    "Exam": r"\b(exam|examination|final\s+exam)\b",
    "Coursework Due": r"\b(coursework|assignment|essay|report)\s*(due|deadline|submission)\b",
    "Deadline": r"\b(deadline|due\s+date|submit\s+by)\b",
    "Quiz": r"\b(quiz|test)\b",
    "Presentation": r"\b(presentation|present)\b",
}

# Duration patterns (e.g., "3-hour exam", "2 hours")
DURATION_PATTERN = r"(\d+(?:\.\d+)?)\s*[-]?\s*(hour|hr|minute|min)s?"


def parse_date(text: str) -> Optional[datetime]:
    """
    Parse a date string into a datetime object.

    Uses dateparser for flexible parsing with UK timezone.

    Args:
        text: Raw date text

    Returns:
        Parsed datetime or None if parsing fails
    """
    if not text:
        return None

    settings = {
        "TIMEZONE": TIMEZONE,
        "RETURN_AS_TIMEZONE_AWARE": True,
        "PREFER_DAY_OF_MONTH": "first",
        "PREFER_DATES_FROM": "future",
    }

    parsed = dateparser.parse(text, settings=settings)
    return parsed


def extract_dates_from_text(text: str) -> list[tuple[str, datetime]]:
    """
    Extract all date-like strings from free text.

    Args:
        text: Free text that may contain dates

    Returns:
        List of (matched_text, parsed_datetime) tuples
    """
    results: list[tuple[str, datetime]] = []

    for pattern in DATE_PATTERNS:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            parsed = parse_date(match)
            if parsed:
                results.append((match, parsed))

    return results


def detect_event_type(text: str) -> str:
    """
    Detect the type of event from text.

    Args:
        text: Text describing the event

    Returns:
        Event type string (e.g., "Exam", "Coursework Due")
    """
    text_lower = text.lower()

    for event_type, pattern in EVENT_TYPE_PATTERNS.items():
        if re.search(pattern, text_lower):
            return event_type

    return "Event"  # Default


def parse_duration(text: str) -> Optional[int]:
    """
    Parse a duration from text into minutes.

    Args:
        text: Text that may contain duration (e.g., "3-hour exam")

    Returns:
        Duration in minutes, or None if not found
    """
    match = re.search(DURATION_PATTERN, text, re.IGNORECASE)
    if not match:
        return None

    value = float(match.group(1))
    unit = match.group(2).lower()

    if unit.startswith("hour") or unit == "hr":
        return int(value * 60)
    else:  # minutes
        return int(value)


def is_all_day(dt: datetime) -> bool:
    """
    Determine if a datetime should be treated as all-day.

    Returns True if the time is midnight (00:00:00).
    """
    return dt.hour == 0 and dt.minute == 0 and dt.second == 0


def parse_extracted_date(extracted) -> list[ParsedEvent]:
    """
    Parse an ExtractedDate into one or more ParsedEvents.

    Handles assignment dates (Opens/Due) and key dates.

    Args:
        extracted: ExtractedDate from scrapers.py

    Returns:
        List of ParsedEvent objects
    """
    from polecat.scrapers import ExtractedDate

    if not isinstance(extracted, ExtractedDate):
        return []

    events: list[ParsedEvent] = []

    # Parse the date text directly
    parsed_dt = parse_date(extracted.date_text)

    if parsed_dt:
        all_day = is_all_day(parsed_dt)

        events.append(
            ParsedEvent(
                course_name=extracted.course_name,
                title=extracted.title,
                start_dt=parsed_dt.date() if all_day else parsed_dt,
                all_day=all_day,
                source=extracted.source,
                url=extracted.url,
                notes=extracted.notes,
            )
        )

    return events


def merge_events(events: list[ParsedEvent]) -> list[ParsedEvent]:
    """
    Merge events from multiple sources, prioritizing assignment pages on conflicts.

    Conflict resolution rules:
    - If same course+date has events from both "key_dates" and "assignment" sources
    - Prioritize "assignment" source (more accurate)
    - Flag the conflict for user notification

    Args:
        events: List of ParsedEvent from all sources

    Returns:
        Deduplicated list with conflicts flagged
    """
    # Group by course and approximate date
    grouped: dict[str, list[ParsedEvent]] = {}

    for event in events:
        # Create a key based on course and date (ignoring time for grouping)
        if isinstance(event.start_dt, datetime):
            date_key = event.start_dt.date()
        else:
            date_key = event.start_dt

        key = f"{event.course_name}|{date_key}"

        if key not in grouped:
            grouped[key] = []
        grouped[key].append(event)

    # Process groups
    result: list[ParsedEvent] = []

    for key, group in grouped.items():
        if len(group) == 1:
            result.append(group[0])
        else:
            # Multiple events on same date for same course
            key_dates_events = [e for e in group if e.source == "key_dates"]
            assignment_events = [e for e in group if e.source == "assignment"]

            if key_dates_events and assignment_events:
                # Conflict: prioritize assignment source but flag it
                for event in assignment_events:
                    event.conflict = True
                    event.notes = (
                        (event.notes + " " if event.notes else "") +
                        "[Conflict: Key Dates table had different info - Assignment page prioritized]"
                    )
                    result.append(event)
            else:
                # No conflict between sources, keep all
                result.extend(group)

    # Sort by date
    # Convert all to timezone-aware datetimes for comparison
    import pytz
    tz = pytz.timezone(TIMEZONE)

    def sort_key(e):
        if isinstance(e.start_dt, datetime):
            # If already timezone-aware, use as-is
            if e.start_dt.tzinfo is not None:
                return e.start_dt
            # Make naive datetime timezone-aware
            return tz.localize(e.start_dt)
        else:
            # Convert date to timezone-aware datetime
            return tz.localize(datetime.combine(e.start_dt, datetime.min.time()))

    result.sort(key=sort_key)

    return result
