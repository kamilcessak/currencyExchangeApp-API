from decimal import Decimal
from pydantic import BaseModel
from datetime import date

class RateResponse(BaseModel):
    currency_code: str
    rate: Decimal
    last_updated: date
    