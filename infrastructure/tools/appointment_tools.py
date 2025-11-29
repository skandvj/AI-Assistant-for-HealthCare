"""Appointment-related LangChain tools."""

from datetime import datetime
from typing import Optional
from langchain_core.tools import tool
from dateutil import parser

from application.services.appointment_service import AppointmentService


def create_appointment_tool(appointment_service: AppointmentService):
    """Create appointment tool."""
    
    async def create_appointment(
        patient_id: str,
        appointment_type: str,
        scheduled_time: str,
        emergency_details: Optional[str] = None
    ) -> str:
        """
        Create a new appointment for a patient.
        
        Args:
            patient_id: The patient's ID
            appointment_type: Type of appointment (cleaning, checkup, emergency)
            scheduled_time: ISO format datetime string (e.g., "2024-01-15T10:00:00")
            emergency_details: Details about emergency if appointment_type is emergency
        
        Returns:
            Appointment ID if successful, error message otherwise
        """
        try:
            scheduled_dt = parser.parse(scheduled_time)
            appointment = await appointment_service.create_appointment(
                patient_id=patient_id,
                appointment_type=appointment_type,
                scheduled_time=scheduled_dt,
                emergency_details=emergency_details
            )
            return f"Appointment created successfully! Appointment ID: {appointment.id}"
        except Exception as e:
            return f"Error creating appointment: {str(e)}"
    
    return tool(create_appointment)


def get_available_slots_tool(appointment_service: AppointmentService):
    """Get available slots tool."""
    
    async def get_available_slots(
        start_date: str,
        end_date: str,
        duration_minutes: int = 30
    ) -> str:
        """
        Get available appointment time slots.
        
        Args:
            start_date: Start date in ISO format (e.g., "2024-01-15")
            end_date: End date in ISO format (e.g., "2024-01-20")
            duration_minutes: Duration of appointment in minutes (default: 30)
        
        Returns:
            JSON string of available time slots
        """
        try:
            start_dt = parser.parse(start_date)
            end_dt = parser.parse(end_date)
            slots = await appointment_service.get_available_slots(
                start_date=start_dt,
                end_date=end_dt,
                duration_minutes=duration_minutes
            )
            slots_data = [
                {
                    "start_time": slot.start_time.isoformat(),
                    "end_time": slot.end_time.isoformat(),
                    "is_available": slot.is_available
                }
                for slot in slots
            ]
            import json
            return json.dumps(slots_data, indent=2)
        except Exception as e:
            return f"Error getting available slots: {str(e)}"
    
    return tool(get_available_slots)


def cancel_appointment_tool(appointment_service: AppointmentService):
    """Cancel appointment tool."""
    
    async def cancel_appointment(appointment_id: str) -> str:
        """
        Cancel an appointment.
        
        Args:
            appointment_id: The appointment ID to cancel
        
        Returns:
            Success or error message
        """
        try:
            success = await appointment_service.cancel_appointment(appointment_id)
            if success:
                return f"Appointment {appointment_id} cancelled successfully."
            else:
                return f"Could not cancel appointment {appointment_id}. It may not exist or cannot be cancelled."
        except Exception as e:
            return f"Error cancelling appointment: {str(e)}"
    
    return tool(cancel_appointment)


def reschedule_appointment_tool(appointment_service: AppointmentService):
    """Reschedule appointment tool."""
    
    async def reschedule_appointment(
        appointment_id: str,
        new_time: str
    ) -> str:
        """
        Reschedule an appointment to a new time.
        
        Args:
            appointment_id: The appointment ID to reschedule
            new_time: New scheduled time in ISO format (e.g., "2024-01-15T14:00:00")
        
        Returns:
            Success or error message
        """
        try:
            new_dt = parser.parse(new_time)
            appointment = await appointment_service.reschedule_appointment(
                appointment_id=appointment_id,
                new_time=new_dt
            )
            return f"Appointment rescheduled successfully to {new_dt.isoformat()}"
        except Exception as e:
            return f"Error rescheduling appointment: {str(e)}"
    
    return tool(reschedule_appointment)

