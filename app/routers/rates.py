from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from app.schemas import RateResponse
from app.models.rate import Rate
from app.utils.nbp import sync_rates_with_nbp
from app.utils.security import get_current_user

router = APIRouter(prefix="/rates", tags=["Exchange Rates"])

@router.post("/sync", status_code=status.HTTP_200_OK)
async def sync_nbp_rates(current_user = Depends(get_current_user)):
    count = await sync_rates_with_nbp()
    if count == 0:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Failed to sync rates with NBP"
        )
    return {
        "message": f"Successfully synced {count} rates with NBP"
    }

@router.get("/", response_model=List[RateResponse])
async def get_current_rates():
    rates = await Rate.find_all().to_list()
    return rates