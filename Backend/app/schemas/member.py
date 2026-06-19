from datetime import date
from pydantic import BaseModel, ConfigDict


class MemberOut(BaseModel):
    model_config = ConfigDict(strict=True, from_attributes=True)
    id: str
    first_name: str
    last_name: str
    date_of_birth: date
    gender: str
    member_number: str
    group_number: str
