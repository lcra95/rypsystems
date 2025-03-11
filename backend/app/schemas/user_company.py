from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UserCompanyBase(BaseModel):
    user_id: int
    company_id: int
    status: Optional[str] = "active"

class UserCompanyCreate(UserCompanyBase):
    pass

class UserCompanyResponse(UserCompanyBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
