from sqlalchemy import Boolean, Column, Integer, String,Text, DateTime
from database import Base
from datetime import datetime


class LongTermMemory(Base):
    __tablename__ = "long_term_memory"

    id = Column(Integer, primary_key=True, index=True)
    user_id= Column(Integer,index=True)
    thread_id = Column(String(255), nullable=False, index=True)
    memory = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)