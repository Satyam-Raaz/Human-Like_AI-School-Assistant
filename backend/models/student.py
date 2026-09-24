from sqlalchemy import Boolean, Column, Integer, String
from database import Base


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50),index=True)
    email = Column(String(100), unique=True, index=True)
    password = Column(String(255))
    class_name = Column(String(50), index=True)
    roll_number = Column(Integer)
    attendance = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)

