"""Tests for polecat.parsers module."""

import pytest
from datetime import datetime, date

from polecat.parsers import (
    parse_date,
    extract_dates_from_text,
    detect_event_type,
    parse_duration,
    is_all_day,
    parse_extracted_date,
    merge_events,
    ParsedEvent,
)
from polecat.scrapers import ExtractedDate


class TestParseDate:
    """Tests for parse_date function."""

    def test_parse_standard_date(self):
        result = parse_date("10 February 2025")
        assert result is not None
        assert result.year == 2025
        assert result.month == 2
        assert result.day == 10

    def test_parse_date_with_time(self):
        result = parse_date("10 February 2025 14:00")
        assert result is not None
        assert result.year == 2025
        assert result.month == 2
        assert result.day == 10
        assert result.hour == 14
        assert result.minute == 0

    def test_parse_date_with_day_name(self):
        result = parse_date("Monday 10 February 2025")
        assert result is not None
        assert result.day == 10
        assert result.month == 2

    def test_parse_iso_format(self):
        result = parse_date("2025-02-10")
        assert result is not None
        assert result.year == 2025
        assert result.month == 2
        assert result.day == 10

    def test_parse_empty_string(self):
        result = parse_date("")
        assert result is None

    def test_parse_none(self):
        result = parse_date(None)
        assert result is None


class TestExtractDatesFromText:
    """Tests for extract_dates_from_text function."""

    def test_extract_single_date(self):
        text = "The exam is on 15 March 2025."
        results = extract_dates_from_text(text)
        assert len(results) >= 1
        matched_text, parsed_dt = results[0]
        assert parsed_dt.month == 3
        assert parsed_dt.day == 15

    def test_extract_multiple_dates(self):
        text = "Coursework due 10 February 2025. Exam on 15 March 2025."
        results = extract_dates_from_text(text)
        assert len(results) >= 2

    def test_extract_date_with_time(self):
        text = "Exam: 10 February 2025, 2:00 PM"
        results = extract_dates_from_text(text)
        assert len(results) >= 1

    def test_no_dates_found(self):
        text = "This text has no dates in it."
        results = extract_dates_from_text(text)
        assert len(results) == 0


class TestDetectEventType:
    """Tests for detect_event_type function."""

    def test_detect_exam(self):
        assert detect_event_type("Final Exam") == "Exam"
        assert detect_event_type("examination") == "Exam"

    def test_detect_coursework(self):
        assert detect_event_type("Coursework submission deadline") == "Coursework Due"
        assert detect_event_type("Assignment due") == "Coursework Due"

    def test_detect_deadline(self):
        assert detect_event_type("Deadline for submission") == "Deadline"

    def test_detect_quiz(self):
        assert detect_event_type("Weekly Quiz") == "Quiz"

    def test_detect_presentation(self):
        assert detect_event_type("Group Presentation") == "Presentation"

    def test_default_event_type(self):
        assert detect_event_type("Some random text") == "Event"


class TestParseDuration:
    """Tests for parse_duration function."""

    def test_parse_hours(self):
        assert parse_duration("3-hour exam") == 180
        assert parse_duration("2 hour test") == 120
        assert parse_duration("1.5 hours") == 90

    def test_parse_minutes(self):
        assert parse_duration("90 minute quiz") == 90
        assert parse_duration("45 mins") == 45

    def test_no_duration(self):
        assert parse_duration("exam on Monday") is None


class TestIsAllDay:
    """Tests for is_all_day function."""

    def test_midnight_is_all_day(self):
        dt = datetime(2025, 2, 10, 0, 0, 0)
        assert is_all_day(dt) is True

    def test_non_midnight_not_all_day(self):
        dt = datetime(2025, 2, 10, 14, 30, 0)
        assert is_all_day(dt) is False


class TestParseExtractedDate:
    """Tests for parse_extracted_date function."""

    def test_parse_assignment_date(self):
        extracted = ExtractedDate(
            course_name="MBA10 Strategy",
            title="MBA10 Assignment - Due",
            date_text="Wednesday, 4 March 2026, 9:00 AM",
            source="assignment",
            url="https://example.com/mod/assign/view.php?id=123",
        )
        events = parse_extracted_date(extracted)
        assert len(events) >= 1
        assert events[0].course_name == "MBA10 Strategy"
        assert events[0].source == "assignment"

    def test_parse_assignment_opens_date(self):
        extracted = ExtractedDate(
            course_name="MBA11 Marketing",
            title="MBA11 Assignment - Opens",
            date_text="Monday, 12 January 2026, 9:00 AM",
            source="assignment",
            url="https://example.com/mod/assign/view.php?id=456",
        )
        events = parse_extracted_date(extracted)
        assert len(events) >= 1
        assert events[0].source == "assignment"
        assert "Opens" in events[0].title


class TestMergeEvents:
    """Tests for merge_events function."""

    def test_no_conflicts(self):
        events = [
            ParsedEvent(
                course_name="Course A",
                title="Exam",
                start_dt=datetime(2025, 2, 10, 14, 0),
                source="key_dates",
            ),
            ParsedEvent(
                course_name="Course B",
                title="Exam",
                start_dt=datetime(2025, 2, 15, 10, 0),
                source="key_dates",
            ),
        ]
        merged = merge_events(events)
        assert len(merged) == 2
        assert not any(e.conflict for e in merged)

    def test_conflict_prioritizes_assignment(self):
        events = [
            ParsedEvent(
                course_name="Course A",
                title="Exam",
                start_dt=datetime(2025, 2, 10, 14, 0),
                source="key_dates",
            ),
            ParsedEvent(
                course_name="Course A",
                title="Exam",
                start_dt=datetime(2025, 2, 10, 15, 0),  # Same date, different time
                source="assignment",
            ),
        ]
        merged = merge_events(events)
        # Assignment source should be kept and flagged
        assert len(merged) == 1
        assert merged[0].source == "assignment"
        assert merged[0].conflict is True

    def test_events_sorted_by_date(self):
        events = [
            ParsedEvent(
                course_name="Course A",
                title="Later Exam",
                start_dt=datetime(2025, 3, 15, 14, 0),
                source="assignment",
            ),
            ParsedEvent(
                course_name="Course B",
                title="Earlier Exam",
                start_dt=datetime(2025, 2, 10, 10, 0),
                source="assignment",
            ),
        ]
        merged = merge_events(events)
        assert merged[0].title == "Earlier Exam"
        assert merged[1].title == "Later Exam"
