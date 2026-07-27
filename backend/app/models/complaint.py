import enum
import uuid
from datetime import datetime

from sqlalchemy import Column, String, Text, DateTime, Enum, JSON, Float
from app.core.database import Base


class ComplaintStatus(str, enum.Enum):
    NEW = "New"
    UNDER_INVESTIGATION = "Under Investigation"
    CAPA_INITIATED = "CAPA Initiated"
    CLOSED = "Closed"


class ComplaintSeverity(str, enum.Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class Complaint(Base):
    __tablename__ = "complaints"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    complaint_number = Column(String(30), unique=True, nullable=False)

    # Reporter / customer info
    customer_name = Column(String(255), nullable=False)
    customer_email = Column(String(255), nullable=True)
    customer_phone = Column(String(50), nullable=True)

    # Product / batch info — core to a pharma QMS complaint record
    product_name = Column(String(255), nullable=False)
    batch_number = Column(String(100), nullable=False)
    manufacturing_date = Column(String(50), nullable=True)
    expiry_date = Column(String(50), nullable=True)

    complaint_type = Column(String(100), nullable=False)  # e.g. Quality, Packaging, Adverse Event, Delivery
    description = Column(Text, nullable=False)
    source_channel = Column(String(50), default="Manual")  # Manual, Email, PDF Upload

    status = Column(Enum(ComplaintStatus), default=ComplaintStatus.NEW, nullable=False)
    severity = Column(Enum(ComplaintSeverity), nullable=True)

    # AI-generated fields (populated by the LangGraph pipeline)
    ai_completeness_score = Column(Float, nullable=True)
    ai_missing_fields = Column(JSON, nullable=True)
    ai_risk_classification = Column(String(50), nullable=True)
    ai_risk_reasoning = Column(Text, nullable=True)
    ai_summary = Column(Text, nullable=True)
    ai_root_cause_suggestion = Column(Text, nullable=True)
    ai_capa_suggestion = Column(Text, nullable=True)
    ai_duplicate_of = Column(String(36), nullable=True)  # complaint_number of suspected duplicate

    attachment_path = Column(String(500), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
