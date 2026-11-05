from dataclasses import asdict, dataclass
from datetime import date


@dataclass(frozen=True)
class CreateAppointmentRequest:
    doctor_id: int
    appointment_date: str
    time_slot: str
    notes: str = ""

    def to_json(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class RescheduleRequest:
    appointment_date: str
    time_slot: str

    def to_json(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class Doctor:
    id: int
    first_name: str
    last_name: str
    specialty: str

    @classmethod
    def from_json(cls, data: dict) -> "Doctor":
        return cls(
            id=data["id"],
            first_name=data["first_name"],
            last_name=data["last_name"],
            specialty=data["specialty"],
        )


@dataclass(frozen=True)
class Appointment:
    id: int
    patient_id: int
    doctor_id: int
    appointment_date: date
    time_slot: str
    status: str
    notes: str | None
    created_at: str
    updated_at: str

    @classmethod
    def from_json(cls, data: dict) -> "Appointment":
        # The API returns dates as UTC midnight timestamps ("2027-01-18T00:00:00.000Z"),
        # so only the date part is kept.
        return cls(
            id=data["id"],
            patient_id=data["patient_id"],
            doctor_id=data["doctor_id"],
            appointment_date=date.fromisoformat(data["appointment_date"][:10]),
            time_slot=data["time_slot"],
            status=data["status"],
            notes=data.get("notes"),
            created_at=data["created_at"],
            updated_at=data["updated_at"],
        )
