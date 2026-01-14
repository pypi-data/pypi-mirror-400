"""Tests for polecat.calendar_gen module."""

import pytest
from datetime import datetime, date, timedelta
from pathlib import Path
import tempfile

from polecat.calendar_gen import (
    generate_uid,
    create_event,
    create_calendar,
    get_output_filename,
    write_calendar,
    generate_ics,
)
from polecat.parsers import ParsedEvent


class TestGenerateUid:
    """Tests for generate_uid function."""

    def test_uid_is_stable(self):
        event = ParsedEvent(
            course_name="MBA10 Strategy",
            title="Exam",
            start_dt=datetime(2025, 2, 10, 14, 0),
            source="A",
        )
        uid1 = generate_uid(event)
        uid2 = generate_uid(event)
        assert uid1 == uid2

    def test_different_events_different_uids(self):
        event1 = ParsedEvent(
            course_name="MBA10 Strategy",
            title="Exam",
            start_dt=datetime(2025, 2, 10, 14, 0),
            source="A",
        )
        event2 = ParsedEvent(
            course_name="MBA10 Strategy",
            title="Exam",
            start_dt=datetime(2025, 2, 11, 14, 0),  # Different date
            source="A",
        )
        assert generate_uid(event1) != generate_uid(event2)

    def test_uid_format(self):
        event = ParsedEvent(
            course_name="Course",
            title="Event",
            start_dt=datetime(2025, 2, 10, 14, 0),
            source="A",
        )
        uid = generate_uid(event)
        assert uid.endswith("@polecat.jbs")
        assert len(uid) > 20  # Hash + domain


class TestCreateEvent:
    """Tests for create_event function."""

    def test_timed_event(self):
        parsed = ParsedEvent(
            course_name="MBA10 Strategy",
            title="Final Exam",
            start_dt=datetime(2025, 2, 10, 14, 0),
            source="A",
            url="https://example.com/course/1",
        )
        event = create_event(parsed)

        assert "[MBA10 Strategy] Final Exam" in event.name
        assert event.begin is not None
        assert event.url == "https://example.com/course/1"

    def test_all_day_event(self):
        parsed = ParsedEvent(
            course_name="MBA10 Strategy",
            title="Deadline",
            start_dt=date(2025, 2, 10),
            all_day=True,
            source="A",
        )
        event = create_event(parsed)

        assert event.begin is not None
        # All-day events should have the all_day property set
        assert event.all_day is True

    def test_event_with_end_time(self):
        start = datetime(2025, 2, 10, 14, 0)
        end = datetime(2025, 2, 10, 17, 0)
        parsed = ParsedEvent(
            course_name="Course",
            title="Exam",
            start_dt=start,
            end_dt=end,
            source="A",
        )
        event = create_event(parsed)

        assert event.end is not None

    def test_conflict_warning_in_description(self):
        parsed = ParsedEvent(
            course_name="Course",
            title="Exam",
            start_dt=datetime(2025, 2, 10, 14, 0),
            source="B",
            conflict=True,
        )
        event = create_event(parsed)

        assert "CONFLICT" in event.description

    def test_source_in_description(self):
        parsed = ParsedEvent(
            course_name="Course",
            title="Exam",
            start_dt=datetime(2025, 2, 10, 14, 0),
            source="assignment",
        )
        event = create_event(parsed)

        assert "Assignment page" in event.description


class TestCreateCalendar:
    """Tests for create_calendar function."""

    def test_create_calendar_with_events(self):
        events = [
            ParsedEvent(
                course_name="Course A",
                title="Exam 1",
                start_dt=datetime(2025, 2, 10, 14, 0),
                source="A",
            ),
            ParsedEvent(
                course_name="Course B",
                title="Exam 2",
                start_dt=datetime(2025, 2, 15, 10, 0),
                source="A",
            ),
        ]
        calendar = create_calendar(events)

        assert len(calendar.events) == 2

    def test_create_empty_calendar(self):
        calendar = create_calendar([])
        assert len(calendar.events) == 0


class TestGetOutputFilename:
    """Tests for get_output_filename function."""

    def test_filename_format(self):
        filename = get_output_filename()
        assert filename.startswith("JBS_Calendar_")
        assert filename.endswith(".ics")
        assert "Lent" in filename  # Current hardcoded term


class TestWriteCalendar:
    """Tests for write_calendar function."""

    def test_write_to_temp_directory(self):
        events = [
            ParsedEvent(
                course_name="Course A",
                title="Exam",
                start_dt=datetime(2025, 2, 10, 14, 0),
                source="A",
            ),
        ]
        calendar = create_calendar(events)

        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = write_calendar(calendar, tmpdir)

            assert filepath.exists()
            assert filepath.suffix == ".ics"

            # Verify file has content
            content = filepath.read_text()
            assert "BEGIN:VCALENDAR" in content
            assert "END:VCALENDAR" in content


class TestGenerateIcs:
    """Tests for generate_ics function (integration)."""

    def test_generate_ics_creates_file(self):
        events = [
            ParsedEvent(
                course_name="MBA10 Strategy",
                title="Final Exam",
                start_dt=datetime(2025, 2, 10, 14, 0),
                end_dt=datetime(2025, 2, 10, 17, 0),
                source="A",
                url="https://example.com/course/1",
            ),
            ParsedEvent(
                course_name="MBA11 Marketing",
                title="Coursework Due",
                start_dt=date(2025, 2, 15),
                all_day=True,
                source="B",
            ),
        ]

        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = generate_ics(events, tmpdir)

            assert filepath.exists()

            content = filepath.read_text()
            assert "BEGIN:VEVENT" in content
            assert "MBA10 Strategy" in content
            assert "MBA11 Marketing" in content
