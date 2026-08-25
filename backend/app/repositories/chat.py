from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import select

from ..models.chat import ChatSession, ChatMessage

class ChatRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_session(self, session_id: UUID) -> ChatSession | None:
        return self.db.scalars(
            select(ChatSession).where(ChatSession.id == session_id)
        ).first()

    def create_session(self, merchant_id: UUID, cart_id: UUID | None = None) -> ChatSession:
        chat_session = ChatSession(
            merchant_id=merchant_id,
            cart_id=cart_id
        )
        self.db.add(chat_session)
        self.db.commit()
        self.db.refresh(chat_session)
        return chat_session
        
    def get_messages(self, session_id: UUID) -> list[ChatMessage]:
        return list(self.db.scalars(
            select(ChatMessage).where(ChatMessage.session_id == session_id).order_by(ChatMessage.created_at)
        ))

    def add_message(self, session_id: UUID, role: str, content: str) -> ChatMessage:
        message = ChatMessage(
            session_id=session_id,
            role=role,
            content=content
        )
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        return message
