from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import uuid4

from ...database.dependencies import get_db
from ...schemas.chat import ChatRequest, ChatResponse
from ...agent.commerce_agent import CommerceAgent
from ...services.chat_service import ChatService
from langchain_core.messages import HumanMessage, AIMessage

router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)

@router.post(
    "",
    response_model=ChatResponse,
)
def chat_with_agent(
    data: ChatRequest,
    db: Session = Depends(get_db),
):
    try:
        # Generate a new cart ID if none was provided
        cart_id = data.cart_id if data.cart_id else uuid4()
        
        chat_service = ChatService(db)
        session = chat_service.get_or_create_session(
            session_id=data.session_id,
            merchant_id=data.merchant_id,
            cart_id=cart_id
        )
        
        agent = CommerceAgent(
            db=db,
            merchant_id=data.merchant_id,
            cart_id=cart_id
        )
                
        # Get response
        response_text = agent.chat(data.message, session.id)
        
        return ChatResponse(
            response=response_text,
            session_id=session.id,
            cart_id=cart_id
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc)
        ) from exc
