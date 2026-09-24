from sqlalchemy import Boolean, Column, Integer, String
from database import Base


class Parent(Base):
    __tablename__ = "parents"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50))
    email = Column(String(100), unique=True, index=True)
    password = Column(String(255))
    phone = Column(String(15))
    student_id = Column(Integer)
    is_active = Column(Boolean, default=True)
