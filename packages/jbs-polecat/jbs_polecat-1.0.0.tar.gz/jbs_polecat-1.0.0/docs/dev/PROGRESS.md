# Polecat Development Progress Log

## Current Status
**Phase:** 1 (Calendar Automation) — **COMPLETE**
**Version:** 1.0.0
**Last Updated:** 2026-01-08

---

## Completed

### Commit 1: Project Structure
- Created `polecat/` package directory
- Created `tests/` directory
- Created `PROGRESS.md` (this file)
- Created `polecat/__init__.py`

### Commit 2: Configuration
- Created `polecat/config.py` with constants (URLs, timezone, term, timeouts)
- Created `requirements.txt` with dependencies

### Commit 3: Browser Module
- Created `polecat/browser.py` with Playwright setup
- `launch_browser()` — launches headful Chromium
- `create_page()` — creates page with default timeouts
- `wait_for_login()` — navigates to dashboard, waits for SSO completion
- `wait_for_term_selection()` — prompts user to select term, waits for confirmation

### Commit 4: Scrapers Module
- Created `polecat/scrapers.py` with BeautifulSoup extraction
- Data classes: `Course`, `ExtractedDate`
- `extract_courses()` — finds course cards on dashboard (multiple selector strategies)
- `extract_key_dates()` — Source A extraction from Key dates table
- `extract_assessment_dates()` — Source B extraction from Assessment guidance text
- `scrape_course_dates()` — navigates to course and extracts from both sources

### Commit 5: Parsers Module
- Created `polecat/parsers.py` with dateparser-based parsing
- Data class: `ParsedEvent` (normalized event ready for ICS)
- `parse_date()` — flexible date parsing with UK timezone
- `extract_dates_from_text()` — regex-based date extraction from free text
- `detect_event_type()` — identifies Exam, Coursework, Deadline, etc.
- `parse_duration()` — extracts duration for end time calculation
- `parse_extracted_date()` — converts ExtractedDate to ParsedEvent(s)
- `merge_events()` — deduplicates and flags conflicts (Source B prioritized)

### Commit 6: Calendar Generation Module
- Created `polecat/calendar_gen.py` with ICS generation
- `generate_uid()` — stable UIDs via SHA256 hash to prevent duplicates on re-import
- `create_event()` — converts ParsedEvent to ics.Event (handles all-day/timed)
- `create_calendar()` — builds Calendar from list of events
- `get_output_filename()` — generates filename like `JBS_Calendar_Lent_2025.ics`
- `write_calendar()` — writes ICS file to disk
- `generate_ics()` — main entry point combining all steps

### Commit 7: CLI Orchestrator
- Created `polecat/main.py` — ties all modules together
- `print_banner()` — displays Polecat header
- `print_summary_table()` — shows extracted events in a formatted table
- `get_user_confirmation()` — y/n prompt before generating ICS
- `run()` — main workflow: login → term select → discover → scrape → parse → confirm → generate
- `main()` — entry point with error handling

### Commit 8: Unit Tests
- Created `tests/__init__.py`
- Created `tests/test_parsers.py` — tests for parsing functions
- Created `tests/test_calendar_gen.py` — tests for calendar generation
- Added `pytest>=7.0.0` to `requirements.txt`

### Commit 9: Dual-Source Date Extraction
- Updated `docs/SITE_STRUCTURE.md` with critical dual-source extraction rules
- Rewrote `scrapers.py` for dual-source extraction:
  - `find_key_dates_link()` — finds Key Dates link on course page
  - `extract_key_dates()` — extracts dates from Key Dates table (if exists)
  - `find_assignment_links()` — finds all assignment links on course page
  - `extract_assignment_dates()` — extracts "Opens:" and "Due:" dates from assignment pages
  - `scrape_course_dates()` — now extracts from BOTH sources
- Updated `parsers.py` merge_events() for conflict resolution:
  - Prioritizes assignment pages over Key Dates table on conflicts
  - Flags conflicts for user notification
- Updated `calendar_gen.py` source labels ("key_dates", "assignment")
- Updated `CLAUDE.md` to reference site structure docs
- Updated all tests to use new source names

### Commit 10: Documentation Updates
- Updated `CLAUDE.md` section 3 with dual-source extraction details
- Updated `project-requirements.md` section 2.3 with accurate source info
- Updated `PROGRESS.md` with testing steps

### Commit 11: Bug Fixes for Live Site Testing
- **Fixed timezone comparison bug** in `parsers.py`:
  - `merge_events()` was comparing offset-naive and offset-aware datetimes
  - Now converts all datetimes to timezone-aware before sorting
- **Fixed date extraction regex** in `scrapers.py`:
  - Original regex too strict for actual page format
  - New flexible pattern captures: `DD Month YYYY` + optional `HH:MM AM/PM`
  - Added `extract_dates_near_assignment_link()` for course page extraction
  - Updated `scrape_course_dates()` to try course page first, then assignment page
- **Live test results (Lent 2026):**
  - 9 courses discovered
  - 79 total events extracted
  - 11 conflicts detected and flagged
  - ICS file generated successfully

### Commit 12: Event Filtering and Calendar Options
- **Added event filtering** in `main.py`:
  - By default, only saves deadlines (exams, assignments, submissions, quizzes)
  - Quiz opens/closes dates always included (time-sensitive)
  - User can opt-in to include "Opens" dates via prompt
  - User can opt-in to include unit releases/live sessions via prompt
  - All events still shown in terminal summary table
- **Added text cleanup** in `scrapers.py`:
  - `clean_title()` function fixes formatting issues
  - Adds space after colons (e.g., "Unit 2:Creating" -> "Unit 2: Creating")
  - Normalizes whitespace
- **Added `.gitignore`**:
  - Excludes generated `.ics` files
  - Excludes `__pycache__/`, `.pyc`, venv, IDE files, etc.

### Commit 13: Quiz Opens/Closes Date Extraction
- **Extended Key Dates table extraction** in `scrapers.py`:
  - Now extracts all 5 columns (was only 3):
    - Column 1: Unit name
    - Column 2: Unit release date
    - Column 3: Live session date
    - Column 4: Online open book assessment (quiz) opens
    - Column 5: Online open book assessment (quiz) closes
  - Handles "09.00am" date format (normalizes to "09:00am")
  - Skips N/A values
- **Updated quiz detection** in `main.py`:
  - Checks both title and notes field for quiz indicators
  - Quiz events always included (both Opens and Closes)
- **Removed `__pycache__/` from git tracking**

### Commit 14: Repository Cleanup
- **Removed `.DS_Store`** from git tracking
- **Reorganized documentation** into `docs/dev/`:
  - Moved `CLAUDE.md`, `PROGRESS.md`, `project-requirements.md`
  - Moved `SITE_STRUCTURE.md` from `docs/` to `docs/dev/`
  - Updated all internal file references
- **Removed `tests/__pycache__/`** from git tracking
- Root now contains only: README.md, LICENSE, requirements.txt, .gitignore, and code directories

### Commit 15: PyPI Package Setup (v1.0.0)
- **Added `pyproject.toml`** with PEP 621 metadata:
  - Package name: `polecat`
  - Version: 1.0.0
  - CLI entry point: `polecat` command
  - All dependencies declared
- **Updated `polecat/__init__.py`** with `__version__ = "1.0.0"`
- **Updated README.md** with simplified pip install instructions
- **Updated documentation** (CLAUDE.md, project-requirements.md) with distribution info
- Polecat is now installable via `pip install polecat`

---

## In Progress
- None

---

## Up Next
1. **Publish to PyPI** — Upload v1.0.0 to pypi.org
2. **Phase 2 planning** — Directory structure and file downloads

---

## Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2025-01-07 | Hardcode "Lent" term | Current term, simplifies initial build |
| 2025-01-07 | Manual term dropdown selection | Simpler, less brittle, matches human-in-the-loop philosophy |
| 2025-01-07 | Skip session persistence | Simpler for Phase 1, can add later |
| 2025-01-07 | UK timezone (Europe/London) | JBS is in Cambridge, UK |
| 2025-01-07 | Dual-source extraction | Key Dates may have quizzes not on assignment pages; must check both |
| 2025-01-07 | Prioritize assignment pages on conflicts | Assignment pages have more accurate/official dates |
| 2026-01-08 | Distribute as pip package on PyPI | Lowers barrier for non-technical users who don't use git |
| 2026-01-08 | Version 1.0.0 for first stable release | Phase 1 complete, tested on live site, ready for users |

---

## Notes
- User must complete SSO manually in headful browser
- User must select "Lent" from term dropdown manually, then confirm in terminal
- Output `.ics` written to current working directory with full path displayed
