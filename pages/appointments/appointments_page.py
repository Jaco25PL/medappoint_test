from playwright.sync_api import Locator
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from pages.base_page import BasePage


class AppointmentsPage(BasePage):
    PATH = "/appointments"

    @property
    def frm_reschedule(self) -> Locator:
        return self.page.locator("form").filter(has=self.page.get_by_role("button", name="Confirm"))

    # The "New Date" / "New Time" labels are not linked to their inputs,
    # so the fields are located inside the reschedule form instead of by label
    @property
    def txt_new_date(self) -> Locator:
        return self.frm_reschedule.locator("input[type=date]")

    @property
    def ddl_new_time(self) -> Locator:
        return self.frm_reschedule.locator("select")

    @property
    def btn_confirm(self) -> Locator:
        return self.frm_reschedule.get_by_role("button", name="Confirm")

    def crd_appointment(self, notes: str) -> Locator:
        # Cards have no id or test id, so each test gives its appointment unique notes
        # and the card is found by that text
        return (
            self.page.locator("div")
            .filter(has_text=notes)
            .filter(has=self.page.get_by_role("button", name="Reschedule"))
            .last
        )

    def lbl_message(self, text: str) -> Locator:
        return self.page.get_by_text(text)

    def fill_reschedule_form(self, notes: str, new_date: str, new_time: str) -> None:
        self.crd_appointment(notes).get_by_role("button", name="Reschedule").click()
        if new_date:
            self.txt_new_date.fill(new_date)
        if new_time:
            self.ddl_new_time.select_option(new_time)

    def reschedule(self, notes: str, new_date: str, new_time: str) -> None:
        self.fill_reschedule_form(notes, new_date, new_time)
        self.btn_confirm.click()

    def confirm_sends_request(self, timeout_ms: int = 3000) -> bool:
        # Negative tests need to prove that nothing was sent, so this waits a few seconds
        # for the reschedule request and returns False if it never goes out
        try:
            with self.page.expect_request(
                lambda request: request.method == "PUT" and "/reschedule" in request.url,
                timeout=timeout_ms,
            ):
                self.btn_confirm.click()
        except PlaywrightTimeoutError:
            return False
        return True

    def form_error(self) -> str:
        # The form uses native browser validation, so the message lives on the first invalid field
        return self.frm_reschedule.evaluate(
            "form => [...form.elements].find(f => !f.validity.valid)?.validationMessage ?? ''"
        )
