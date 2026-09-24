from sqlalchemy.orm import Session
from models.parent import Parent
from Service.AuthenticationService import AuthenticationService


class ParentService:

    @staticmethod
    def create_parent(db: Session, name, email, password,
                      phone, student_id):

        hashed_password = AuthenticationService.hash_password(password)

        parent = Parent(
            name=name,
            email=email,
            password=hashed_password,
            phone=phone,
            student_id=student_id
        )

        db.add(parent)
        db.commit()
        db.refresh(parent)

        return parent

    @staticmethod
    def get_parent(db: Session, parent_id: int):

        return db.query(Parent).filter(
            Parent.id == parent_id
        ).first()

    @staticmethod
    def get_all_parents(db: Session):

        return db.query(Parent).all()

    @staticmethod
    def get_parent_by_email(db: Session, email: str):

        return db.query(Parent).filter(
            Parent.email == email
        ).first()

    @staticmethod
    def get_parent_by_student(db: Session, student_id: int):

        return db.query(Parent).filter(
            Parent.student_id == student_id
        ).all()

    @staticmethod
    def update_parent(db: Session, parent_id: int, data: dict):

        parent = db.query(Parent).filter(
            Parent.id == parent_id
        ).first()

        if not parent:
            return None

        if "password" in data and data["password"]:
            data["password"] = AuthenticationService.hash_password(
                data["password"]
            )

        for key, value in data.items():
            if hasattr(parent, key):
                setattr(parent, key, value)

        db.commit()
        db.refresh(parent)

        return parent

    @staticmethod
    def delete_parent(db: Session, parent_id: int):

        parent = db.query(Parent).filter(
            Parent.id == parent_id
        ).first()

        if not parent:
            return None

        db.delete(parent)
        db.commit()

        return parent
