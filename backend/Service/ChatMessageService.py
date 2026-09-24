from sqlalchemy.orm import Session
from models.ChatMessage import ChatMessage 
from Service.AuthenticationService import AuthenticationService
from datetime import datetime
from database import SessionLocal



class ChatMessageService:

    
    
    @staticmethod
    def save_chat_message(user_id: int,thread_id: str, role: str, content: str):
        db=SessionLocal()
        try:
            msg = ChatMessage(
                user_id=user_id,
                thread_id=thread_id,
                role=role,
                content=content,
                created_at=datetime.utcnow()
            )

            db.add(msg)

            db.commit()

        finally:
            db.close()



    @staticmethod
    def get_chat_history(user_id:int, thread_id: str):
        db=SessionLocal()
        try:
            return (
                db.query(ChatMessage)
                .filter(ChatMessage.thread_id == thread_id)
                .order_by(ChatMessage.created_at.asc())
                .all()
            )

        finally:
            db.close()

