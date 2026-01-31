"""Main FastAPI application for GST CA Copilot backend."""
from fastapi import FastAPI, HTTPException, status, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from config import settings
from models import ChatRequest, ChatResponse, ChatMessage
from services.supabase_service import supabase_service
from services.ai_service import AIService
from services.a2ui_service import parse_a2ui_action, A2UIBuilder, create_response_with_a2ui

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize services
ai_service = AIService()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown events."""
    logger.info("Starting GST CA Copilot Backend...")
    logger.info(f"Using Gemini model: {settings.main_model}")
    yield
    logger.info("Shutting down GST CA Copilot Backend...")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create API router with /api prefix
api_router = APIRouter(prefix="/api")


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version
    }


@api_router.get("/chats/{conversation_id}")
async def get_chat(conversation_id: str):
    """
    Fetch a specific conversation by ID.
    
    Args:
        conversation_id: UUID of the conversation
        
    Returns:
        Conversation record with messages
    """
    try:
        logger.info(f"Fetching conversation: {conversation_id}")
        conversation = supabase_service.get_conversation(conversation_id)
        
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conversation {conversation_id} not found"
            )
        
        return conversation
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching conversation: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@api_router.get("/chats")
async def list_chats(user_id: str):
    """
    List all conversations for a user.
    
    Args:
        user_id: UUID of the user (query parameter)
        
    Returns:
        List of conversation records, ordered by most recent first
    """
    try:
        if not user_id or not user_id.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="user_id query parameter is required"
            )
        
        logger.info(f"Fetching conversations for user: {user_id}")
        conversations = supabase_service.get_user_conversations(user_id)
        
        return {
            "conversations": conversations,
            "count": len(conversations)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching user conversations: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@api_router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint for GST CA Copilot with A2UI support.
    
    Flow:
    1. Check if message is an A2UI action or plain text
    2. Fetch existing conversation from Supabase
    3. Handle A2UI action or process as regular message
    4. Call Gemini API if needed
    5. Generate A2UI response or plain text
    6. Update Supabase
    7. Return response (with optional a2ui_message)
    """
    try:
        conversation_id = request.conversation_id
        user_message = request.message
        
        if not user_message or not user_message.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Message cannot be empty"
            )
        
        # Check if message is an A2UI action
        action = parse_a2ui_action(user_message)
        
        # Step 1: Fetch existing conversation from Supabase
        logger.info(f"Fetching conversation: {conversation_id}")
        conversation = supabase_service.get_conversation(conversation_id)
        
        conversation_messages = []
        user_id = None
        user_info = None
        
        if conversation:
            conversation_messages = conversation.get("messages", [])
            user_id = conversation.get("user_id")
            
            # Fetch user information for context
            if user_id:
                logger.info(f"Fetching user info for: {user_id}")
                user_info = supabase_service.get_user(user_id)
                if user_info:
                    logger.info(f"User context loaded: {user_info.get('business_type')}, {user_info.get('state')}")
        else:
            # If conversation doesn't exist, we'll create it after getting the response
            logger.info(f"Conversation {conversation_id} not found, will create new one")
        
        # Step 2: Handle A2UI action or process as regular message
        if action:
            logger.info(f"Processing A2UI action: {action.get('type')}")
            # Handle A2UI action
            response_data = handle_a2ui_action(action, user_info)
            assistant_response = response_data["reply"]
            a2ui_message = response_data.get("a2ui_message")
        else:
            # Regular text message - check if AI should respond with A2UI
            logger.info("Processing regular message, checking for A2UI triggers...")
            
            # Check if message triggers A2UI (e.g., keywords like "file GST", "ITR", "form")
            should_use_a2ui = should_trigger_a2ui(user_message)
            
            if should_use_a2ui:
                logger.info("Message triggers A2UI form")
                # Generate A2UI response based on message content
                response_data = generate_a2ui_response(user_message, user_info)
                assistant_response = response_data["reply"]
                a2ui_message = response_data.get("a2ui_message")
            else:
                # Regular AI response
                logger.info("Calling Gemini API for regular response...")
                assistant_response = ai_service.get_completion(conversation_messages, user_message, user_info)
                logger.info("Received response from Gemini")
                a2ui_message = None
        
        # Step 3: Prepare updated messages list
        updated_messages = conversation_messages.copy() if conversation_messages else []
        
        # Add user message
        updated_messages.append({
            "role": "user",
            "content": user_message
        })
        
        # Add assistant response
        updated_messages.append({
            "role": "assistant",
            "content": assistant_response
        })
        
        # Step 4: Update or create conversation in Supabase
        logger.info("Updating conversation in Supabase...")
        if conversation:
            success = supabase_service.update_conversation_messages(conversation_id, updated_messages)
        else:
            # For new conversations, frontend should create them first
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found. Please create the conversation first via frontend."
            )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save conversation"
            )
        
        logger.info(f"Successfully processed chat request for {conversation_id}")
        
        # Step 5: Return response
        return ChatResponse(
            conversation_id=conversation_id,
            reply=assistant_response,
            success=True,
            a2ui_message=a2ui_message
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


def should_trigger_a2ui(message: str) -> bool:
    """
    Check if a message should trigger an A2UI response.
    
    Args:
        message: User message
        
    Returns:
        True if message should trigger A2UI form/interface
    """
    message_lower = message.lower()
    
    # Keywords that trigger A2UI forms
    a2ui_triggers = [
        "file gst", "gst filing", "gst return",
        "register for gst", "gst registration",
        "file itr", "itr filing", "income tax return",
        "calculate gst", "gst calculator",
        "itc claim", "input tax credit",
        "gstr-1", "gstr-3b", "gstr-9"
    ]
    
    return any(trigger in message_lower for trigger in a2ui_triggers)


def generate_a2ui_response(message: str, user_info: dict = None) -> dict:
    """
    Generate A2UI response based on message content.
    
    Args:
        message: User message
        user_info: Optional user information
        
    Returns:
        Dict with 'reply' and 'a2ui_message'
    """
    message_lower = message.lower()
    
    # GST Filing Form
    if "file gst" in message_lower or "gst filing" in message_lower or "gstr" in message_lower:
        builder = A2UIBuilder()
        
        components = [
            A2UIBuilder.heading("gst_heading", "GST Filing Information", level=3),
            A2UIBuilder.text("gst_intro", "Please provide the following details to proceed with GST filing:"),
            A2UIBuilder.text_input(
                "input_gstin",
                "GSTIN Number",
                "form.gstin",
                placeholder="Enter your 15-digit GSTIN",
                required=True
            ),
            A2UIBuilder.select(
                "input_return_type",
                "Return Type",
                "form.returnType",
                options=[
                    {"value": "GSTR1", "label": "GSTR-1 (Outward Supplies)"},
                    {"value": "GSTR3B", "label": "GSTR-3B (Summary Return)"},
                    {"value": "GSTR9", "label": "GSTR-9 (Annual Return)"}
                ],
                required=True
            ),
            A2UIBuilder.select(
                "input_period",
                "Filing Period",
                "form.period",
                options=[
                    {"value": "Jan2024", "label": "January 2024"},
                    {"value": "Feb2024", "label": "February 2024"},
                    {"value": "Mar2024", "label": "March 2024"},
                    {"value": "Apr2024", "label": "April 2024"},
                    {"value": "May2024", "label": "May 2024"},
                    {"value": "Jun2024", "label": "June 2024"},
                    {"value": "Jul2024", "label": "July 2024"},
                    {"value": "Aug2024", "label": "August 2024"},
                    {"value": "Sep2024", "label": "September 2024"},
                    {"value": "Oct2024", "label": "October 2024"},
                    {"value": "Nov2024", "label": "November 2024"},
                    {"value": "Dec2024", "label": "December 2024"}
                ],
                required=True
            ),
            A2UIBuilder.button(
                "submit_gst",
                "Proceed with Filing",
                "submit_gst_filing",
                {
                    "gstin": "{{ form.gstin }}",
                    "returnType": "{{ form.returnType }}",
                    "period": "{{ form.period }}"
                },
                variant="primary"
            )
        ]
        
        builder.add_surface("gst_filing_form", components)
        
        return {
            "reply": "I can help you with GST filing. Please fill in the form below:",
            "a2ui_message": builder.build()
        }
    
    # GST Registration Form
    elif "register" in message_lower and "gst" in message_lower:
        builder = A2UIBuilder()
        
        components = [
            A2UIBuilder.heading("reg_heading", "GST Registration", level=3),
            A2UIBuilder.text_input(
                "input_business_name",
                "Business Name",
                "form.businessName",
                placeholder="Enter legal business name",
                required=True
            ),
            A2UIBuilder.text_input(
                "input_pan",
                "PAN Number",
                "form.pan",
                placeholder="ABCDE1234F",
                required=True
            ),
            A2UIBuilder.select(
                "input_state",
                "State",
                "form.state",
                options=[
                    {"value": "AP", "label": "Andhra Pradesh"},
                    {"value": "TN", "label": "Tamil Nadu"},
                    {"value": "KA", "label": "Karnataka"},
                    {"value": "MH", "label": "Maharashtra"},
                    {"value": "DL", "label": "Delhi"},
                    {"value": "UP", "label": "Uttar Pradesh"}
                ],
                required=True
            ),
            A2UIBuilder.number_input(
                "input_turnover",
                "Expected Annual Turnover (₹)",
                "form.turnover",
                placeholder="0",
                min_value=0,
                required=True
            ),
            A2UIBuilder.button(
                "submit_registration",
                "Submit Registration",
                "submit_gst_registration",
                {
                    "businessName": "{{ form.businessName }}",
                    "pan": "{{ form.pan }}",
                    "state": "{{ form.state }}",
                    "turnover": "{{ form.turnover }}"
                },
                variant="primary"
            )
        ]
        
        builder.add_surface("gst_registration_form", components)
        
        return {
            "reply": "Let's start your GST registration. Please provide the following information:",
            "a2ui_message": builder.build()
        }
    
    # Default: return None (will use regular AI response)
    return {"reply": "", "a2ui_message": None}


def handle_a2ui_action(action: dict, user_info: dict = None) -> dict:
    """
    Handle A2UI action from frontend.
    
    Args:
        action: Action dict with 'type' and 'data'
        user_info: Optional user information
        
    Returns:
        Dict with 'reply' and optional 'a2ui_message'
    """
    action_type = action.get("type")
    action_data = action.get("data", {})
    
    logger.info(f"Handling A2UI action: {action_type} with data: {action_data}")
    
    # GST Filing Action
    if action_type == "submit_gst_filing":
        gstin = action_data.get("gstin")
        return_type = action_data.get("returnType")
        period = action_data.get("period")
        
        # Validate GSTIN format
        if not gstin or len(gstin) != 15:
            return {
                "reply": "❌ Invalid GSTIN. Please enter a valid 15-digit GSTIN number.",
                "a2ui_message": None
            }
        
        # Process filing
        return {
            "reply": f"✅ GST filing details received!\n\n"
                    f"**GSTIN:** {gstin}\n"
                    f"**Return Type:** {return_type}\n"
                    f"**Period:** {period}\n\n"
                    f"I'm now processing your {return_type} filing for {period}. "
                    f"According to GST law, {return_type} must be filed by the 20th of the following month. "
                    f"Please ensure all invoices are uploaded before filing.",
            "a2ui_message": None
        }
    
    # GST Registration Action
    elif action_type == "submit_gst_registration":
        business_name = action_data.get("businessName")
        pan = action_data.get("pan")
        state = action_data.get("state")
        turnover = action_data.get("turnover")
        
        # Validate PAN format
        if not pan or len(pan) != 10:
            return {
                "reply": "❌ Invalid PAN. Please enter a valid 10-character PAN number.",
                "a2ui_message": None
            }
        
        # Check GST registration threshold
        threshold = 20_00_000  # ₹20 lakhs for goods, ₹10 lakhs for services
        
        reply = f"✅ GST registration details received!\n\n"
        reply += f"**Business Name:** {business_name}\n"
        reply += f"**PAN:** {pan}\n"
        reply += f"**State:** {state}\n"
        reply += f"**Expected Turnover:** ₹{turnover:,.0f}\n\n"
        
        if float(turnover) >= threshold:
            reply += f"✅ Your turnover exceeds ₹20 lakhs. GST registration is **mandatory** as per Section 22 of CGST Act.\n\n"
            reply += "Next steps:\n"
            reply += "1. Prepare required documents (PAN, Aadhar, Business proof)\n"
            reply += "2. Visit GST portal: https://www.gst.gov.in/\n"
            reply += "3. Complete Part A and Part B of registration\n"
            reply += "4. ARN will be generated within 15 minutes"
        else:
            reply += f"ℹ️ Your turnover is below ₹20 lakhs. GST registration is **optional** but can be beneficial for ITC claims."
        
        return {
            "reply": reply,
            "a2ui_message": None
        }
    
    # Unknown action
    else:
        return {
            "reply": f"I received an action of type '{action_type}', but I'm not sure how to handle it yet. Please try a different action or ask me a question.",
            "a2ui_message": None
        }


# Include the API router with /api prefix
app.include_router(api_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

