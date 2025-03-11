from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CompanyBase(BaseModel):
    document: str
    name: str
    direction: Optional[str] = None
    business: Optional[str] = None
    contact_person: Optional[str] = None
    contact_number: Optional[str] = None
    status: Optional[str] = "active"

class CompanyCreate(CompanyBase):
    pass

class CompanyUpdate(CompanyBase):
    pass

class CompanyResponse(CompanyBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
