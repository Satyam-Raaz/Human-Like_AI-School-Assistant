from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):

    email: EmailStr
    password: str


class TokenResponse(BaseModel):

    access_token: str
    token_type: str
    user_id: int
    role: str


class CurrentUser(BaseModel):

    user_id: int
    role: str


# ---------------------------------------
# Registration schemas
# (added so accounts can actually be created)
# ---------------------------------------

class StudentRegister(BaseModel):
    name: str
    email: EmailStr
    password: str
    class_name: str
    roll_number: int


class TeacherRegister(BaseModel):
    name: str
    email: EmailStr
    password: str
    subject: str
    class_name: str


class ParentRegister(BaseModel):
    name: str
    email: EmailStr
    password: str
    phone: str
    student_id: int
