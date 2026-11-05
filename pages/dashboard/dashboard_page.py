import re

from playwright.sync_api import Locator

from pages.base_page import BasePage


class DashboardPage(BasePage):
    PATH = "/dashboard"

    @property
    def lbl_greeting(self) -> Locator:
        return self.page.get_by_role(
            "heading", name=re.compile(r"^Good (morning|afternoon|evening)")
        )

    @property
    def lbl_next_appointment(self) -> Locator:
        return self.page.get_by_role("heading", name="Your next appointment")

    @property
    def btn_logout(self) -> Locator:
        return self.page.get_by_role("button", name=re.compile("Logout"))
