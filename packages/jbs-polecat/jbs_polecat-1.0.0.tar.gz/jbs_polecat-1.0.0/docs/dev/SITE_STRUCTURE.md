# JBS Learning Platform Site Structure

**Last verified:** 2026-01-07 (live tested successfully)
**Base URL:** `https://learn.jbs.cam.ac.uk`

This document describes the structure of the JBS Moodle learning platform for scraping purposes.

---

## CRITICAL: Dual-Source Date Extraction

**Dates must be collected from TWO sources for each course:**

| Source | Location | Availability | Contains |
|--------|----------|--------------|----------|
| **Key Dates** | Key Resources → Key Dates | Some courses only (e.g., MBA10 has it, MBA41 does not) | Exams, quizzes, deadlines - may have dates NOT found elsewhere |
| **Assignment Pages** | Module overview and assessment → Assignment links | All courses | Assignment Opens/Due dates |

### Conflict Resolution Rules

1. **Always check BOTH sources** — Key Dates may have additional dates (e.g., online quizzes) not found on assignment pages
2. **If same activity has different dates in both sources** → Prioritize the date from Assignment Pages (Module overview and assessment)
3. **Always notify user** when a conflict is detected between sources

---

## 1. Dashboard (`/my/`)

The main entry point after SSO login.

**Key elements:**
- Term/course filter dropdown (user selects manually)
- Course cards with links to individual courses

**Course card selectors:**
```
.coursebox a.aalink
.course-card a
[data-region='course-content'] a
.course-listitem a.aalink
```

**Course URL pattern:** `/course/view.php?id={course_id}`

---

## 2. Course Page (`/course/view.php?id={course_id}`)

Main course page with sections.

**Key sections (accessed via links):**

| Section | URL Pattern | Content |
|---------|-------------|---------|
| Key resources | `/course/section.php?id={section_id}` | Reading list, **Key dates** (if exists) |
| Module overview and assessment | `/course/section.php?id={section_id}` | Assessment overview, assignment links |
| Module assessment guidance | `/mod/summary/view.php?id={module_id}` | Word counts, requirements |

---

## 3. Source A: Key Dates Table (NOT ALL COURSES)

**Availability:** Only some courses have this (e.g., MBA10 Strategy has it, MBA41 does not)

**Location:** Course Page → Key Resources section → "Key dates" link

**Why it matters:** May contain dates for quizzes, exams, or other events NOT found on assignment pages.

**How to find:**
```python
# On course page, look for "Key dates" link
key_dates_link = soup.find("a", string=lambda s: s and "key dates" in s.lower())
```

**Table structure (3-5 columns depending on course):**

| Column | Content | Example |
|--------|---------|---------|
| 1 | Unit/Activity name | "Unit 1: Introduction to marketing" |
| 2 | Unit release date | "15 December 2025" |
| 3 | Live session date | "w/c 12 January 2026" or "N/A" |
| 4 | Quiz opens (if exists) | "09.00am 5 January 2026" or "N/A" |
| 5 | Quiz closes (if exists) | "09.00am 16 January 2026" or "N/A" |

**Note:** Columns 4-5 only exist for courses with online open book assessments (e.g., MBA11 Marketing).

**If not found:** Skip this source for the course, proceed to assignment pages.

---

## 4. Source B: Assignment Pages (ALL COURSES) ⭐ PRIMARY SOURCE

**Availability:** All courses have assignment pages

**Location:** Course Page → Find assignment links → Navigate to each

**Date format in HTML:**
```
Opens: Monday, 12 January 2026, 9:00 AM
Due: Wednesday, 4 March 2026, 9:00 AM
```

**Location in DOM:**
```html
<div data-region="completionrequirements">
    ...
    <div>Opens: Monday, 12 January 2026, 9:00 AM</div>
    <div>Due: Wednesday, 4 March 2026, 9:00 AM</div>
    ...
</div>
```

**Selector for assignment links:**
```python
soup.find_all("a", href=lambda h: h and "/mod/assign/" in h)
```

**Regex patterns for extraction (flexible):**
```python
# Captures: day number, month name, year + optional time
date_pattern = r"(?:[A-Za-z]+,?\s+)?(\d{1,2}\s+[A-Za-z]+\s+\d{4})(?:[,\s]+(\d{1,2}:\d{2}\s*(?:AM|PM)))?"

opens_match = re.search(r"Opens:\s*" + date_pattern, text, re.IGNORECASE)
due_match = re.search(r"Due:\s*" + date_pattern, text, re.IGNORECASE)
```

---

## 5. Reading List (`/mod/lti/view.php?id={lti_id}`)

External LTI tool (Leganto) for reading lists. Not relevant for date extraction.

---

## Scraping Strategy

### Complete approach for Phase 1:

```
1. Navigate to dashboard → Wait for SSO → User selects term
2. Extract course cards → Get course names and URLs
3. For each course:
   a. Navigate to course page

   b. SOURCE A: Check for Key Dates
      - Look for "Key dates" link under Key Resources
      - If found: navigate and extract dates from table
      - If not found: skip (not all courses have this)

   c. SOURCE B: Extract from Assignment Pages
      - Find all assignment links (/mod/assign/)
      - Navigate to each assignment page
      - Extract "Opens:" and "Due:" dates

   d. Merge dates from both sources
      - If conflict: prioritize Source B, flag for user

4. Parse all dates → Create calendar events
5. Show summary with any conflicts highlighted
6. Generate ICS on user confirmation
```

### Selectors summary:

| Purpose | Selector/Pattern |
|---------|------------------|
| Course cards | `.coursebox a.aalink, .course-card a` |
| Key dates link | `a` containing text "key dates" (case-insensitive) |
| Assignment links | `a[href*="/mod/assign/"]` |
| Completion requirements | `[data-region="completionrequirements"]` |
| Opens date | Text matching `Opens:\s*(.+)` |
| Due date | Text matching `Due:\s*(.+)` |

---

## Notes

- The site uses Moodle with Boost Union theme
- Content is largely server-rendered (not heavy SPA)
- Use `page.wait_for_load_state("networkidle")` for reliable scraping
- Some course structures may vary; handle missing elements gracefully
- **Always collect from both sources** — don't assume assignment pages have everything

---

## Example Courses (as of 2026-01-07, Lent term)

| Course | Has Key Dates? | Has Assignments? | Events Found |
|--------|----------------|------------------|--------------|
| MBA10 Strategy | ✅ Yes (15) | ✅ Yes (2) | 19 |
| MBA11 Marketing | ✅ Yes (14) | ✅ Yes (1) | 15 |
| MBA116 Digital Business | ✅ Yes (6) | ✅ Yes (1) | 8 |
| MBA12 Corporate Governance | ✅ Yes (15) | ✅ Yes (1) | 17 |
| MBA137 Data Science | ❌ No | ✅ Yes (1) | 2 |
| MBA14 Managing Innovation | ❌ No | ✅ Yes (1) | 2 |
| MBA33 Negotiations Lab | ✅ Yes (17) | ✅ Yes (1) | 19 |
| MBA34 Global Consulting | ❌ No | ✅ Yes (3) | 5 |
| MBA41 Energy and Emissions | ❌ No | ✅ Yes (1) | 2 |

This variability is why we must check both sources.
