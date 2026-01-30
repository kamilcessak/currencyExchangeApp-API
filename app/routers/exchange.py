from fastapi import APIRouter, HTTPException, status, Depends
from decimal import Decimal, ROUND_HALF_UP
from app.models.user import User, Balance
from app.models.rate import Rate
from app.models.transaction import Transaction
from app.schemas import ExchangeRequest, ExchangeResponse
from app.utils.security import get_current_user

router = APIRouter(prefix="/exchange", tags=["Exchange"])

async def get_rate_value(currency_code: str) -> Decimal:
    if currency_code == "PLN":
        return Decimal("1.0")

    rate_doc = await Rate.find_one(Rate.currency_code == currency_code)

    if not rate_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Exchange rate for {currency_code} not found"
        )
    
    return rate_doc.rate

@router.post("/", response_model=ExchangeResponse)
async def exchange_currency(
    data: ExchangeRequest,
    current_user: User = Depends(get_current_user)
):
    if data.from_currency == data.to_currency:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="From and to currencies cannot be the same"
        )
    
    rate_from = await get_rate_value(data.from_currency)
    rate_to = await get_rate_value(data.to_currency)

    cross_rate = rate_from / rate_to

    amount_sold = data.amount
    amount_bought = amount_sold * cross_rate
    amount_bought = amount_bought.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    source_balance = next((b for b in current_user.balances if b.currency == data.from_currency), None)

    if not source_balance or source_balance.value < amount_sold:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Insufficient balance for {data.from_currency}"
        )

    source_balance.value -= amount_sold

    target_balance = next((b for b in current_user.balances if b.currency == data.to_currency), None)

    if target_balance:
        target_balance.value += amount_bought
    else:
        new_balance = Balance(currency=data.to_currency, value=amount_bought)
        current_user.balances.append(new_balance)

    await current_user.save()

    await Transaction(
        user_id=str(current_user.id),
        sold_currency=data.from_currency,
        sold_amount=amount_sold,
        bought_currency=data.to_currency,
        bought_amount=amount_bought,
        rate=cross_rate
    ).create()

    return{
        "message": "Currency exchanged successfully",
        "sold_amount": amount_sold,
        "sold_currency": data.from_currency,
        "bought_amount": amount_bought,
        "bought_currency": data.to_currency,
        "rate_used": cross_rate
    }
