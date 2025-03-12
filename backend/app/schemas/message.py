from pydantic import BaseModel
from datetime import datetime

class MessageBase(BaseModel):
    to: str
    from_: str
    direction: str
    message: str  # <-- Nuevo campo agregado
    number_id: int

class MessageCreate(MessageBase):
    pass

class MessageResponse(MessageBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
