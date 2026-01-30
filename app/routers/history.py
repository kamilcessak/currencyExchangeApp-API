from fastapi import APIRouter, Depends
from typing import List
from app.models.transaction import Transaction
from app.schemas import TransactionResponse
from app.utils.security import get_current_user
from app.models.user import User

router = APIRouter(prefix="/history", tags=["History"])

@router.get("/", response_model=List[TransactionResponse])
async def get_my_history(current_user: User = Depends(get_current_user)):
    history = await Transaction.find(
        Transaction.user_id == str(current_user.id)
    ).sort(-Transaction.created_at).to_list()

    return history