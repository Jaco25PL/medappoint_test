from playwright.sync_api import Locator

from pages.base_page import BasePage


class NewAppointmentPage(BasePage):
    PATH = "/appointments/new"

    @property
    def ddl_doctor(self) -> Locator:
        return self.page.get_by_label("Doctor")

    @property
    def txt_date(self) -> Locator:
        return self.page.get_by_label("Date")

    @property
    def ddl_time_slot(self) -> Locator:
        return self.page.get_by_label("Time Slot")

    @property
    def txt_notes(self) -> Locator:
        return self.page.get_by_label("Notes (optional)")

    @property
    def btn_book(self) -> Locator:
        return self.page.get_by_test_id("submit-appointment")

    def lbl_message(self, text: str) -> Locator:
        return self.page.get_by_text(text)

    def book(self, doctor_id: int, date: str, time_slot: str, notes: str) -> None:
        self.ddl_doctor.select_option(str(doctor_id))
        self.txt_date.fill(date)
        self.ddl_time_slot.select_option(time_slot)
        self.txt_notes.fill(notes)
        self.btn_book.click()
