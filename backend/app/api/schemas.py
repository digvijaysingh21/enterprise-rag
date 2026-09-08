import uuid

from pydantic import BaseModel, EmailStr

from app.models.user import UserRole


class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str
    role: UserRole = UserRole.END_USER


class UserResponse(BaseModel):
    id: uuid.UUID
    email: EmailStr
    role: UserRole
    is_active: bool

    model_config = {"from_attributes": True}  # lets Pydantic read straight from the SQLAlchemy model


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"