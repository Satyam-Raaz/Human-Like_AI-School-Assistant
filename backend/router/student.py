from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models.student import Student
from security.dependencies import require_role


router = APIRouter(
    prefix="/students",
    tags=["Students"]
)


# ---------------------------------------
# Get Student Profile
# ---------------------------------------

@router.get("/profile")
def get_student_profile(
    current_user=Depends(
        require_role("student")
    ),
    db: Session = Depends(get_db)
):

    student = db.query(Student).filter(
        Student.id == current_user["user_id"]
    ).first()

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    return {
        "id": student.id,
        "name": student.name,
        "email": student.email,
        "class_name": student.class_name,
        "roll_number": student.roll_number,
        "attendance": student.attendance
    }


# ---------------------------------------
# Get Own Attendance
# ---------------------------------------

@router.get("/attendance")
def get_student_attendance(
    current_user=Depends(
        require_role("student")
    ),
    db: Session = Depends(get_db)
):

    student = db.query(Student).filter(
        Student.id == current_user["user_id"]
    ).first()

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    return {
        "student_id": student.id,
        "student_name": student.name,
        "attendance": student.attendance
    }
