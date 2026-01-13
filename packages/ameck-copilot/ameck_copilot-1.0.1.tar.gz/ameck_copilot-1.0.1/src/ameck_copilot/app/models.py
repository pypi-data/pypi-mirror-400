"""
Pydantic models for request/response handling
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from datetime import datetime
from enum import Enum


class MessageRole(str, Enum):
    """Role of the message sender"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class Mode(str, Enum):
    """Mode of the assistant"""
    ASK = "ask"
    AGENT = "agent"
    EDIT = "edit"
    PLAN = "plan"


class Message(BaseModel):
    """A single chat message"""
    role: MessageRole
    content: str
    timestamp: Optional[datetime] = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ChatRequest(BaseModel):
    """Request model for chat endpoint"""
    message: str = Field(..., min_length=1, max_length=100000, description="User's message")
    conversation_history: Optional[List[Message]] = Field(
        default=[],
        description="Previous messages in the conversation"
    )
    mode: Mode = Field(default=Mode.ASK, description="Mode to run the assistant in: 'ask', 'agent', 'edit', or 'plan'")
    stream: bool = Field(default=True, description="Whether to stream the response")
    temperature: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Override default temperature"
    )
    max_tokens: Optional[int] = Field(
        default=None,
        ge=1,
        le=16384,
        description="Override default max tokens"
    )
    model: Optional[str] = Field(
        default=None,
        description="Model to use for this request"
    )


class ChatResponse(BaseModel):
    """Response model for non-streaming chat"""
    message: str
    role: MessageRole = MessageRole.ASSISTANT
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    model: str
    usage: Optional[dict] = None
    structured: Optional[dict] = None  # Optional structured data (e.g., parsed Plan JSON)



class CodeRequest(BaseModel):
    """Request model for code-specific operations"""
    code: str = Field(..., description="Code to analyze/modify")
    language: Optional[str] = Field(default=None, description="Programming language")
    operation: Literal["explain", "review", "optimize", "fix", "document", "test"] = Field(
        ..., description="Operation to perform on the code"
    )
    context: Optional[str] = Field(default=None, description="Additional context")
    model: Optional[str] = Field(
        default=None,
        description="Model to use for this request"
    )


class CodeResponse(BaseModel):
    """Response model for code operations"""
    result: str
    operation: str
    language: Optional[str]
    suggestions: Optional[List[str]] = None


class GenerateRequest(BaseModel):
    """Request model for code generation"""
    prompt: str = Field(..., description="Description of what to generate")
    language: str = Field(..., description="Target programming language")
    framework: Optional[str] = Field(default=None, description="Framework to use")
    style: Optional[str] = Field(default=None, description="Coding style preferences")
    model: Optional[str] = Field(
        default=None,
        description="Model to use for this request"
    )


class ErrorResponse(BaseModel):
    """Error response model"""
    error: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class HealthResponse(BaseModel):
    """Health check response"""
    status: str = "healthy"
    version: str
    model: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
