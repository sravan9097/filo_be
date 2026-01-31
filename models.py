"""Pydantic models for request and response validation."""
from typing import Optional, Literal, Dict, Any
from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    """Individual chat message model."""
    role: Literal["user", "assistant", "system"]
    content: str


class ChatRequest(BaseModel):
    """Request model for POST /chat endpoint."""
    conversation_id: str = Field(..., description="UUID of the conversation")
    message: str = Field(..., description="Latest user message or A2UI action JSON")


class ChatResponse(BaseModel):
    """Response model for POST /chat endpoint."""
    conversation_id: str
    reply: str
    success: bool = True
    error: Optional[str] = None
    a2ui_message: Optional[Dict[str, Any]] = Field(None, description="A2UI protocol message for dynamic UI")

