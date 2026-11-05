import random

import pytest
from playwright.sync_api import Page, expect

from config.settings import Settings
from messages import success_messages
from pages.appointments.new_appointment_page import NewAppointmentPage
from services.api_client import ApiClient
from utils.dates import days_from_today


@pytest.mark.booking
def test_book_appointment(
    authenticated_page: Page,
    settings: Settings,
    api: ApiClient,
    booking_notes: str,
) -> None:
    doctor = random.choice(api.get_doctors())
    day = days_from_today(random.randint(60, 260))
    time_slot = random.choice(api.get_available_slots(doctor.id, day))
    new_appointment_page = NewAppointmentPage(authenticated_page, settings.web_url)
    new_appointment_page.open()

    new_appointment_page.book(doctor.id, day.isoformat(), time_slot, booking_notes)

    expect(new_appointment_page.lbl_message(success_messages.APPOINTMENT_BOOKED)).to_be_visible()
    saved = api.find_appointment_by_notes(booking_notes)
    assert saved is not None
    assert saved.doctor_id == doctor.id
    assert saved.appointment_date == day
    assert saved.time_slot == time_slot
    assert saved.status == "active"
