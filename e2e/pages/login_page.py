from playwright.sync_api import Page

from e2e.pages.base_page import BasePage


class LoginPage(BasePage):
    PATH = "/login"

    def __init__(self, page: Page, base_url: str) -> None:
        super().__init__(page, base_url)
        self.email_input = page.get_by_label("Email")
        self.password_input = page.get_by_label("Password")
        self.sign_in_button = page.get_by_role("button", name="Sign In")

    def login(self, email: str, password: str) -> None:
        self.email_input.fill(email)
        self.password_input.fill(password)
        self.sign_in_button.click()
