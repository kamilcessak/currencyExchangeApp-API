from datetime import date
from beanie import Document, Indexed
from pydantic import Field
from app.utils.types import MongoDecimal

class Rate(Document):
    currency_code: Indexed(str, unique=True)
    rate: MongoDecimal
    last_updated: date = Field(default_factory=date.today)

    class Settings:
        name = "rates"