import random
import string
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.core.database import get_db
from app.models.complaint import Complaint, ComplaintStatus
from app.schemas.complaint import ComplaintOut, ComplaintListOut, ComplaintStatusUpdate
from app.agents.graph import run_complaint_analysis

router = APIRouter(prefix="/api/complaints", tags=["complaints"])


def _generate_complaint_number() -> str:
    suffix = "".join(random.choices(string.digits, k=6))
    return f"CMP-{datetime.utcnow().strftime('%Y%m')}-{suffix}"


@router.post("", response_model=ComplaintOut)
def create_complaint(
    customer_name: str = Form(...),
    customer_email: Optional[str] = Form(None),
    customer_phone: Optional[str] = Form(None),
    product_name: str = Form(...),
    batch_number: str = Form(...),
    manufacturing_date: Optional[str] = Form(None),
    expiry_date: Optional[str] = Form(None),
    complaint_type: str = Form(...),
    description: str = Form(...),
    source_channel: str = Form("Manual"),
    attachment: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
):
    """Creates a complaint, saves any attachment, and runs the LangGraph AI analysis pipeline
    (completeness check, risk classification, summary, root cause/CAPA, duplicate detection)
    before persisting the final record."""

    attachment_path = None
    if attachment is not None:
        import os

        os.makedirs("uploads", exist_ok=True)
        attachment_path = f"uploads/{datetime.utcnow().timestamp()}_{attachment.filename}"
        with open(attachment_path, "wb") as f:
            f.write(attachment.file.read())

    # Pull a handful of recent complaints for the same product for duplicate-checking context
    recent = (
        db.query(Complaint)
        .filter(Complaint.product_name == product_name)
        .order_by(desc(Complaint.created_at))
        .limit(10)
        .all()
    )
    existing_complaints = [
        {
            "complaint_number": c.complaint_number,
            "product_name": c.product_name,
            "batch_number": c.batch_number,
            "description": c.description,
        }
        for c in recent
    ]

    analysis = run_complaint_analysis(
        {
            "product_name": product_name,
            "batch_number": batch_number,
            "complaint_type": complaint_type,
            "description": description,
            "manufacturing_date": manufacturing_date,
            "expiry_date": expiry_date,
        },
        existing_complaints,
    )

    complaint = Complaint(
        complaint_number=_generate_complaint_number(),
        customer_name=customer_name,
        customer_email=customer_email,
        customer_phone=customer_phone,
        product_name=product_name,
        batch_number=batch_number,
        manufacturing_date=manufacturing_date,
        expiry_date=expiry_date,
        complaint_type=complaint_type,
        description=description,
        source_channel=source_channel,
        status=ComplaintStatus.NEW,
        severity=analysis.get("risk_classification"),
        ai_completeness_score=analysis.get("completeness_score"),
        ai_missing_fields=analysis.get("missing_fields"),
        ai_risk_classification=analysis.get("risk_classification"),
        ai_risk_reasoning=analysis.get("risk_reasoning"),
        ai_summary=analysis.get("summary"),
        ai_root_cause_suggestion=analysis.get("root_cause_suggestion"),
        ai_capa_suggestion=analysis.get("capa_suggestion"),
        ai_duplicate_of=analysis.get("duplicate_of"),
        attachment_path=attachment_path,
    )
    db.add(complaint)
    db.commit()
    db.refresh(complaint)
    return complaint


@router.get("", response_model=ComplaintListOut)
def list_complaints(
    status: Optional[str] = None,
    severity: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    query = db.query(Complaint)
    if status:
        query = query.filter(Complaint.status == status)
    if severity:
        query = query.filter(Complaint.severity == severity)
    total = query.count()
    items = query.order_by(desc(Complaint.created_at)).offset(skip).limit(limit).all()
    return {"total": total, "items": items}


@router.get("/{complaint_id}", response_model=ComplaintOut)
def get_complaint(complaint_id: str, db: Session = Depends(get_db)):
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    return complaint


@router.patch("/{complaint_id}/status", response_model=ComplaintOut)
def update_status(complaint_id: str, payload: ComplaintStatusUpdate, db: Session = Depends(get_db)):
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    if payload.status not in [s.value for s in ComplaintStatus]:
        raise HTTPException(status_code=400, detail="Invalid status value")
    complaint.status = payload.status
    db.commit()
    db.refresh(complaint)
    return complaint
