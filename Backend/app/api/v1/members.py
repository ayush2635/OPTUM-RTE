from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.api.deps import get_db
from app.schemas.member import MemberOut
from app.models.member import Member

router = APIRouter()


@router.get("", response_model=List[MemberOut])
async def get_members(
    skip: int = 0, limit: int = 20, db: AsyncSession = Depends(get_db)
):
    stmt = select(Member).offset(skip).limit(limit)
    result = await db.execute(stmt)
    members = result.scalars().all()
    return members


@router.get("/{member_id}", response_model=MemberOut)
async def get_member(member_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(Member).where(Member.id == member_id)
    result = await db.execute(stmt)
    member = result.scalars().first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    return member
