from decimal import Decimal
from pydantic import BaseModel, field_validator

class ExchangeRequest(BaseModel):
    from_currency: str
    to_currency: str
    amount: Decimal

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, value):
        if value <= 0:
            raise ValueError("Amount must be greater than 0")
        return value

    @field_validator("from_currency", "to_currency")
    @classmethod
    def validate_currency(cls, value):
        return value.upper()

class ExchangeResponse(BaseModel):
    message: str
    sold_amount: Decimal
    sold_currency: str
    bought_amount: Decimal
    bought_currency: str
    rate_used: Decimal