from playwright.sync_api import Page


class BasePage:
    PATH: str = "/"

    def __init__(self, page: Page, base_url: str) -> None:
        self.page = page
        self.base_url = base_url

    @property
    def url(self) -> str:
        return f"{self.base_url}{self.PATH}"

    def open(self) -> None:
        self.page.goto(self.url)
