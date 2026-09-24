from sqlalchemy.orm import Session
from models.LongTermMemory import LongTermMemory
from Service.AuthenticationService import AuthenticationService
from datetime import datetime
from database import SessionLocal
from typing import Any



class LongTermMemoryService:

    @staticmethod
    def save_memory(user_id: int, thread_id: str, memory:str):
        db=SessionLocal()
        try:
            item = LongTermMemory(
                user_id=user_id,
                thread_id=thread_id,
                memory=memory,
                created_at=datetime.utcnow()
            )
        
            db.add(item)
            db.commit()
        
            return "Memory saved successfully."
        
        finally:
            db.close()




    @staticmethod
    def search_memory(user_id: int, thread_id: str, query: str):
        db=SessionLocal()
        try:
            memories = (
                db.query(LongTermMemory)
                .filter(LongTermMemory.user_id==user_id)
                .filter(LongTermMemory.thread_id == thread_id)
                .order_by(LongTermMemory.created_at.desc())
                .limit(20)
                .all()
            )

            if not memories:
                return "No saved memory found."

            return "\n".join([f"- {m.memory}" for m in memories])

        finally:
            db.close()
