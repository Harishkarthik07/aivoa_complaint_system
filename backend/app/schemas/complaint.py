from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class ComplaintCreate(BaseModel):
    customer_name: str
    customer_email: Optional[str] = None
    customer_phone: Optional[str] = None
    product_name: str
    batch_number: str
    manufacturing_date: Optional[str] = None
    expiry_date: Optional[str] = None
    complaint_type: str
    description: str
    source_channel: Optional[str] = "Manual"


class ComplaintStatusUpdate(BaseModel):
    status: str


class ComplaintOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    complaint_number: str
    customer_name: str
    customer_email: Optional[str] = None
    customer_phone: Optional[str] = None
    product_name: str
    batch_number: str
    manufacturing_date: Optional[str] = None
    expiry_date: Optional[str] = None
    complaint_type: str
    description: str
    source_channel: str
    status: str
    severity: Optional[str] = None

    ai_completeness_score: Optional[float] = None
    ai_missing_fields: Optional[List[str]] = None
    ai_risk_classification: Optional[str] = None
    ai_risk_reasoning: Optional[str] = None
    ai_summary: Optional[str] = None
    ai_root_cause_suggestion: Optional[str] = None
    ai_capa_suggestion: Optional[str] = None
    ai_duplicate_of: Optional[str] = None

    attachment_path: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class ComplaintListOut(BaseModel):
    total: int
    items: List[ComplaintOut]
