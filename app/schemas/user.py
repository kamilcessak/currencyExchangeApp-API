from typing import Annotated
from pydantic import BaseModel, EmailStr, field_validator, BeforeValidator
import string
from decimal import Decimal

PyObjectId = Annotated[str, BeforeValidator(str)]

class UserRegister(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str

    # Password validation
    @field_validator("password")
    @classmethod
    def validate_password(cls, value):
        if(len(value) < 8):
            raise ValueError("Password must be at least 8 characters long")
        if not any(char.isdigit() for char in value):
            raise ValueError("Password must contain at least one digit")
        if not any(char in string.punctuation for char in value):
            raise ValueError("Password must contain at least one special character")
        return value

    # Empty value validation
    @field_validator("email", "first_name", "last_name")
    @classmethod
    def validate_empty_values(cls, value):
        if not value.strip():
            raise ValueError("Field cannot be empty")
        return value

class UserResponse(BaseModel):
    id: PyObjectId
    email: EmailStr
    first_name: str
    last_name: str

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str