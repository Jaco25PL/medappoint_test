import pytest
from playwright.sync_api import Page, expect

from config.settings import Settings
from pages.auth.login_page import LoginPage
from pages.dashboard.dashboard_page import DashboardPage


@pytest.mark.smoke
def test_patient_can_log_in_through_the_ui(page: Page, settings: Settings) -> None:
    login_page = LoginPage(page, settings.web_url)
    login_page.open()

    login_page.login(settings.app_email, settings.app_password)

    dashboard = DashboardPage(page, settings.web_url)
    expect(page).to_have_url(dashboard.url)
    expect(dashboard.lbl_greeting).to_be_visible()


@pytest.mark.smoke
def test_authenticated_page_fixture_skips_login(
    authenticated_page: Page, settings: Settings
) -> None:
    dashboard = DashboardPage(authenticated_page, settings.web_url)
    dashboard.open()

    expect(authenticated_page).to_have_url(dashboard.url)
    expect(dashboard.lbl_next_appointment).to_be_visible()
