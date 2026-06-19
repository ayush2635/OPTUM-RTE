from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import date
from app.models.coverage import Coverage
from app.schemas.eligibility import EligibilityStatus, CoverageOut
from decimal import Decimal
from app.models.plan import HealthPlan


async def check_coverage_window(
    member_id: str, date_of_service: date, db: AsyncSession
):
    stmt = (
        select(Coverage)
        .where(Coverage.member_id == member_id)
        .order_by(Coverage.effective_date.desc())
    )
    result = await db.execute(stmt)
    coverages = result.scalars().all()
    if not coverages:
        return EligibilityStatus.NOT_FOUND, None
    for cov in coverages:
        if cov.effective_date <= date_of_service:
            if cov.termination_date is None or cov.termination_date >= date_of_service:
                plan_stmt = select(HealthPlan).where(HealthPlan.id == cov.plan_id)
                plan_result = await db.execute(plan_stmt)
                plan = plan_result.scalars().first()
                if plan:
                    return EligibilityStatus.ACTIVE, CoverageOut(
                        plan_name=plan.plan_name,
                        effective_date=cov.effective_date,
                        termination_date=cov.termination_date,
                        copay_amount=Decimal(str(plan.copay_primary_care)),
                        deductible_remaining=Decimal(str(plan.deductible_amount)),
                        out_of_pocket_max=Decimal(str(plan.out_of_pocket_max)),
                    )
                else:
                    return EligibilityStatus.INACTIVE, None
    return EligibilityStatus.INACTIVE, None
