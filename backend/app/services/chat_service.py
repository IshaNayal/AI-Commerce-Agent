from uuid import UUID
from sqlalchemy.orm import Session

from ..repositories.chat import ChatRepository
from ..models.chat import ChatSession, ChatMessage

class ChatService:
    def __init__(self, db: Session):
        self.chat_repository = ChatRepository(db)

    def get_or_create_session(self, session_id: UUID | None, merchant_id: UUID, cart_id: UUID | None = None) -> ChatSession:
        if session_id:
            session = self.chat_repository.get_session(session_id)
            if session:
                return session
        
        return self.chat_repository.create_session(
            merchant_id=merchant_id,
            cart_id=cart_id
        )

    def get_history(self, session_id: UUID) -> list[ChatMessage]:
        return self.chat_repository.get_messages(session_id)

    def add_message(self, session_id: UUID, role: str, content: str) -> ChatMessage:
        if role not in ["user", "assistant"]:
            raise ValueError(f"Invalid role: {role}")
            
        return self.chat_repository.add_message(
            session_id=session_id,
            role=role,
            content=content
        )
