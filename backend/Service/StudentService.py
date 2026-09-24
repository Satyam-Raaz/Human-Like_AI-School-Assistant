from sqlalchemy.orm import Session
from models.student import Student
from Service.AuthenticationService import AuthenticationService
from database import SessionLocal
from sqlalchemy import func




class StudentService:

    @staticmethod
    def create_student(db: Session, name, email, password,
                       class_name, roll_number, attendance=0):

        hashed_password = AuthenticationService.hash_password(password)

        student = Student(
            name=name,
            email=email,
            password=hashed_password,
            class_name=class_name,
            roll_number=roll_number,
            attendance=attendance
        )

        db.add(student)
        db.commit()
        db.refresh(student)

        return student

    @staticmethod
    def get_student(db: Session, student_id: int):

        return db.query(Student).filter(
            Student.id == student_id
        ).first()
        
    @staticmethod
    def get_student_by_id(student_id: int):
        db= SessionLocal()
    
        std =  db.query(Student).filter(
            Student.id == student_id
        ).first() 
        db.close()  
        return std 

    @staticmethod
    def get_all_students(db: Session):

        return db.query(Student).all()

    @staticmethod
    def get_student_by_email(db: Session, email: str):

        return db.query(Student).filter(
            Student.email == email
        ).first()
        
    @staticmethod    
    def get_student_by_name_and_class(
        name: str,
        class_name: str
    ):
        db = SessionLocal()
        std = db.query(Student).filter(
            func.lower(Student.name) == name.strip().lower(),
            func.lower(Student.class_name) == class_name.strip().lower()
        ).first()    
        
        return std

    @staticmethod
    def update_student(db: Session, student_id: int, data: dict):

        student = db.query(Student).filter(
            Student.id == student_id
        ).first()

        if not student:
            return None

        if "password" in data and data["password"]:
            data["password"] = AuthenticationService.hash_password(
                data["password"]
            )

        for key, value in data.items():
            if hasattr(student, key):
                setattr(student, key, value)

        db.commit()
        db.refresh(student)

        return student

    @staticmethod
    def delete_student(db: Session, student_id: int):

        student = db.query(Student).filter(
            Student.id == student_id
        ).first()

        if not student:
            return None

        db.delete(student)
        db.commit()

        return student
    
    @staticmethod
    def update_attendance(student_id: int):
        db = SessionLocal()

        try:
            student = db.query(Student).filter(
                Student.id == student_id
            ).first()

            if not student:
                return {
                    "success": False,
                    "message": "Student not found"
                }

            student.attendance = student.attendance+1

            db.commit()
            db.refresh(student)

            return {
                "success": True,
                "message": "Attendance updated successfully",
                "student_id": student.id,
                "attendance": student.attendance
            }

        except Exception as e:
            db.rollback()

            return {
                "success": False,
                "message": f"Failed to update attendance: {str(e)}"
            }

        finally:
            db.close()
            
            
    @staticmethod    
    def update_student_by_name_and_class(
        name: str,
        class_name: str
    ):
        db=SessionLocal()
        student = db.query(Student).filter(
            func.lower(Student.name) == name.strip().lower(),
            func.lower(Student.class_name) == class_name.strip().lower()
        ).first() 
        print("============================================================================================")
        print(name,class_name)
        
        if not student:
            return {
                "success": False,
                "message": "Student not found"
            }
        
        student.attendance =  student.attendance + 1
        db.commit()
        db.refresh(student)
        db.close()
        return student
        
        
             
        
    
        
        
