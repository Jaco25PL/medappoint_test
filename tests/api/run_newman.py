"""Runs the Postman collection with Newman, taking the credentials from .env"""

import shutil
import subprocess
import sys
from pathlib import Path

from dotenv import dotenv_values

API_TESTS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = API_TESTS_DIR.parents[1]

env = dotenv_values(PROJECT_ROOT / ".env")
missing = [key for key in ("APP_EMAIL", "APP_PASSWORD") if not env.get(key)]
if missing:
    sys.exit(f"Missing in .env: {', '.join(missing)}")

npx = shutil.which("npx")
if not npx:
    sys.exit("npx not found. Install Node.js to run Newman")

command = [
    npx,
    "-y",
    "newman@6",
    "run",
    str(API_TESTS_DIR / "medappoint.postman_collection.json"),
    "-e",
    str(API_TESTS_DIR / "medappoint.postman_environment.json"),
    "--env-var",
    f"app_email={env['APP_EMAIL']}",
    "--env-var",
    f"app_password={env['APP_PASSWORD']}",
]
sys.exit(subprocess.run(command).returncode)
