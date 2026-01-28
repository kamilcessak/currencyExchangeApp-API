from decimal import Decimal
from pydantic import BaseModel, field_validator

class TopUpRequest(BaseModel):
    currency: str = "PLN"
    amount: Decimal

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, value):
        if value <= 0:
            raise ValueError("Amount must be greater than 0")
        return value
    
    @field_validator("currency")
    @classmethod
    def validate_currency(cls, value):
        return value.upper()

class BalanceResponse(BaseModel):
    currency: str
    value: Decimal