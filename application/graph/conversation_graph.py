"""LangGraph conversation state machine implementation."""

from typing import Literal, TypedDict, Annotated, Optional
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from dateutil import parser
import json

from domain.value_objects.conversation_state import ConversationIntent
from infrastructure.llm import create_llm_provider
from infrastructure.tools import (
    create_appointment_tool,
    get_available_slots_tool,
    cancel_appointment_tool,
    reschedule_appointment_tool,
    create_patient_tool,
    get_patient_tool,
    verify_patient_tool,
)
from application.services.patient_service import PatientService
from application.services.appointment_service import AppointmentService


class GraphState(TypedDict):
    """Graph state definition."""
    messages: Annotated[list, add_messages]
    conversation_state: dict
    intent: str
    patient_id: Optional[str]
    appointment_ids: list
    collected_data: dict
    current_step: Optional[str]
    requires_human: bool


def create_conversation_graph(
    patient_service: PatientService,
    appointment_service: AppointmentService
) -> StateGraph:
    """Create the conversation graph."""
    
    # Create LLM provider with automatic fallback
    try:
        llm_provider = create_llm_provider(use_fallback=True)
    except Exception as e:
        print(f"[Graph] Fallback provider creation failed: {e}")
        # If fallback fails, try without fallback
        try:
            llm_provider = create_llm_provider(use_fallback=False)
        except:
            raise ValueError("Could not initialize any LLM provider. Please check your API keys.")
    
    # Store provider for fallback use
    global _llm_provider
    _llm_provider = llm_provider
    
    llm = llm_provider.get_chat_model()
    
    # Set temperature for more natural, conversational responses
    if hasattr(llm, 'temperature'):
        llm.temperature = 0.8  # Higher for more natural conversation
    
    # Create tools
    tools = [
        create_patient_tool(patient_service),
        get_patient_tool(patient_service),
        verify_patient_tool(patient_service),
        create_appointment_tool(appointment_service),
        get_available_slots_tool(appointment_service),
        cancel_appointment_tool(appointment_service),
        reschedule_appointment_tool(appointment_service),
    ]
    
    # Bind tools to LLM
    llm_with_tools = llm.bind_tools(tools)
    
    # Create tool node
    tool_node = ToolNode(tools)
    
    # System prompt - Enhanced for better understanding and user-friendly responses
    SYSTEM_PROMPT = """You are a warm, friendly, and highly intelligent dental practice assistant for Premium Dental Care. Your goal is to make every interaction feel natural, helpful, and easy for patients.

CORE PRINCIPLES:
- Understand what patients REALLY want, even if they don't say it directly
- Respond in simple, clear language that anyone can understand
- Be conversational and natural - like talking to a helpful friend
- Show empathy and care, especially for emergencies or concerns
- Break down complex information into easy-to-understand steps

UNDERSTANDING USER INTENT:
- If someone says "I need an appointment" → They want to schedule
- If they mention pain, emergency, urgent → Treat as emergency immediately
- If they ask about hours, location, insurance → Provide clear, concise answers
- If they're vague ("sometime next week") → Help them pick a specific time
- If they mention family/kids/spouse → Offer to book multiple appointments
- If they seem confused → Explain things step-by-step, ask clarifying questions

CONVERSATION STYLE:
- Use everyday language, avoid medical jargon
- Ask one question at a time to avoid overwhelming
- Confirm understanding: "So you'd like to book a cleaning for next Tuesday at 2pm, is that right?"
- Be proactive: "Would you like me to check what times are available this week?"
- Show personality: Use natural expressions, be warm and approachable

INFORMATION TO COLLECT (for new patients):
- Full name
- Phone number (can accept various formats)
- Date of birth (accept "MM/DD/YYYY", "January 15, 1990", etc.)
- Insurance information (if they have it)

APPOINTMENT HANDLING:
- Practice hours: Monday-Saturday, 8am-6pm
- Appointment types: Cleaning, Checkup, Emergency
- For emergencies: Get details, reassure them staff is notified
- If requested time isn't available: Suggest 2-3 alternatives immediately
- Handle vague dates: "later next week" → suggest specific days/times
- Family bookings: Offer back-to-back appointments when possible

INSURANCE & PAYMENT:
- Accept all major dental insurance plans
- No insurance? Explain: "We have self-pay options and membership plans available. Would you like to hear about those?"
- Keep it simple and non-intimidating

TOOLS AVAILABLE:
- verify_patient: Check if patient exists by phone
- create_patient: Register new patient
- get_available_slots: Find appointment times
- create_appointment: Book appointment
- cancel_appointment: Cancel existing
- reschedule_appointment: Change appointment time

IMPORTANT:
- Always use tools when you need to perform actions (don't just say you'll do it)
- If you don't understand something, ask for clarification in a friendly way
- If something goes wrong, explain it simply and offer alternatives
- Make patients feel heard, valued, and taken care of

Remember: Your job is to make dental care accessible and stress-free. Be the helpful assistant that makes their day easier."""

    def should_continue(state: GraphState) -> Literal["tools", "end"]:
        """Determine if we should continue to tools or end."""
        messages = state["messages"]
        last_message = messages[-1]
        
        # If the last message has tool calls, route to tools
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "tools"
        return "end"
    
    async def call_model(state: GraphState) -> GraphState:
        """Call the LLM model with enhanced context understanding and fallback."""
        messages = state["messages"]
        conversation_state = state.get("conversation_state", {})
        
        # Add system message if not present
        if not any(isinstance(msg, SystemMessage) for msg in messages):
            messages = [SystemMessage(content=SYSTEM_PROMPT)] + messages
        
        # Enhance context with conversation state if available
        if conversation_state:
            context_note = f"\n\n[Context: {conversation_state}]"
            # Add context to the last user message if it exists
            if messages and isinstance(messages[-1], HumanMessage):
                messages[-1].content += context_note
        
        # Call LLM with fallback handling
        try:
            response = await llm_with_tools.ainvoke(messages)
        except Exception as e:
            error_str = str(e)
            print(f"[Graph] LLM call failed: {error_str[:200]}")
            
            # If using FallbackLLMProvider, it should handle fallback internally
            # But if we get here, the error happened at LangChain level
            # Try to use fallback provider directly
            if hasattr(llm_provider, 'fallback_providers') and llm_provider.fallback_providers:
                print(f"[Graph] Attempting fallback providers...")
                for i, fallback_provider in enumerate(llm_provider.fallback_providers):
                    try:
                        print(f"[Graph] Trying fallback {i+1}: {type(fallback_provider).__name__}")
                        fallback_llm = fallback_provider.get_chat_model()
                        if hasattr(fallback_llm, 'temperature'):
                            fallback_llm.temperature = 0.8
                        fallback_llm_with_tools = fallback_llm.bind_tools(tools)
                        response = await fallback_llm_with_tools.ainvoke(messages)
                        print(f"[Graph] ✓ Fallback {i+1} succeeded!")
                        break
                    except Exception as fallback_error:
                        print(f"[Graph] ✗ Fallback {i+1} failed: {str(fallback_error)[:150]}")
                        continue
                else:
                    # All fallbacks failed
                    from langchain_core.messages import AIMessage
                    error_msg = AIMessage(
                        content="I'm having trouble connecting to our AI service right now. Please try again in a moment, or contact us directly at +1-555-0123."
                    )
                    return {
                        **state,
                        "messages": [error_msg]
                    }
            else:
                # Not using fallback provider, return error
                from langchain_core.messages import AIMessage
                error_msg = AIMessage(
                    content="I'm having trouble connecting to our AI service right now. Please try again in a moment, or contact us directly at +1-555-0123."
                )
                return {
                    **state,
                    "messages": [error_msg]
                }
        
        return {
            **state,
            "messages": [response]
        }
    
    async def call_tools(state: GraphState) -> GraphState:
        """Call tools and update state."""
        result = await tool_node.ainvoke(state)
        
        # Update state based on tool results
        updated_state = {**state, "messages": result["messages"]}
        
        # Extract patient_id and appointment_ids from tool results if present
        for msg in result["messages"]:
            if hasattr(msg, "content"):
                content = str(msg.content)
                # Try to extract patient ID
                if "Patient ID:" in content:
                    try:
                        patient_id = content.split("Patient ID:")[1].split()[0].strip()
                        updated_state["patient_id"] = patient_id
                    except:
                        pass
                # Try to extract appointment ID
                if "Appointment ID:" in content:
                    try:
                        apt_id = content.split("Appointment ID:")[1].split()[0].strip()
                        if apt_id not in updated_state.get("appointment_ids", []):
                            updated_state["appointment_ids"] = updated_state.get("appointment_ids", []) + [apt_id]
                    except:
                        pass
        
        return updated_state
    
    # Build graph
    workflow = StateGraph(GraphState)
    
    # Add nodes
    workflow.add_node("agent", call_model)
    workflow.add_node("tools", call_tools)
    
    # Set entry point
    workflow.set_entry_point("agent")
    
    # Add conditional edges
    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            "tools": "tools",
            "end": END
        }
    )
    
    # Add edge from tools back to agent
    workflow.add_edge("tools", "agent")
    
    return workflow.compile()


async def process_message(
    graph: StateGraph,
    user_message: str,
    conversation_history: list[dict] = None
) -> dict:
    """Process a user message through the graph."""
    
    if conversation_history is None:
        conversation_history = []
    
    # Convert history to LangChain messages
    messages = []
    for msg in conversation_history:
        if msg["role"] == "user":
            messages.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            messages.append(AIMessage(content=msg["content"]))
    
    # Add current user message
    messages.append(HumanMessage(content=user_message))
    
    # Initial state
    initial_state = {
        "messages": messages,
        "conversation_state": {},
        "intent": ConversationIntent.UNKNOWN.value,
        "patient_id": None,
        "appointment_ids": [],
        "collected_data": {},
        "current_step": None,
        "requires_human": False
    }
    
    # Run graph
    final_state = await graph.ainvoke(initial_state)
    
    # Extract response
    response_messages = final_state["messages"]
    assistant_message = None
    
    for msg in reversed(response_messages):
        if isinstance(msg, AIMessage):
            assistant_message = msg.content
            break
    
    if not assistant_message:
        # More friendly fallback message
        assistant_message = "I'm sorry, I didn't quite catch that. Could you tell me what you need help with? I'm here to help with appointments, questions about our practice, or anything else you need!"
    
    return {
        "response": assistant_message,
        "patient_id": final_state.get("patient_id"),
        "appointment_ids": final_state.get("appointment_ids", []),
        "conversation_state": final_state.get("conversation_state", {}),
        "requires_human": final_state.get("requires_human", False)
    }

