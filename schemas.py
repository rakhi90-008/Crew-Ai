from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ParsedResult(BaseModel):
    vendor: Optional[str]
    invoice_no: Optional[str]
    date: Optional[str]
    total: Optional[str]

class DocumentCreate(BaseModel):
    filename: Optional[str]
    raw_text: str

class DocumentResponse(BaseModel):
    id: int
    filename: Optional[str]
    raw_text: str
    parsed: ParsedResult
    task_id: Optional[str]
    status: Optional[str]
    created_at: Optional[datetime]

    class Config:
        orm_mode = True

class TaskStatus(BaseModel):
    task_id: str
    status: str
    result: Optional[ParsedResult]
