from sqlalchemy import Boolean, Column, Integer, String, DateTime
from database import Base
from datetime import datetime



class Meeting(Base):
    __tablename__ = "parents"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_status = Column(String, default="Pending")