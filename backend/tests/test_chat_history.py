import pytest
from uuid import uuid4

from backend.app.schemas.merchant import MerchantCreate
from backend.app.services.merchant_services import MerchantService
from backend.app.services.chat_service import ChatService

def test_chat_history_db(db):
    merchant = MerchantService(db).create(
        MerchantCreate(name="Shoe Store", slug="shoe-store-chat", email="shoe@store.com")
    )
    
    chat_service = ChatService(db)
    
    # Create session
    session = chat_service.get_or_create_session(None, merchant.id)
    assert session.id is not None
    assert session.merchant_id == merchant.id
    
    # Get existing session
    session2 = chat_service.get_or_create_session(session.id, merchant.id)
    assert session2.id == session.id
    
    # Add messages
    chat_service.add_message(session.id, "user", "Hello agent")
    chat_service.add_message(session.id, "assistant", "Hello human")
    
    # Get history
    history = chat_service.get_history(session.id)
    assert len(history) == 2
    assert history[0].role == "user"
    assert history[0].content == "Hello agent"
    assert history[1].role == "assistant"
    assert history[1].content == "Hello human"
