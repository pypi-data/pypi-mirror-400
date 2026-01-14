# Polecat (JBS Learning Platform Automation)

## What this repo is
Polecat automates parts of the Cambridge Judge Business School learning platform (`learn.jbs.cam.ac.uk`).

### Phase 1 (current priority)
1) User manually logs in via SSO in a visible (headful) browser session  
2) Polecat discovers courses for a user-selected term (e.g., Lent)  
3) Polecat extracts assessment/exam dates from each course (two sources)  
4) Polecat shows a sanity-check summary in terminal and asks for confirmation  
5) Polecat generates an `.ics` calendar file: `JBS_Calendar_[Term]_[Year].ics`

### Phase 2 (future scope)
- Create `[term-name]/` and per-course subfolders
- Download “Required readings” and “Notes/slides/files” into structured folders

---

## Non-negotiable constraints
- **Human-in-the-loop SSO:** do not automate login or store credentials.
- **Headful browser:** user must be able to see the browser and complete SSO.
- **Be gentle:** avoid hammering the site; prefer explicit waits over tight loops.
- **Do not leak data:** no logging of personal course content beyond what’s needed.

---

## Tech stack (expected)
- Python 3.10+
- Playwright (navigation + downloads)
- BeautifulSoup4 (HTML parsing)
- `dateparser` (date/time parsing)
- `ics` (calendar generation)

---

## Distribution
Polecat is distributed as a **pip-installable Python package** on PyPI.

### Installation (for users)
```bash
pip install jbs-polecat
playwright install chromium
polecat
```

### Versioning
- Follows [Semantic Versioning](https://semver.org/) (MAJOR.MINOR.PATCH)
- Version is defined in `polecat/__init__.py`
- v1.0.0 = First stable release (Phase 1 complete)

### Publishing to PyPI
```bash
python -m build
twine upload dist/*
```

---

## How the automation should work (high level)
### 1) Browser + login checkpoint
- Launch Playwright in headful mode.
- Navigate to `https://learn.jbs.cam.ac.uk/my/`.
- Wait until the user has completed SSO and the dashboard is reachable.
  - Prefer robust conditions: `page.wait_for_url("**/my/**")` and/or a known dashboard selector. :contentReference[oaicite:2]{index=2}

### 2) Term selection + course discovery
- Term is selected via CLI prompt (e.g., “Lent”).
- Apply the dashboard filter for that term.
- Extract all visible course cards:
  - `course_name`
  - `course_url`

### 3) Date extraction for each course (DUAL SOURCE)
**CRITICAL:** Dates must be extracted from TWO sources. See `docs/dev/SITE_STRUCTURE.md` for detailed selectors.

**Source 1: Key Dates table** (not all courses have this)
- Location: Course page → Key Resources → "Key dates" link
- Contains: Exams, quizzes, deadlines — may have dates NOT found on assignment pages
- If not found: Skip this source for the course

**Source 2: Assignment pages** (all courses have this)
- Location: Course page → Find `/mod/assign/` links → Visit each
- Contains: "Opens:" and "Due:" dates in completion requirements div
- Primary/priority source when conflicts occur

**Conflict resolution:**
- If same activity has different dates in both sources → Prioritize Assignment pages
- Flag conflicts for user notification in summary table

Normalize into a single internal structure:
  - `course_name`
  - `title` (e.g., "MBA41 Individual Assignment - Due")
  - `start_dt` (timezone-aware)
  - `all_day` (if no time)
  - `source` ("key_dates" or "assignment")
  - `url` (deep link)
  - `notes` (optional)
  - `conflict` (True if sources disagreed)

### 4) Verification + output
- Print a compact summary table (sorted by date).
- Ask: “Do these dates look correct? (y/n)”
- Only write the `.ics` file on “y”.

---

## Calendar (.ics) rules
- Use RFC 5545-compatible generation via the `ics` library. :contentReference[oaicite:3]{index=3}
- Prefer stable `UID`s to reduce duplicates on re-import (e.g., hash of course+title+datetime).
- Handle:
  - all-day events (date only)
  - timed events (datetime)
  - missing/ambiguous times (mark all-day + add note)
- Put the course URL in the event `url`/description when available.

---

## Playwright guidance (keep it resilient)
- Prefer user-facing selectors (roles/text) over brittle CSS when possible. :contentReference[oaicite:4]{index=4}
- Always use explicit waits for navigation and dynamic content. :contentReference[oaicite:5]{index=5}
- Keep scraping separate from navigation: navigate with Playwright, parse with BeautifulSoup using `page.content()`.

### Optional: session persistence
If it materially improves DX, you MAY add an opt-in persistent context (stores browser state locally).
- Must be explicit and documented, because it can retain an authenticated session on disk. :contentReference[oaicite:6]{index=6}

---

## Suggested repo layout
- `polecat/`
  - `__init__.py` (package init + version)
  - `config.py` (constants)
  - `browser.py` (Playwright setup + login wait)
  - `scrapers.py` (BeautifulSoup extraction)
  - `parsers.py` (text cleanup + date parsing)
  - `calendar_gen.py` (ICS creation)
  - `main.py` (CLI orchestrator)
- `docs/dev/`
  - `CLAUDE.md` — AI assistant instructions
  - `PROGRESS.md` — Development progress log
  - `project-requirements.md` — Project requirements
  - `SITE_STRUCTURE.md` — JBS Moodle site layout, selectors, and scraping strategy
- `tests/` — Unit tests for parsing + calendar generation
- `pyproject.toml` — Package metadata, dependencies, CLI entry point
- `README.md` — User-facing documentation
- `LICENSE` — MIT license

---

## Quality bar (what you should enforce)
When making changes in this repo:
- Keep changes small and reviewable; prefer incremental commits.
- Add type hints for public functions and key data structures.
- Write unit tests for parsers and ICS generation.
- Don’t introduce heavy frameworks unless clearly needed.

---

## What to do when unsure
- If an extraction is ambiguous, surface it in the summary table with a note rather than guessing silently.
- If the UI changes, favor robust selector strategies and fail with a helpful message (“Could not find Key dates link for course X”).

---

## Quick “definition of done” for Phase 1
- Running the CLI produces a verified summary table and a valid `.ics` file for a chosen term.
- No credentials stored.
- Reasonable handling of missing times and duplicate events.
