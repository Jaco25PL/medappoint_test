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
