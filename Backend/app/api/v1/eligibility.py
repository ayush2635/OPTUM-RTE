from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_db, get_current_user
from app.schemas.eligibility import EligibilityRequest, EligibilityResponse
from app.services.rules_engine import run_full_scrub

router = APIRouter()


@router.post("", response_model=EligibilityResponse)
async def check_eligibility(
    request: EligibilityRequest,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(get_current_user),
):
    response = await run_full_scrub(request, db)
    return response
