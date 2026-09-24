from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from schemas.auth_schema import (
    LoginRequest,
    TokenResponse,
    StudentRegister,
    TeacherRegister,
    ParentRegister,
)
from Service.LoginService import LoginService
from Service.StudentService import StudentService
from Service.TeacherService import TeacherService
from Service.ParentService import ParentService


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post(
    "/login",
    response_model=TokenResponse
)
def login(
    request: LoginRequest,
    db: Session = Depends(get_db)
):

    result = LoginService.login(
        db=db,
        email=request.email,
        password=request.password
    )

    if result is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    return result


# ---------------------------------------
# Registration endpoints
# (added — without these, no accounts can ever be created)
# ---------------------------------------

@router.post("/register/student")
def register_student(
    request: StudentRegister,
    db: Session = Depends(get_db)
):

    existing = StudentService.get_student_by_email(db, request.email)

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    student = StudentService.create_student(
        db=db,
        name=request.name,
        email=request.email,
        password=request.password,
        class_name=request.class_name,
        roll_number=request.roll_number
    )

    return {
        "id": student.id,
        "name": student.name,
        "email": student.email
    }


@router.post("/register/teacher")
def register_teacher(
    request: TeacherRegister,
    db: Session = Depends(get_db)
):

    existing = TeacherService.get_teacher_by_email(db, request.email)

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    teacher = TeacherService.create_teacher(
        db=db,
        name=request.name,
        email=request.email,
        password=request.password,
        subject=request.subject,
        class_name=request.class_name
    )

    return {
        "id": teacher.id,
        "name": teacher.name,
        "email": teacher.email
    }


@router.post("/register/parent")
def register_parent(
    request: ParentRegister,
    db: Session = Depends(get_db)
):

    existing = ParentService.get_parent_by_email(db, request.email)

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    parent = ParentService.create_parent(
        db=db,
        name=request.name,
        email=request.email,
        password=request.password,
        phone=request.phone,
        student_id=request.student_id
    )

    return {
        "id": parent.id,
        "name": parent.name,
        "email": parent.email
    }
