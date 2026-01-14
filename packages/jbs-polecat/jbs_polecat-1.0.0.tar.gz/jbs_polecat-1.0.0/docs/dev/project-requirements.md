# Project Requirements: JBS Learning Platform Automation
This project and automation tool will be named "polecat".

## 1. Project Overview
**Goal:** build an automation tool for the Cambridge Judge Business School (JBS) learning platform (`learn.jbs.cam.ac.uk`).
* **Phase 1 (Current Focus):** Extract exam dates/deadlines and generate a `.ics` calendar.
* **Phase 2 (Future Scope):** Automate file management by creating course directories and downloading required readings and lecture slides.

**Core Philosophy:** "Hybrid Pilot" — Use browser automation (Playwright) to handle navigation, `BeautifulSoup` for parsing, but rely on manual user intervention for the initial Single Sign-On (SSO).

---

## 2. Phase 1: Calendar Automation (Current Priority)

### 2.1 Authentication
* **Method:** Manual "Human-in-the-Loop" Login.
* **Process:**
    1.  Script launches a visible (headful) browser instance.
    2.  Script waits/polls until the user manually logs in and reaches the Dashboard.
* **Constraint:** No credentials stored in code.

### 2.2 Term Selection & Course Discovery
* **Dashboard Entry:** `https://learn.jbs.cam.ac.uk/my/`
* **Term Filtering:**
    * User selects term via CLI (e.g., "Lent").
    * Script applies filter on Dashboard.
* **Course Extraction:**
    * Identify all visible course cards.
    * Store `Course Name` and `Course URL`.

### 2.3 Data Extraction (Dual-Source)
For *each* course, extract dates from **BOTH** sources:
1.  **Source 1 (Key Dates Table):** "Key resources" → "Key dates" link → Table with dates.
    - Not all courses have this (e.g., MBA10 has it, MBA41 does not).
    - May contain quizzes/exams NOT found on assignment pages.
2.  **Source 2 (Assignment Pages):** Course page → `/mod/assign/` links → Each assignment page.
    - All courses have this.
    - Extract "Opens:" and "Due:" dates from completion requirements.
    - **Priority source** when conflicts occur.

See `docs/dev/SITE_STRUCTURE.md` for detailed selectors and patterns.

### 2.4 Verification & Output
* **Sanity Check:** Display a summary table of found dates in the terminal.
* **User Prompt:** "Do these dates look correct? (y/n)"
* **Output:** Generate `JBS_Calendar_[Term]_[Year].ics`.

---

## 3. Phase 2: Content Management (Future Additions)

### 3.1 Directory Structure Automation
* **Trigger:** Immediately after "Course Discovery" (Step 2.2).
* **Logic:**
    1.  Create a parent directory: `[Term-Name]/` (e.g., `lent-term/`).
    2.  Clean/Slugify course names (e.g., "MBA10 Strategy (2025/26)" -> `mba10-strategy`).
    3.  Create a sub-directory for each course inside the parent folder.
* **Example Structure:**
    ```text
    lent-term/
    ├── mba10-strategy/
    ├── mba11-marketing/
    └── mba12-corporate-governance/
    ```

### 3.2 Material Downloads
* **Navigation:**
    * Go to Course Home.
    * Locate "Reading list" under "Key resources".
    * Locate "Notes, slides & files" under "Key resources".
* **Action - Readings:**
    * Identify items tagged as "Required readings".
    * Download PDF/Document to `[Course-Folder]/Readings/`.
* **Action - Slides:**
    * Identify lecture slides/notes.
    * Download to `[Course-Folder]/Slides/`.

---

## 4. Technical Requirements & Stack
* **Language:** Python 3.10+
* **Browser Automation:** `playwright` (Navigation & Downloads).
* **Scraping Engine:** `beautifulsoup4` (HTML Parsing).
* **File System:** Python `os` and `pathlib` modules (Directory creation).
* **Calendar:** `ics` library.
* **Date Parsing:** `dateparser`.
* **Packaging:** `pyproject.toml` (PEP 621).

---

## 5. Distribution

### 5.1 Package Distribution
Polecat is distributed as a **pip-installable Python package** on PyPI to lower the barrier for non-technical users.

* **Package Name:** `jbs-polecat`
* **Installation:** `pip install jbs-polecat`
* **CLI Command:** `polecat` (entry point defined in pyproject.toml)

### 5.2 Versioning
* Follows [Semantic Versioning](https://semver.org/) (MAJOR.MINOR.PATCH)
* Version defined in `polecat/__init__.py`
* **v1.0.0** = First stable release (Phase 1 complete)

### 5.3 User Installation Steps
```bash
pip install jbs-polecat
playwright install chromium
polecat
```

**Note:** `playwright install chromium` is required separately because browser binaries (~150MB) cannot be bundled with PyPI packages.

---

## 6. Module Architecture

1.  **`config.py`**: Constants.
2.  **`browser.py`**: Playwright init & Login.
3.  **`scrapers.py`**: BeautifulSoup logic (Dates & Material Links).
4.  **`file_manager.py` (New for Phase 2)**:
    * `create_term_directory(term_name)`
    * `create_course_folder(course_name)`
    * `download_file(url, destination_path)`
5.  **`parsers.py`**: Date & Text cleaning.
6.  **`calendar_gen.py`**: ICS creation.
7.  **`main.py`**: Orchestrator.

---

## 7. Version Control Strategy
* **Atomic Commits:**
    * *Commit 1-5:* Phase 1 implementation (Calendar).
    * *Commit 6:* Feature - Directory Structure Creation (Phase 2).
    * *Commit 7:* Feature - Reading List Scraper & Downloader (Phase 2).