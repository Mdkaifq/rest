from pydantic import BaseModel
from typing import List, Optional
import uuid
from datetime import datetime

class CaseType(BaseModel):
    id: Optional[uuid.UUID] = None
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    created_by: Optional[uuid.UUID] = None
    created_on: Optional[datetime] = None
    assignee: Optional[uuid.UUID] = None
    status_change_reason: Optional[str] = None
    comment: Optional[str] = None
    watchers: Optional[List[str]] = None
    updated_by: Optional[uuid.UUID] = None
    updated_on: Optional[datetime] = None
    message: Optional[str] = None

class CaseStatusType(BaseModel):
    category: str
    count: int

class DistinctValueType(BaseModel):
    field: str
    title: str

class CreateCaseRequest(BaseModel):
    title: str
    description: str
    status: str

class UpdateCaseRequest(BaseModel):
    description: Optional[str] = None
    status: Optional[str] = None
    assignee: Optional[uuid.UUID] = None
    status_change_reason: Optional[str] = None
    comment: Optional[str] = None
    watchers: Optional[List[str] | str] = None
