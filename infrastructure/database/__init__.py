"""Database implementations."""

from .repository import PatientRepository, AppointmentRepository
from .json_repository import JSONPatientRepository, JSONAppointmentRepository

__all__ = [
    "PatientRepository",
    "AppointmentRepository",
    "JSONPatientRepository",
    "JSONAppointmentRepository",
]

