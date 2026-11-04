# AI Notes

How AI was used in this challenge and how its output was checked.

Tool: Claude Code.

What I used it for:
- Setting up the project faster: folder structure, Page Object base classes, pytest fixtures, env config, Postman auth script.
- Reading the Swagger spec and the app to map endpoints and routes.
- Exploring the database: schema, relations, appointment states and data anomalies (read-only queries).

What I decided myself:
- Stack (Python, pytest, Playwright, Page Object Model), one repo for everything, logging in through the API in UI tests, caching the token in Postman.
- How to split the exploration: AI explored the database while I explored the web app by hand, so both happened in parallel and the app exploration stayed my own first-hand experience.

How I validated it:
- Read and reviewed every file before keeping it.
- Ran everything against the real environment: pytest (UI smoke tests), Newman (Postman collection), ruff (lint).
- Tested pieces on their own, not only the full happy path.
- Checked the key database findings myself in DBeaver (my appointments, the inactive doctor, the double-booked slot) before using them in the test strategy.

