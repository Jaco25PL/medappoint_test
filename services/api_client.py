"""API client used by the UI tests for setup, teardown and backend checks."""

from datetime import date

from playwright.sync_api import APIRequestContext, APIResponse, Playwright

from services import endpoints
from services.schemas import (
    Appointment,
    CreateAppointmentRequest,
    Doctor,
    RescheduleRequest,
)


class ApiClient:
    def __init__(self, playwright: Playwright, base_url: str) -> None:
        self._playwright = playwright
        self._base_url = base_url
        self._context: APIRequestContext = playwright.request.new_context(base_url=base_url)
        self._token: str | None = None

    @property
    def token(self) -> str:
        if self._token is None:
            raise RuntimeError("ApiClient is not authenticated. Call login() first.")
        return self._token

    def login(self, email: str, password: str) -> str:
        response = self._context.post(endpoints.LOGIN, data={"email": email, "password": password})
        assert response.ok, f"Login failed: {response.status} {response.text()}"
        self._token = response.json()["token"]

        # Re-create the context so every following request carries the token.
        self._context.dispose()
        self._context = self._playwright.request.new_context(
            base_url=self._base_url,
            extra_http_headers={"Authorization": f"Bearer {self._token}"},
        )
        return self._token

    def get_doctors(self) -> list[Doctor]:
        response = self._context.get(endpoints.DOCTORS)
        assert response.ok, f"Get doctors failed: {response.status} {response.text()}"
        return [Doctor.from_json(doctor) for doctor in response.json()]

    def get_available_slots(self, doctor_id: int, day: date) -> list[str]:
        response = self._context.get(
            endpoints.DOCTOR_AVAILABILITY.format(id=doctor_id), params={"date": day.isoformat()}
        )
        assert response.ok, f"Get availability failed: {response.status} {response.text()}"
        return response.json()["time_slots"]

    def create_appointment(self, request: CreateAppointmentRequest) -> Appointment:
        response = self._context.post(endpoints.APPOINTMENTS, data=request.to_json())
        assert response.status == 201, f"Create failed: {response.status} {response.text()}"
        return Appointment.from_json(response.json())

    def get_appointments(self) -> list[Appointment]:
        response = self._context.get(endpoints.APPOINTMENTS)
        assert response.ok, f"Get appointments failed: {response.status} {response.text()}"
        return [Appointment.from_json(appointment) for appointment in response.json()]

    def find_appointment_by_notes(self, notes: str) -> Appointment | None:
        return next((a for a in self.get_appointments() if a.notes == notes), None)

    def get_appointment(self, appointment_id: int) -> Appointment:
        response = self.get_appointment_response(appointment_id)
        assert response.ok, f"Get failed: {response.status} {response.text()}"
        return Appointment.from_json(response.json())

    def get_appointment_response(self, appointment_id: int) -> APIResponse:
        return self._context.get(endpoints.APPOINTMENT.format(id=appointment_id))

    def reschedule_appointment(
        self, appointment_id: int, request: RescheduleRequest
    ) -> APIResponse:
        return self._context.put(
            endpoints.RESCHEDULE_APPOINTMENT.format(id=appointment_id), data=request.to_json()
        )

    def cancel_appointment(self, appointment_id: int) -> APIResponse:
        return self._context.put(endpoints.CANCEL_APPOINTMENT.format(id=appointment_id))

    def delete_appointment(self, appointment_id: int) -> APIResponse:
        return self._context.delete(endpoints.APPOINTMENT.format(id=appointment_id))

    def dispose(self) -> None:
        self._context.dispose()
