from sqlalchemy.orm import Session

from models.student import Student
from models.teacher import Teacher
from models.parent import Parent

from Service.AuthenticationService import AuthenticationService


class LoginService:

    @staticmethod
    def login(
        db: Session,
        email: str,
        password: str
    ):

        # --------------------------------
        # Student
        # --------------------------------

        student = db.query(Student).filter(
            Student.email == email
        ).first()

        if student:

            if not student.is_active:
                return "not active"

            if AuthenticationService.verify_password(
                password,
                student.password
            ):

                return AuthenticationService.create_login_response(
                    user_id=student.id,
                    role="student"
                )

            return "error in student login"

        # --------------------------------
        # Teacher
        # --------------------------------

        teacher = db.query(Teacher).filter(
            Teacher.email == email
        ).first()

        if teacher:

            if not teacher.is_active:
                return None

            if AuthenticationService.verify_password(
                password,
                teacher.password
            ):

                return AuthenticationService.create_login_response(
                    user_id=teacher.id,
                    role="teacher"
                )

            return None

        # --------------------------------
        # Parent
        # --------------------------------

        parent = db.query(Parent).filter(
            Parent.email == email
        ).first()

        if parent:

            if not parent.is_active:
                return None

            if AuthenticationService.verify_password(
                password,
                parent.password
            ):

                return AuthenticationService.create_login_response(
                    user_id=parent.id,
                    role="parent"
                )

            return None

        return None
