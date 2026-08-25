from uuid import UUID
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class ChatMessage(BaseModel):
    role: str # 'user' or 'assistant'
    content: str

class ChatRequest(BaseModel):
    merchant_id: UUID
    session_id: Optional[UUID] = None
    cart_id: Optional[UUID] = None
    message: str

class ChatResponse(BaseModel):
    response: str
    session_id: UUID
    cart_id: UUID
