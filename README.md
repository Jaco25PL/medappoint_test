# MedAppoint QA Challenge

QA challenge for Light-it. User story under test:

"As a patient, I want to reschedule an existing appointment to another available time slot, without having to cancel and book from scratch."

## What's in this repo

- `docs/Functional-Testing-Report-Reschedule.pdf` - Part 1: test strategy, test cases, bugs, improvements, go / no-go
- `docs/exploratory-findings.md` - raw notes from exploring the database, API and web app. The report is built from these
- `sql/queries.sql` - Part 2: SQL queries, each one commented
- `tests/api/` - Part 3: Postman collection and environment
- `tests/ui/` - Part 4: UI automation with Playwright + pytest
- `AI_NOTES.md` - how AI was used and how its output was validated

## Project structure

```
tests/
  ui/          UI tests (pytest + Playwright), one folder per feature
  api/         API tests (Postman collection + environment)
pages/         page objects, one class per page, same feature folders as the tests
services/      API client used by the UI tests for setup, teardown and backend checks
config/        settings loaded from .env
messages/      success and error messages the tests expect
utils/         small helpers (dates)
conftest.py    shared fixtures (login, test data)
sql/           Part 2 queries
docs/          report, exploratory findings and bugs
```

## Setup

You need Python 3.11+ and Node.js (only for running Postman from the command line)

Bash (macOS / Linux / Git Bash):

```bash
python -m venv .venv
source .venv/bin/activate        # Git Bash on Windows: source .venv/Scripts/activate
pip install -r requirements.txt
playwright install chromium
cp .env.example .env
```

PowerShell (Windows):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
playwright install chromium
Copy-Item .env.example .env
```

Then fill in the credentials in `.env`. If a value has special characters (`#`, `!`), wrap it in single quotes

If PowerShell blocks the activation script, run this once: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`

The commands below (`pytest`, `ruff`, `npx`) are the same in both shells

## Run the UI tests

The three flows covered:
1. Log in through the UI (`tests/ui/auth/`)
2. Book an appointment (`tests/ui/appointments/test_book_appointment.py`)
3. Reschedule an appointment, including form validation and invalid dates (`tests/ui/appointments/test_reschedule.py`)

```bash
pytest              # all tests
pytest -m smoke     # smoke tests only
pytest -m booking   # booking tests only
pytest --headed     # see the browser
```

The report is saved to `reports/report.html`. If a test fails, a screenshot and a trace are saved in `reports/test-results/` (open the trace with `playwright show-trace <file>.zip`)

How the UI tests are built:
- Page Object Model: each page has a class in `pages/`. Tests only describe what the user does and what should happen
- Tests log in through the API and reuse the token, so each test only covers its own flow. Login through the UI has its own test
- Each test creates its own appointment through the API and deletes it at the end. Doctor, date and time are picked at random from the API and logged, so a failure can be reproduced
- After acting in the UI, tests check the backend with a GET, so a UI that says "success" but saved nothing is caught
- Elements are found by role or label, the way a user sees them, not by CSS classes
- No hardcoded URLs, credentials or messages. URLs and credentials come from `.env` and messages from `messages/`
- Tests that fail because of a known bug are marked `xfail` with the bug as the reason. They show up as "xfailed" in the report, and if the bug gets fixed the test fails on purpose so the mark gets removed

### Element naming convention

Page elements use a prefix that tells what kind of element they are. To add a new element, follow the same prefixes

| Prefix | Element | Example |
|---|---|---|
| `btn_` | button | `btn_confirm` |
| `txt_` | text, date, email or password input | `txt_new_date` |
| `ddl_` | dropdown / select | `ddl_new_time` |
| `rdo_` | radio button | `rdo_gender` |
| `chk_` | checkbox | `chk_remember_me` |
| `lnk_` | link | `lnk_appointments` |
| `lbl_` | text, heading or message | `lbl_greeting` |
| `frm_` | form or section | `frm_reschedule` |
| `crd_` | card in a list | `crd_appointment` |

## Run the Postman collection

In Postman: import both files from `tests/api/`, select the "MedAppoint - QA" environment, fill in `app_email` and `app_password`, and run the whole collection in order

From the command line with Newman (needs Node.js, `npx` downloads Newman the first time)

Same command in Bash and PowerShell:

```bash
npx newman run tests/api/medappoint.postman_collection.json -e tests/api/medappoint.postman_environment.json --env-var 'app_email=<email>' --env-var 'app_password=<password>'
```

Use single quotes around the values in both shells, so characters like `!`, `#` or `$` in the password are not changed by the shell

You never need to paste a token. Before each request, the collection checks for a saved token and logs in automatically if there is none or it is about to expire. The token is reused because the login endpoint has a rate limit (429)

What the collection does:

| Folder | What it covers |
|---|---|
| `00 - Auth` | Login and current user |
| `01 - Setup` | Picks a random active doctor, date and free slot from the API and creates a new appointment for this run |
| `02 - Reschedule (happy path)` | Reschedules it and checks with a GET that the change was really saved |
| `03 - Edge cases` | One case per risk: past date, invalid date, invalid time slot, missing field, a taken slot, another patient's appointment, an appointment that does not exist, no token. After each one the appointment is read again to check it did not change |
| `04 - Appointment states` | Tries to reschedule a cancelled appointment, a completed one and one with an inactive doctor |
| `99 - Cleanup` | Deletes everything the run created |

Not covered, with more time: year 0001, February 30, a slot that already passed today, a slot outside the doctor hours, a slot with only spaces, SQL injection text in the slot, malformed JSON and an id bigger than the database allows. They were tried by hand during exploration, results in `docs/exploratory-findings.md`

Some tests fail on purpose: each failing test is a bug in the API (see `docs/Functional-Testing-Report-Reschedule.pdf`). A green run is not the goal, the goal is that every failure points to a real problem

## CI

`.github/workflows/tests.yml` runs on every push to main (and by hand from the Actions tab): ruff, the UI tests and the Postman collection, in two parallel jobs

It needs two repository secrets (Settings > Secrets and variables > Actions): `APP_EMAIL` and `APP_PASSWORD`

The UI test report is saved as an artifact of the run. The Postman job fails on purpose while the known bugs are open, each failing assertion is a bug

## Code quality

```bash
ruff check .    # lint
ruff format .   # format
```
