from typing import Optional
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from app.models.logs import LogStatus

class UnparsedLogBase(BaseModel):
    raw_text: str
    source: str
    
class UnparsedLogCreate(UnparsedLogBase):
    pass

class UnparsedLogResponse(UnparsedLogBase):
    id: int
    status: LogStatus
    created_at: datetime
    resolved_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)