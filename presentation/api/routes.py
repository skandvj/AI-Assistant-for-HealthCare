"""FastAPI routes for the chatbot API."""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List

from application.graph.conversation_graph import create_conversation_graph, process_message
from application.services.patient_service import PatientService
from application.services.appointment_service import AppointmentService
from infrastructure.database import JSONPatientRepository, JSONAppointmentRepository


# Dependency injection for services
def get_patient_service() -> PatientService:
    """Get patient service instance."""
    repository = JSONPatientRepository()
    return PatientService(repository)


def get_appointment_service() -> AppointmentService:
    """Get appointment service instance."""
    patient_repo = JSONPatientRepository()
    appointment_repo = JSONAppointmentRepository()
    return AppointmentService(appointment_repo, patient_repo)


def get_conversation_graph():
    """Get conversation graph instance."""
    patient_service = get_patient_service()
    appointment_service = get_appointment_service()
    return create_conversation_graph(patient_service, appointment_service)


# Request/Response models
class ChatMessage(BaseModel):
    """Chat message model."""
    role: str
    content: str


class ChatRequest(BaseModel):
    """Chat request model."""
    message: str
    conversation_history: Optional[List[ChatMessage]] = None


class ChatResponse(BaseModel):
    """Chat response model."""
    response: str
    patient_id: Optional[str] = None
    appointment_ids: List[str] = []
    conversation_state: dict = {}
    requires_human: bool = False


# Router
router = APIRouter(prefix="/api", tags=["chatbot"])


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    patient_service: PatientService = Depends(get_patient_service),
    appointment_service: AppointmentService = Depends(get_appointment_service)
):
    """
    Process a chat message and return response.
    
    This endpoint handles all conversation interactions with the chatbot.
    """
    try:
        graph = create_conversation_graph(patient_service, appointment_service)
        
        # Convert conversation history
        history = None
        if request.conversation_history:
            history = [{"role": msg.role, "content": msg.content} for msg in request.conversation_history]
        
        # Process message
        result = await process_message(graph, request.message, history)
        
        return ChatResponse(**result)
    
    except ValueError as e:
        # Handle API key or configuration errors
        error_msg = str(e)
        if "API key" in error_msg or "not found" in error_msg.lower():
            raise HTTPException(
                status_code=400,
                detail="LLM service configuration error. Please check your API key in .env file."
            )
        raise HTTPException(status_code=500, detail=f"Configuration error: {error_msg}")
    except Exception as e:
        error_str = str(e)
        # Provide user-friendly error messages
        if "Insufficient Balance" in error_str or "402" in error_str:
            raise HTTPException(
                status_code=402,
                detail="Your API account has insufficient balance. Please add credits to your API account."
            )
        elif "401" in error_str or "Authentication" in error_str:
            raise HTTPException(
                status_code=401,
                detail="API authentication failed. Please check your API key is valid."
            )
        else:
            # Log the full error but return a friendly message
            import logging
            logging.error(f"Chat error: {error_str}")
            # Return a proper response instead of raising exception for better UX
            return ChatResponse(
                response="I'm having trouble connecting to our AI service right now. This might be due to API service issues. Please try again in a moment, or contact us directly at +1-555-0123.",
                patient_id=None,
                appointment_ids=[],
                conversation_state={},
                requires_human=False
            )


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "dental-chatbot"}


@router.get("/test")
async def test_endpoint():
    """Simple test endpoint to verify API connectivity."""
    return {
        "status": "ok",
        "message": "API is working!",
        "timestamp": "now"
    }

