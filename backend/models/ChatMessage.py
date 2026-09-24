from sqlalchemy import Boolean, Column, Integer, String,Text, DateTime
from database import Base
from datetime import datetime


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    thread_id = Column(String(255), nullable=False, index=True)
    role = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)