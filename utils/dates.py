from datetime import date, timedelta


def days_from_today(days: int) -> date:
    return date.today() + timedelta(days=days)


def as_card_date(value: date) -> str:
    # Appointment cards show dates as day/month/year without leading zeros (e.g. "18/1/2027").
    return f"{value.day}/{value.month}/{value.year}"
