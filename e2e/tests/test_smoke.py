"""Smoke checks: validate the environment and the test harness before the real flows."""

import pytest
from playwright.sync_api import Page, expect

from e2e.config.settings import Settings
from e2e.pages.dashboard_page import DashboardPage
from e2e.pages.login_page import LoginPage


@pytest.mark.smoke
def test_patient_can_log_in_through_the_ui(page: Page, settings: Settings) -> None:
    login_page = LoginPage(page, settings.web_url)
    login_page.open()

    login_page.login(settings.app_email, settings.app_password)

    dashboard = DashboardPage(page, settings.web_url)
    expect(page).to_have_url(dashboard.url)
    expect(dashboard.greeting).to_be_visible()


@pytest.mark.smoke
def test_authenticated_page_fixture_skips_login(
    authenticated_page: Page, settings: Settings
) -> None:
    dashboard = DashboardPage(authenticated_page, settings.web_url)
    dashboard.open()

    expect(authenticated_page).to_have_url(dashboard.url)
    expect(dashboard.next_appointment_section).to_be_visible()
