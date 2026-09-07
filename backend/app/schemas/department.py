from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class DepartmentBase(BaseModel):
    name: str
    description: Optional[str] = None

class DepartmentCreate(DepartmentBase):
    pass

class DepartmentResponse(DepartmentBase):
    id: str
    created_at: datetime
    class Config:
        from_attributes = True

class CrossDepartmentBridgeBase(BaseModel):
    source_department_id: str
    target_department_id: str
    purpose: str

class CrossDepartmentBridgeCreate(CrossDepartmentBridgeBase):
    pass

class CrossDepartmentBridgeResponse(CrossDepartmentBridgeBase):
    id: str
    approved_by_id: str
    created_at: datetime
    class Config:
        from_attributes = True
