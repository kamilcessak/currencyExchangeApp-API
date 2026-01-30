from pydantic import BaseModel
from decimal import Decimal
from datetime import datetime

class TransactionResponse(BaseModel):
    sold_currency: str
    sold_amount: Decimal
    bought_currency: str
    bought_amount: Decimal
    rate: Decimal
    created_at: datetime