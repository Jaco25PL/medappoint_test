import random
from datetime import date, timedelta

import pytest
from playwright.sync_api import Page, expect

from config.settings import Settings
from messages import error_messages, success_messages
from pages.appointments.appointments_page import AppointmentsPage
from services.api_client import ApiClient
from services.schemas import Appointment
from utils.dates import as_card_date, days_from_today


@pytest.mark.reschedule
@pytest.mark.title("Test reschedule to a free slot")
@pytest.mark.description("Verify the card and the saved appointment show the new date and time")
@pytest.mark.xfail(
    reason="BUG-04: The card keeps the old date and time after a reschedule", strict=True
)
def test_reschedule_to_free_slot(
    authenticated_page: Page,
    settings: Settings,
    api: ApiClient,
    future_appointment: Appointment,
) -> None:
    new_date = future_appointment.appointment_date + timedelta(days=1)
    new_time = random.choice(api.get_available_slots(future_appointment.doctor_id, new_date))
    appointments_page = AppointmentsPage(authenticated_page, settings.web_url)
    appointments_page.open()

    appointments_page.reschedule(future_appointment.notes, new_date.isoformat(), new_time)

    expect(appointments_page.lbl_message(success_messages.APPOINTMENT_RESCHEDULED)).to_be_visible()
    card = appointments_page.crd_appointment(future_appointment.notes)
    expect(card).to_contain_text(as_card_date(new_date))
    expect(card).to_contain_text(new_time)

    saved = api.get_appointment(future_appointment.id)
    assert saved.appointment_date == new_date
    assert saved.time_slot == new_time
    assert saved.doctor_id == future_appointment.doctor_id
    assert saved.notes == future_appointment.notes
    assert saved.updated_at != future_appointment.updated_at


@pytest.mark.reschedule
@pytest.mark.title("Test reschedule form required fields")
@pytest.mark.description(
    "Verify an empty date or time is blocked and the appointment does not change"
)
@pytest.mark.parametrize(
    ("new_date", "expected_error"),
    [
        pytest.param("", error_messages.REQUIRED_FIELD, id="empty_date"),
        pytest.param(
            days_from_today(300).isoformat(), error_messages.REQUIRED_OPTION, id="empty_time"
        ),
    ],
)
def test_reschedule_requires_date_and_time(
    authenticated_page: Page,
    settings: Settings,
    api: ApiClient,
    future_appointment: Appointment,
    new_date: str,
    expected_error: str,
) -> None:
    appointments_page = AppointmentsPage(authenticated_page, settings.web_url)
    appointments_page.open()

    appointments_page.fill_reschedule_form(future_appointment.notes, new_date, "")

    assert not appointments_page.confirm_sends_request()
    assert appointments_page.form_error() == expected_error
    assert api.get_appointment(future_appointment.id) == future_appointment


@pytest.mark.reschedule
@pytest.mark.title("Test reschedule to an invalid date")
@pytest.mark.description(
    "Verify past dates and year 1 are rejected and the appointment does not change"
)
@pytest.mark.parametrize(
    "new_date",
    [
        pytest.param(
            days_from_today(-3),
            id="past_date",
            marks=pytest.mark.xfail(reason="BUG-02: Past dates are accepted", strict=True),
        ),
        pytest.param(
            date(1, 1, 1),
            id="year_1",
            marks=pytest.mark.xfail(reason="BUG-02: Year 1 is accepted", strict=True),
        ),
    ],
)
def test_reschedule_rejects_invalid_date(
    authenticated_page: Page,
    settings: Settings,
    api: ApiClient,
    future_appointment: Appointment,
    new_date: date,
) -> None:
    new_time = random.choice(api.get_available_slots(future_appointment.doctor_id, new_date))
    appointments_page = AppointmentsPage(authenticated_page, settings.web_url)
    appointments_page.open()

    appointments_page.fill_reschedule_form(future_appointment.notes, new_date.isoformat(), new_time)

    assert not appointments_page.confirm_sends_request()
    assert api.get_appointment(future_appointment.id) == future_appointment
