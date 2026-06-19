from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_
import itertools
from app.schemas.eligibility import (
    EligibilityRequest,
    EligibilityResponse,
    ScrubResult,
    ScrubStatus,
    EligibilityStatus,
)
from app.models.member import Member
from app.models.coding_rule import CodingRule
from app.schemas.member import MemberOut
from app.services.eligibility import check_coverage_window
import json
import os

DATA_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data"
)


def check_code_validity(cpt_codes, icd10_codes):
    results = []
    valid_cpts = set(["99213", "99214", "71046", "99201", "85025", "80053", "36415"])
    valid_icds = set(["J18.9", "I10", "E11.9", "M54.5", "Z00.00"])
    for cpt in cpt_codes:
        if cpt not in valid_cpts:
            results.append(
                ScrubResult(
                    cpt_code=cpt, result=ScrubStatus.DENIED, message="Unknown CPT code"
                )
            )
    return results


async def check_ncci_edits(cpt_codes, db: AsyncSession):
    results = []
    pairs = list(itertools.combinations(cpt_codes, 2))
    conflicted = set()
    for cpt_a, cpt_b in pairs:
        stmt = select(CodingRule).where(
            or_(
                and_(CodingRule.column1_cpt == cpt_a, CodingRule.column2_cpt == cpt_b),
                and_(CodingRule.column1_cpt == cpt_b, CodingRule.column2_cpt == cpt_a),
            )
        )
        res = await db.execute(stmt)
        rule = res.scalars().first()
        if rule:
            if rule.modifier_indicator == 0:
                results.append(
                    ScrubResult(
                        cpt_code=cpt_a,
                        result=ScrubStatus.DENIED,
                        message="NCCI Edit Conflict",
                        ncci_conflict_with=cpt_b,
                    )
                )
                conflicted.add(cpt_a)
            else:
                results.append(
                    ScrubResult(
                        cpt_code=cpt_a,
                        result=ScrubStatus.WARNING,
                        message="Allowed with modifier",
                        ncci_conflict_with=cpt_b,
                    )
                )
                conflicted.add(cpt_a)
    for cpt in cpt_codes:
        if cpt not in conflicted and not any(r.cpt_code == cpt for r in results):
            results.append(
                ScrubResult(
                    cpt_code=cpt, result=ScrubStatus.APPROVED, message="Code valid"
                )
            )
    return results


async def run_full_scrub(
    request: EligibilityRequest, db: AsyncSession
) -> EligibilityResponse:
    stmt = select(Member).where(Member.member_number == request.member_id)
    result = await db.execute(stmt)
    member = result.scalars().first()
    if not member:
        return EligibilityResponse(
            transaction_id=request.transaction_id,
            status=EligibilityStatus.NOT_FOUND,
            message="Member not found",
        )
    if member.date_of_birth != request.date_of_birth:
        return EligibilityResponse(
            transaction_id=request.transaction_id,
            status=EligibilityStatus.NOT_FOUND,
            message="Member not found",
        )
    coverage_status, coverage_detail = await check_coverage_window(
        member.id, request.date_of_service, db
    )
    validity_results = check_code_validity(
        request.proposed_cpt_codes, request.diagnosis_codes
    )
    invalid_cpts = {r.cpt_code for r in validity_results}
    ncci_results = []
    if coverage_status == EligibilityStatus.ACTIVE:
        valid_proposed = [
            c for c in request.proposed_cpt_codes if c not in invalid_cpts
        ]
        ncci_results = await check_ncci_edits(valid_proposed, db)
    scrubbing_results = validity_results + ncci_results
    return EligibilityResponse(
        transaction_id=request.transaction_id,
        status=coverage_status,
        member_details=MemberOut.model_validate(member),
        coverage_details=coverage_detail,
        scrubbing_results=scrubbing_results,
    )
