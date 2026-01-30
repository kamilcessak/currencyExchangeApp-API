from typing import List, Optional, Annotated
from beanie import Document, Indexed
from pydantic import BaseModel, Field, EmailStr, BeforeValidator
from decimal import Decimal
from datetime import datetime
from bson import Decimal128
from app.utils.types import MongoDecimal

class Balance(BaseModel):
    currency: str
    value: MongoDecimal = Field(default=Decimal("0.00"))

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