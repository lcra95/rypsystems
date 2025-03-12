from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class NumberBase(BaseModel):
    number_type: str
    number: str
    account_sid: Optional[str] = None
    auth_token: Optional[str] = None
    agente_id: Optional[str] = None
    status: Optional[str] = "active"
    agent_status: Optional[bool] = False

class NumberCreate(NumberBase):
    company_id: Optional[int] = None  # Para asociar directamente al crear

class NumberUpdate(NumberBase):
    pass

class NumberResponse(NumberBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
