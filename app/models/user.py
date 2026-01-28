from typing import List, Optional
from beanie import Document, Indexed
from pydantic import BaseModel, Field, EmailStr
from decimal import Decimal
from datetime import datetime

class Balance(BaseModel):
    currency: str
    value: Decimal = Field(default=Decimal("0.00"))

class User(Document):
    email: Indexed(EmailStr, unique=True)
    password_hash: str
    first_name: str
    last_name: str
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.now)

    balances: List[Balance] = []

    class Settings:
        name = "users"