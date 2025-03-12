from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CompanyNumberBase(BaseModel):
    company_id: int
    number_id: int
    status: Optional[str] = "active"

class CompanyNumberCreate(CompanyNumberBase):
    pass

class CompanyNumberResponse(CompanyNumberBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
