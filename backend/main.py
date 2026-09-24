from fastapi import FastAPI

from router.auth import router as auth_router
from router.student import router as student_router
from router.teacher import router as teacher_router
from router.parent import router as parent_router
from router.chatbot import router as chatbot_router

from database import Base, engine

# Import models so SQLAlchemy knows about them before create_all runs
from models import student, teacher, parent  # noqa: F401


app = FastAPI(
    title="School ERP API",
    description="XYZ AI School Assistant Backend",
    version="1.0.0"
)

from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173","http://127.0.0.1:5173",],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Creates tables automatically if they don't exist yet.
# Remove/replace with Alembic migrations for production use.
Base.metadata.create_all(bind=engine)


app.include_router(auth_router)
app.include_router(student_router)
app.include_router(teacher_router)
app.include_router(parent_router)
app.include_router(chatbot_router)



@app.get("/")
def root():

    return {
        "message": "School ERP API is running"
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )
