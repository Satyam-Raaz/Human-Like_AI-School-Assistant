from sqlalchemy import Boolean, Column, Integer, String
from database import Base


class Teacher(Base):
    __tablename__ = "teachers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50))
    email = Column(String(100), unique=True, index=True)
    password = Column(String(255))
    subject = Column(String(50))
    class_name = Column(String(50))
    is_active = Column(Boolean, default=True)
