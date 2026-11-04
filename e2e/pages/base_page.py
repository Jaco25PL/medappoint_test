"""Base class for all Page Objects.

Page Objects expose user-level actions and locators. Assertions live in the
tests (or in explicit `expect_*` helpers) so pages stay reusable.
"""

from playwright.sync_api import Page


class BasePage:
    PATH: str = "/"

    def __init__(self, page: Page, base_url: str) -> None:
        self.page = page
        self.base_url = base_url

    @property
    def url(self) -> str:
        return f"{self.base_url}{self.PATH}"

    def open(self) -> "BasePage":
        self.page.goto(self.url)
        return self
