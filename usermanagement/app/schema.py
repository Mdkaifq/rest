from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime

class UserType(BaseModel):
    id: Optional[UUID] = None
    username: Optional[str] = None
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_no: Optional[str] = None
    role: Optional[str] = None
    created_on: Optional[datetime] = None


class AuthResponse(BaseModel):
    access_token: str
    refresh_token: str

class CreateUserRequest(BaseModel):
    username: str
    email: str
    password: str
    first_name: Optional[str] = "null"
    last_name: Optional[str] = "null"

class UserLoginRequest(BaseModel):
    username: str
    password: str

class ResetPasswordRequest(BaseModel):
    username: str
    new_password: str
    old_password: str

class AssignRoleRequest(BaseModel):
    role: str