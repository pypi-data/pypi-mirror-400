# Polecat

A CLI tool that extracts exam dates, assignment deadlines, and quiz schedules from the Cambridge Judge Business School (JBS) learning platform and generates an `.ics` calendar file.

## Features

- Extracts dates from two sources:
  - **Key Dates table** (unit releases, live sessions, quiz opens/closes)
  - **Assignment pages** (submission deadlines)
- Filters to show only important deadlines by default
- Generates standard `.ics` files compatible with Google Calendar, Outlook, Apple Calendar
- Human-in-the-loop: you complete SSO login manually (no credentials stored)

## Requirements

- Python 3.10+
- A JBS learning platform account

## Installation

### Quick Install (Recommended)

```bash
pip install jbs-polecat
playwright install chromium
```

That's it! Now run `polecat` to start.

### Install from Source

For development or if you prefer to clone the repository:

```bash
git clone https://github.com/shoaib-akhter/polecat.git
cd polecat
pip install -e .
playwright install chromium
```

## Usage

```bash
polecat
```

### Steps

1. **Browser opens** - A Chromium browser window will open
2. **Login** - Complete SSO login manually in the browser
3. **Select term** - Use the dropdown to filter courses by term (e.g., "Lent")
4. **Press Enter** - Confirm in terminal once courses are visible
5. **Review dates** - Check the summary table in terminal
6. **Confirm** - Type `y` to proceed
7. **Filter options** - Choose what to include in calendar:
   - Assignment "Opens" dates (default: no)
   - Unit releases and live sessions (default: no)
8. **Done** - Calendar file saved as `JBS_Calendar_[Term]_[Year].ics`

### Example Output

```
Found 9 course(s):
  - MBA10 Strategy (2025/26)
  - MBA11 Marketing (2025/26)
  ...

Filtered: 30 event(s) will be saved to calendar

SUCCESS! Calendar file created:
  /path/to/JBS_Calendar_Lent_2026.ics
```

## What Gets Extracted

| Event Type | Included by Default |
|------------|---------------------|
| Assignment Due dates | Yes |
| Exam dates | Yes |
| Quiz Opens/Closes | Yes |
| Assignment Opens dates | No (opt-in) |
| Unit release dates | No (opt-in) |
| Live session dates | No (opt-in) |

## License

MIT
