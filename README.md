# MedAppoint QA Challenge

QA challenge for Light-it. User story under test:

"As a patient, I want to reschedule an existing appointment to another available time slot, without having to cancel and book from scratch."

## What's in this repo

- `docs/functional-testing-report.md` - Part 1: test strategy, test cases, bugs, improvements, go / no-go.
- `docs/exploratory-findings.md` - raw notes from exploring the database, API and web app. The report is built from these.
- `sql/queries.sql` - Part 2: SQL queries, each one commented.
- `postman/` - Part 3: Postman collection and environment.
- `e2e/` - Part 4: UI automation with Playwright + pytest.
- `AI_NOTES.md` - how AI was used and how its output was validated.

## Setup

You need Python 3.11+ and Node.js (only for running Postman from the command line).

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

Then fill in the credentials in `.env`. If a value has special characters (`#`, `!`), wrap it in single quotes.

If PowerShell blocks the activation script, run this once: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`.

The commands below (`pytest`, `ruff`, `npx`) are the same in both shells.

## Run the UI tests

```bash
pytest              # all tests
pytest -m smoke     # smoke tests only
pytest --headed     # see the browser
```

The report is saved to `reports/report.html`. If a test fails, a screenshot and a trace are saved in `reports/test-results/` (open the trace with `playwright show-trace <file>.zip`).

How the UI tests are built:
- Page Object Model: each page has a class in `e2e/pages/`. Tests only describe what the user does and what should happen.
- Tests log in through the API and reuse the token, so each test only covers its own flow. Login through the UI has its own test.
- Elements are found by role or label, the way a user sees them, not by CSS classes.
- No hardcoded URLs or credentials. Everything comes from `.env`.

## Run the Postman collection

In Postman: import both files from `postman/`, select the "MedAppoint - QA" environment, fill in `app_email` and `app_password`, and run the collection.

From the command line (single line, works in Bash and PowerShell):

```bash
npx newman run postman/medappoint.postman_collection.json -e postman/medappoint.postman_environment.json --env-var "app_email=<email>" --env-var "app_password=<password>"
```

If the password contains `!`, Bash may try to expand it inside double quotes. In Bash use single quotes instead: `--env-var 'app_password=<password>'`.

You never need to paste a token. Before each request, the collection checks for a saved token and logs in automatically if there is none or it is about to expire. The token is reused because the login endpoint has a rate limit (429).

## Code quality

```bash
ruff check .    # lint
ruff format .   # format
```
