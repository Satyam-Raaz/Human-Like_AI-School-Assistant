from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models.parent import Parent
from models.student import Student

from security.dependencies import require_role


router = APIRouter(
    prefix="/parents",
    tags=["Parents"]
)


# ---------------------------------------
# Parent Profile
# ---------------------------------------

@router.get("/profile")
def get_parent_profile(
    current_user=Depends(
        require_role("parent")
    ),
    db: Session = Depends(get_db)
):

    parent = db.query(Parent).filter(
        Parent.id == current_user["user_id"]
    ).first()

    if not parent:
        raise HTTPException(
            status_code=404,
            detail="Parent not found"
        )

    return {
        "id": parent.id,
        "name": parent.name,
        "email": parent.email,
        "phone": parent.phone,
        "student_id": parent.student_id
    }


# ---------------------------------------
# Get Child Information
# ---------------------------------------

@router.get("/child")
def get_child(
    current_user=Depends(
        require_role("parent")
    ),
    db: Session = Depends(get_db)
):

    parent = db.query(Parent).filter(
        Parent.id == current_user["user_id"]
    ).first()

    if not parent:
        raise HTTPException(
            status_code=404,
            detail="Parent not found"
        )

    student = db.query(Student).filter(
        Student.id == parent.student_id
    ).first()

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Child not found"
        )

    return {
        "id": student.id,
        "name": student.name,
        "class_name": student.class_name,
        "roll_number": student.roll_number,
        "attendance": student.attendance
    }


# ---------------------------------------
# Get Child Attendance
# ---------------------------------------

@router.get("/child/attendance")
def get_child_attendance(
    current_user=Depends(
        require_role("parent")
    ),
    db: Session = Depends(get_db)
):

    parent = db.query(Parent).filter(
        Parent.id == current_user["user_id"]
    ).first()

    if not parent:
        raise HTTPException(
            status_code=404,
            detail="Parent not found"
        )

    student = db.query(Student).filter(
        Student.id == parent.student_id
    ).first()

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Child not found"
        )

    return {
        "student_id": student.id,
        "student_name": student.name,
        "attendance": student.attendance
    }
