import asyncio
from faker import Faker
import random
from datetime import timedelta, date
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import engine, AsyncSessionLocal, Base
from app.models.member import Member
from app.models.plan import HealthPlan
from app.models.coverage import Coverage
from app.models.coding_rule import CodingRule

faker = Faker("en_US")


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


async def seed_plans(db: AsyncSession):
    plans = [
        HealthPlan(
            plan_code="PPO_GOLD",
            plan_name="Gold PPO",
            deductible_amount=1000,
            copay_primary_care=20,
            copay_specialist=40,
            out_of_pocket_max=5000,
        ),
        HealthPlan(
            plan_code="HMO_SILVER",
            plan_name="Silver HMO",
            deductible_amount=2000,
            copay_primary_care=30,
            copay_specialist=60,
            out_of_pocket_max=6000,
        ),
        HealthPlan(
            plan_code="HDHP_BRONZE",
            plan_name="Bronze HDHP",
            deductible_amount=3000,
            copay_primary_care=50,
            copay_specialist=100,
            out_of_pocket_max=7000,
        ),
    ]
    db.add_all(plans)
    await db.commit()
    for plan in plans:
        await db.refresh(plan)
    return plans


async def seed_rules(db: AsyncSession):
    rules = [
        CodingRule(
            column1_cpt="99213",
            column2_cpt="99214",
            modifier_indicator=0,
            effective_date=date(2023, 1, 1),
        ),
        CodingRule(
            column1_cpt="71045",
            column2_cpt="71046",
            modifier_indicator=1,
            effective_date=date(2023, 1, 1),
        ),
    ]
    db.add_all(rules)
    await db.commit()


async def seed_members(db: AsyncSession, plans: list[HealthPlan]):
    groups = [f"GRP-{i}" for i in range(1000, 1010)]
    members = []
    coverages = []
    for i in range(120):
        m = Member(
            first_name=faker.first_name(),
            last_name=faker.last_name(),
            date_of_birth=faker.date_of_birth(minimum_age=18, maximum_age=80),
            gender=random.choice(["M", "F"]),
            ssn_last4=faker.numerify("####"),
            member_number=f"OPT-{faker.numerify('######')}",
            group_number=random.choice(groups),
        )
        members.append(m)
    db.add_all(members)
    await db.commit()
    for m in members:
        await db.refresh(m)
        plan = random.choice(plans)
        is_active = random.random() < 0.8
        eff_date = date.today() - timedelta(days=random.randint(100, 500))
        term_date = None
        if not is_active:
            term_date = date.today() - timedelta(days=random.randint(1, 180))
        c = Coverage(
            member_id=m.id,
            plan_id=plan.id,
            effective_date=eff_date,
            termination_date=term_date,
            subscriber_relationship="SELF",
            is_active=is_active,
        )
        coverages.append(c)
    db.add_all(coverages)
    await db.commit()


async def main():
    await create_tables()
    async with AsyncSessionLocal() as db:
        plans = await seed_plans(db)
        await seed_rules(db)
        await seed_members(db, plans)
        print("Database seeded successfully.")


if __name__ == "__main__":
    asyncio.run(main())
