from fastapi import APIRouter
from app.api.v1 import auth, eligibility, members

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(
    eligibility.router, prefix="/eligibility", tags=["eligibility"]
)
api_router.include_router(members.router, prefix="/members", tags=["members"])
