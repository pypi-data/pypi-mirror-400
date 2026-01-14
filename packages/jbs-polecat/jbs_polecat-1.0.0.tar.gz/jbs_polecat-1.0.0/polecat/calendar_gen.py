"""ICS calendar generation."""

import hashlib
import os
from datetime import datetime, date, timedelta
from pathlib import Path

from ics import Calendar, Event

from polecat.config import CURRENT_TERM, ICS_FILENAME_TEMPLATE, TIMEZONE
from polecat.parsers import ParsedEvent


def generate_uid(event: ParsedEvent) -> str:
    """
    Generate a stable UID for an event to prevent duplicates on re-import.

    Args:
        event: The ParsedEvent to generate a UID for

    Returns:
        A unique identifier string
    """
    # Create a stable hash from course, title, and start time
    if isinstance(event.start_dt, datetime):
        dt_str = event.start_dt.isoformat()
    else:
        dt_str = event.start_dt.isoformat()

    unique_string = f"{event.course_name}|{event.title}|{dt_str}"
    hash_digest = hashlib.sha256(unique_string.encode()).hexdigest()[:16]

    return f"{hash_digest}@polecat.jbs"


def create_event(parsed: ParsedEvent) -> Event:
    """
    Create an ICS Event from a ParsedEvent.

    Args:
        parsed: The ParsedEvent to convert

    Returns:
        An ics.Event object
    """
    event = Event()

    # Set name with course prefix
    event.name = f"[{parsed.course_name}] {parsed.title}"

    # Set UID for deduplication
    event.uid = generate_uid(parsed)

    # Handle all-day vs timed events
    if parsed.all_day:
        # For all-day events, use date only
        if isinstance(parsed.start_dt, datetime):
            event.begin = parsed.start_dt.date()
        else:
            event.begin = parsed.start_dt
        event.make_all_day()
    else:
        # Timed event
        event.begin = parsed.start_dt

        # Set end time if available
        if parsed.end_dt:
            event.end = parsed.end_dt
        elif isinstance(parsed.start_dt, datetime):
            # Default to 1 hour if no end time specified
            event.end = parsed.start_dt + timedelta(hours=1)

    # Build description
    description_parts = []

    if parsed.course_name:
        description_parts.append(f"Course: {parsed.course_name}")

    if parsed.source:
        source_name = "Assignment page" if parsed.source == "assignment" else "Key dates"
        description_parts.append(f"Source: {source_name}")

    if parsed.conflict:
        description_parts.append("⚠️ CONFLICT: This event had conflicting data from multiple sources.")

    if parsed.notes:
        description_parts.append(f"Notes: {parsed.notes}")

    if parsed.url:
        description_parts.append(f"Course URL: {parsed.url}")

    event.description = "\n".join(description_parts)

    # Set URL if available
    if parsed.url:
        event.url = parsed.url

    return event


def create_calendar(events: list[ParsedEvent]) -> Calendar:
    """
    Create an ICS Calendar from a list of ParsedEvents.

    Args:
        events: List of ParsedEvent objects

    Returns:
        An ics.Calendar object
    """
    calendar = Calendar()

    for parsed_event in events:
        ics_event = create_event(parsed_event)
        calendar.events.add(ics_event)

    return calendar


def get_output_filename() -> str:
    """
    Generate the output filename based on term and year.

    Returns:
        Filename string (e.g., "JBS_Calendar_Lent_2025.ics")
    """
    year = datetime.now().year
    return ICS_FILENAME_TEMPLATE.format(term=CURRENT_TERM, year=year)


def write_calendar(calendar: Calendar, directory: str | Path | None = None) -> Path:
    """
    Write the calendar to an ICS file.

    Args:
        calendar: The Calendar object to write
        directory: Directory to write to (defaults to current working directory)

    Returns:
        Path to the written file
    """
    if directory is None:
        directory = Path.cwd()
    else:
        directory = Path(directory)

    filename = get_output_filename()
    filepath = directory / filename

    with open(filepath, "w", encoding="utf-8") as f:
        f.writelines(calendar.serialize_iter())

    return filepath


def generate_ics(events: list[ParsedEvent], directory: str | Path | None = None) -> Path:
    """
    Main entry point: generate and write an ICS file from events.

    Args:
        events: List of ParsedEvent objects
        directory: Directory to write to (defaults to current working directory)

    Returns:
        Path to the written ICS file
    """
    calendar = create_calendar(events)
    filepath = write_calendar(calendar, directory)
    return filepath
