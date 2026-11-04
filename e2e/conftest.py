"""Shared pytest fixtures.

Authentication strategy: UI tests that are *not* about login authenticate via
the API and inject the token into localStorage (where the front-end stores it).
This keeps each test focused on its own flow and avoids repeating the login UI.
The login UI itself is covered by its own dedicated test.
"""

from collections.abc import Generator

import pytest
from playwright.sync_api import BrowserContext, Page, Playwright

from e2e.api.api_client import ApiClient
from e2e.config.settings import Settings


@pytest.fixture(scope="session")
def settings() -> Settings:
    return Settings.from_env()


@pytest.fixture(scope="session")
def base_url(settings: Settings) -> str:
    # Overrides pytest-base-url so page.goto("/path") works with relative paths.
    return settings.web_url


@pytest.fixture(scope="session")
def api(playwright: Playwright, settings: Settings) -> Generator[ApiClient, None, None]:
    client = ApiClient(playwright, settings.api_base_url)
    client.login(settings.app_email, settings.app_password)
    yield client
    client.dispose()


@pytest.fixture
def authenticated_page(context: BrowserContext, api: ApiClient) -> Page:
    """A page that is already logged in as the patient defined in .env."""
    context.add_init_script(f"window.localStorage.setItem('token', {api.token!r});")
    return context.new_page()
