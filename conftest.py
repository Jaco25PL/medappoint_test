"""Shared pytest fixtures.

UI tests that are not about login authenticate through the API and inject the
token into localStorage, where the front-end keeps it. Test data is created
through the API before each test and deleted afterwards.
"""

import logging
import random
import uuid
from collections.abc import Generator

import pytest
from playwright.sync_api import BrowserContext, Page, Playwright

from config.settings import Settings
from services.api_client import ApiClient
from services.schemas import Appointment, CreateAppointmentRequest
from utils.dates import days_from_today

logger = logging.getLogger(__name__)

# The app shows dates in the browser's local time, so a fixed timezone keeps
# results the same on any machine (the patients of this clinic are in GMT-3)
TIMEZONE = "America/Montevideo"
# Native validation messages follow the browser language, which in headed mode comes
# from the OS. A fixed language keeps them the same on any machine
LANGUAGE = "en-US"


@pytest.fixture(scope="session")
def settings() -> Settings:
    return Settings.from_env()


@pytest.fixture(scope="session")
def base_url(settings: Settings) -> str:
    return settings.web_url


@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args: dict) -> dict:
    args = [*browser_type_launch_args.get("args", []), f"--lang={LANGUAGE}"]
    return {**browser_type_launch_args, "args": args}


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args: dict) -> dict:
    return {**browser_context_args, "timezone_id": TIMEZONE, "locale": LANGUAGE}


@pytest.fixture(scope="session")
def api(playwright: Playwright, settings: Settings) -> Generator[ApiClient, None, None]:
    client = ApiClient(playwright, settings.api_base_url)
    client.login(settings.app_email, settings.app_password)
    yield client
    client.dispose()


@pytest.fixture
def authenticated_page(context: BrowserContext, api: ApiClient) -> Page:
    context.add_init_script(f"window.localStorage.setItem('token', {api.token!r});")
    return context.new_page()


@pytest.fixture
def future_appointment(api: ApiClient) -> Generator[Appointment, None, None]:
    # Doctor, date and slot are picked at random and logged, so a failure can be reproduced.
    # A random date far ahead also lowers the chance of hitting another candidate's booking
    # in the shared database. Unique notes identify the card in the UI
    doctor = random.choice(api.get_doctors())
    day = days_from_today(random.randint(60, 260))
    request = CreateAppointmentRequest(
        doctor_id=doctor.id,
        appointment_date=day.isoformat(),
        time_slot=random.choice(api.get_available_slots(doctor.id, day)),
        notes=f"qa-auto-{uuid.uuid4().hex[:8]}",
    )
    appointment = api.create_appointment(request)
    logger.info("Created %s", appointment)
    yield appointment
    api.delete_appointment(appointment.id)


@pytest.fixture
def booking_notes(api: ApiClient) -> Generator[str, None, None]:
    # The appointment is created by the UI, so it is found by its unique notes to delete it
    notes = f"qa-auto-{uuid.uuid4().hex[:8]}"
    yield notes
    appointment = api.find_appointment_by_notes(notes)
    if appointment:
        api.delete_appointment(appointment.id)
