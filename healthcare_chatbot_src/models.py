"""
Data models for the Medical Services ChatBot API
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional
import re


class UserInfo(BaseModel):
    """User information model with validation"""
    first_name: str = Field(..., description="User's first name")
    last_name: str = Field(..., description="User's last name")
    id_number: str = Field(..., description="9-digit ID number")
    gender: str = Field(..., description="User's gender")
    age: int = Field(..., ge=0, le=120, description="User's age")
    hmo_name: str = Field(..., description="HMO name (מכבי, מאוחדת, כללית)")
    hmo_card_number: str = Field(..., description="9-digit HMO card number")
    insurance_tier: str = Field(..., description="Insurance tier (זהב, כסף, ארד)")
    
    @validator('id_number')
    def validate_id_number(cls, v):
        if not re.match(r'^\d{9}$', v):
            raise ValueError('ID number must be exactly 9 digits')
        return v
    
    @validator('hmo_card_number')
    def validate_hmo_card_number(cls, v):
        if not re.match(r'^\d{9}$', v):
            raise ValueError('HMO card number must be exactly 9 digits')
        return v
    
    @validator('hmo_name')
    def validate_hmo_name(cls, v):
        valid_hmos = ['מכבי', 'מאוחדת', 'כללית', 'Maccabi', 'Meuhedet', 'Clalit']
        if v not in valid_hmos:
            raise ValueError('Invalid HMO name')
        return v
    
    @validator('insurance_tier')
    def validate_insurance_tier(cls, v):
        valid_tiers = ['זהב', 'כסף', 'ארד', 'Gold', 'Silver', 'Bronze']
        if v not in valid_tiers:
            raise ValueError('Invalid insurance tier')
        return v


class ChatMessage(BaseModel):
    """Chat message model"""
    role: str = Field(..., description="Message role (user/assistant)")
    content: str = Field(..., description="Message content")
    timestamp: Optional[str] = Field(None, description="Message timestamp")


class ChatRequest(BaseModel):
    """Chat request model"""
    message: str = Field(..., description="User message")
    user_info: Optional[UserInfo] = Field(None, description="User information")
    conversation_history: List[ChatMessage] = Field(default_factory=list, description="Conversation history")
    phase: str = Field(..., description="Current phase (info_collection/qa)")
    language: str = Field(default="he", description="Language preference (he/en)")


class ChatResponse(BaseModel):
    """Chat response model"""
    response: str = Field(..., description="Bot response")
    phase: str = Field(..., description="Current phase")
    user_info: Optional[UserInfo] = Field(None, description="User information")
    user_info_complete: bool = Field(..., description="Whether user info collection is complete")
    suggested_questions: Optional[List[str]] = Field(None, description="Suggested follow-up questions")


class HealthStatus(BaseModel):
    """Health check response model"""
    status: str = Field(..., description="Service status")
    timestamp: float = Field(..., description="Current timestamp")
    knowledge_base_loaded: bool = Field(..., description="Whether knowledge base is loaded")
    azure_openai_configured: bool = Field(..., description="Whether Azure OpenAI is configured")
    vector_rag_available: bool = Field(..., description="Whether vector RAG system is available")
    total_chunks: int = Field(..., description="Total number of content chunks")
    total_services: int = Field(..., description="Total number of medical services")


class ServicesList(BaseModel):
    """Available services response model"""
    services: List[str] = Field(..., description="List of available medical services")
