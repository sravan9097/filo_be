"""Pydantic models for request and response validation."""
from typing import Optional, Literal
from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    """Individual chat message model."""
    role: Literal["user", "assistant", "system"]
    content: str


class ChatRequest(BaseModel):
    """Request model for POST /chat endpoint."""
    conversation_id: str = Field(..., description="UUID of the conversation")
    message: str = Field(..., description="Latest user message")


class ChatResponse(BaseModel):
    """Response model for POST /chat endpoint."""
    conversation_id: str
    reply: str
    success: bool = True
    error: Optional[str] = None

