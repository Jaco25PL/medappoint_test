from playwright.sync_api import Locator

from pages.base_page import BasePage


class LoginPage(BasePage):
    PATH = "/login"

    @property
    def txt_email(self) -> Locator:
        return self.page.get_by_label("Email")

    @property
    def txt_password(self) -> Locator:
        return self.page.get_by_label("Password")

    @property
    def btn_sign_in(self) -> Locator:
        return self.page.get_by_role("button", name="Sign In")

    def login(self, email: str, password: str) -> None:
        self.txt_email.fill(email)
        self.txt_password.fill(password)
        self.btn_sign_in.click()
