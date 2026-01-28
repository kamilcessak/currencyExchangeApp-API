from fastapi import APIRouter, Depends, HTTPException, status
from app.models.user import User, Balance
from app.schemas import TopUpRequest, BalanceResponse
from app.utils.security import get_current_user
from typing import List

router = APIRouter(prefix="/wallet", tags=["Wallet"])

@router.get("/", response_model=List[BalanceResponse])
async def get_wallet_status(current_user: User = Depends(get_current_user)):
    return current_user.balances

@router.post("/topup", response_model=List[BalanceResponse])
async def top_up_wallet(data: TopUpRequest, current_user: User = Depends(get_current_user)):
    found = False
    for balance in current_user.balances:
        if balance.currency == data.currency:
            balance.value += data.amount
            found = True
            break
    
    if not found:
        new_balance = Balance(currency=data.currency, value=data.amount)
        current_user.balances.append(new_balance)

    await current_user.save()

    return current_user.balances