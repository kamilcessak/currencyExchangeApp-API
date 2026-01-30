from typing import Annotated
from decimal import Decimal
from bson import Decimal128
from pydantic import BeforeValidator

def convert_decimal128(value):
    if isinstance(value, Decimal128):
        return value.to_decimal()
    return value

MongoDecimal = Annotated[Decimal, BeforeValidator(convert_decimal128)]