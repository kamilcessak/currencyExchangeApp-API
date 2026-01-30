from datetime import datetime
from beanie import Document
from pydantic import Field
from decimal import Decimal
from app.utils.types import MongoDecimal
from typing import Optional

class Transaction(Document):
    user_id: str
    sold_currency: str
    sold_amount: MongoDecimal
    bought_currency: str
    bought_amount: MongoDecimal
    rate: MongoDecimal
    created_at: datetime = Field(default_factory=datetime.now)

    class Settings:
        name = "transactions"