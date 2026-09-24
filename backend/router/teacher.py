from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, conint
from sqlalchemy.orm import Session

from database import get_db
from models.teacher import Teacher
from models.student import Student

from security.dependencies import require_role
from typing import Annotated
from pydantic import Field



router = APIRouter(
    prefix="/teachers",
    tags=["Teachers"]
)


class AttendanceUpdate(BaseModel):
    attendance: Annotated[int, Field(ge=0, le=100)]


# ---------------------------------------
# Teacher Profile
# ---------------------------------------

@router.get("/profile")
def get_teacher_profile(
    current_user=Depends(
        require_role("teacher")
    ),
    db: Session = Depends(get_db)
):

    teacher = db.query(Teacher).filter(
        Teacher.id == current_user["user_id"]
    ).first()

    if not teacher:
        raise HTTPException(
            status_code=404,
            detail="Teacher not found"
        )

    return {
        "id": teacher.id,
        "name": teacher.name,
        "email": teacher.email,
        "subject": teacher.subject,
        "class_name": teacher.class_name
    }


# ---------------------------------------
# Get Students
# ---------------------------------------

@router.get("/students")
def get_students(
    current_user=Depends(
        require_role("teacher")
    ),
    db: Session = Depends(get_db)
):

    students = db.query(Student).all()

    return students


# ---------------------------------------
# Mark Student Attendance
# ---------------------------------------

@router.put("/students/{student_id}/attendance")
def mark_attendance(
    student_id: int,
    payload: AttendanceUpdate,
    current_user=Depends(
        require_role("teacher")
    ),
    db: Session = Depends(get_db)
):

    student = db.query(Student).filter(
        Student.id == student_id
    ).first()

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    student.attendance = payload.attendance

    db.commit()
    db.refresh(student)

    return {
        "message": "Attendance updated successfully",
        "student_id": student.id,
        "attendance": student.attendance
    }
