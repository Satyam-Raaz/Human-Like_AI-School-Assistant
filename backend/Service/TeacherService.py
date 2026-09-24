from sqlalchemy.orm import Session
from models.teacher import Teacher
from Service.AuthenticationService import AuthenticationService


class TeacherService:

    @staticmethod
    def create_teacher(db: Session, name, email, password,
                       subject, class_name):

        hashed_password = AuthenticationService.hash_password(password)

        teacher = Teacher(
            name=name,
            email=email,
            password=hashed_password,
            subject=subject,
            class_name=class_name
        )

        db.add(teacher)
        db.commit()
        db.refresh(teacher)

        return teacher

    @staticmethod
    def get_teacher(db: Session, teacher_id: int):

        return db.query(Teacher).filter(
            Teacher.id == teacher_id
        ).first()

    @staticmethod
    def get_all_teachers(db: Session):

        return db.query(Teacher).all()

    @staticmethod
    def get_teacher_by_email(db: Session, email: str):

        return db.query(Teacher).filter(
            Teacher.email == email
        ).first()

    @staticmethod
    def update_teacher(db: Session, teacher_id: int, data: dict):

        teacher = db.query(Teacher).filter(
            Teacher.id == teacher_id
        ).first()

        if not teacher:
            return None

        if "password" in data and data["password"]:
            data["password"] = AuthenticationService.hash_password(
                data["password"]
            )

        for key, value in data.items():
            if hasattr(teacher, key):
                setattr(teacher, key, value)

        db.commit()
        db.refresh(teacher)

        return teacher

    @staticmethod
    def delete_teacher(db: Session, teacher_id: int):

        teacher = db.query(Teacher).filter(
            Teacher.id == teacher_id
        ).first()

        if not teacher:
            return None

        db.delete(teacher)
        db.commit()

        return teacher
