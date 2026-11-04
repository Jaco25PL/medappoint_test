import re

from playwright.sync_api import Page

from e2e.pages.base_page import BasePage


class DashboardPage(BasePage):
    PATH = "/dashboard"

    def __init__(self, page: Page, base_url: str) -> None:
        super().__init__(page, base_url)
        self.greeting = page.get_by_role(
            "heading", name=re.compile(r"^Good (morning|afternoon|evening)")
        )
        self.next_appointment_section = page.get_by_role("heading", name="Your next appointment")
        self.logout_button = page.get_by_role("button", name=re.compile("Logout"))
