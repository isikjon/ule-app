from pydantic import BaseModel, Field
from typing import Optional
import re

class User(BaseModel):
    phone: str = Field(..., description="Phone number with Russian format")
    password: str = Field(..., min_length=6, description="User password")
    name: Optional[str] = None
    city: Optional[str] = None
    avatar: Optional[str] = None

class PhoneRequest(BaseModel):
    phone: str = Field(..., description="Phone number for verification")

    @classmethod
    def validate_phone(cls, v):
        phone_pattern = r'^(\+7|8)?[\s\-\(]*(\d{3})[\s\-\)]*(\d{3})[\s\-]*(\d{2})[\s\-]*(\d{2})$'
        if not re.match(phone_pattern, v):
            raise ValueError('Invalid Russian phone number format')
        return v

class SMSRequest(BaseModel):
    phone: str
    code: str = Field(..., min_length=4, max_length=4, description="SMS verification code")

class PasswordRequest(BaseModel):
    phone: str
    password: str = Field(..., min_length=6, description="New password")
    name: Optional[str] = None
    city: Optional[str] = None

class LoginRequest(BaseModel):
    phone: str
    password: str = Field(..., min_length=6, description="User password")

class ProfileUpdateRequest(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    city: Optional[str] = None

class PasswordChangeRequest(BaseModel):
    current_password: str = Field(..., min_length=6, description="Current password")
    new_password: str = Field(..., min_length=6, description="New password")

class AuthResponse(BaseModel):
    success: bool
    message: str
    token: Optional[str] = None
