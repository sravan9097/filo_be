"""Main FastAPI application for GST CA Copilot backend."""
from fastapi import FastAPI, HTTPException, status, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from config import settings
from models import ChatRequest, ChatResponse, ChatMessage
from services.supabase_service import supabase_service
from services.openai_service import OpenAIService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize services
openai_service = OpenAIService()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown events."""
    logger.info("Starting GST CA Copilot Backend...")
    logger.info(f"Using OpenAI model: {settings.main_model}")
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
    Main chat endpoint for GST CA Copilot.
    
    Flow:
    1. Fetch existing conversation from Supabase
    2. Build prompt with conversation history and user context
    3. Call OpenAI API
    4. Append assistant response to conversation
    5. Update Supabase
    6. Return response
    """
    try:
        conversation_id = request.conversation_id
        user_message = request.message
        
        if not user_message or not user_message.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Message cannot be empty"
            )
        
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
            # Note: For new conversations, user_id should be provided by frontend
            # For now, we'll skip creation if user_id is missing
        
        # Step 2: Build messages for OpenAI with user context
        logger.info("Building prompt...")
        messages = openai_service.build_messages(conversation_messages, user_message, user_info)
        
        # Step 3: Call OpenAI API
        logger.info("Calling OpenAI API...")
        assistant_response = openai_service.get_completion(messages)
        logger.info("Received response from OpenAI")
        
        # Step 4: Prepare updated messages list
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
        
        # Step 5: Update or create conversation in Supabase
        logger.info("Updating conversation in Supabase...")
        if conversation:
            success = supabase_service.update_conversation_messages(conversation_id, updated_messages)
        else:
            # For new conversations, frontend should create them first
            # If conversation doesn't exist, we can't create it without user_id
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
        
        # Step 6: Return response
        return ChatResponse(
            conversation_id=conversation_id,
            reply=assistant_response,
            success=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


# Include the API router with /api prefix
app.include_router(api_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

