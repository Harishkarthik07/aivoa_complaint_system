"""Seeds the database with a few realistic pharma complaint examples for demo purposes.
Run with: python seed_data.py (from the backend/ directory, with .env configured and
the API server NOT required to be running — this talks to the DB directly, but reuses
the same AI pipeline so seeded records also get AI analysis.)
"""
from app.core.database import SessionLocal, Base, engine
from app.models.complaint import Complaint, ComplaintStatus
from app.agents.graph import run_complaint_analysis
from datetime import datetime
import random
import string

SAMPLE_COMPLAINTS = [
    {
        "customer_name": "Ramesh Iyer",
        "customer_email": "ramesh.iyer@example.com",
        "product_name": "Amoxiclav 625mg Tablets",
        "batch_number": "AMX-2026-0417",
        "manufacturing_date": "2025-04-01",
        "expiry_date": "2027-03-31",
        "complaint_type": "Quality",
        "description": (
            "Received a strip of 10 tablets where 3 tablets appear discolored (yellowish-brown "
            "instead of white) and slightly crumbling at the edges. Rest of the strip looks normal. "
            "Noticed this before consuming, no adverse reaction experienced."
        ),
    },
    {
        "customer_name": "Sunita Deshmukh",
        "customer_email": "sunita.d@example.com",
        "product_name": "Cefixime 200mg Tablets",
        "batch_number": "CFX-2026-0289",
        "manufacturing_date": "2025-11-10",
        "expiry_date": "2027-11-09",
        "complaint_type": "Adverse Event",
        "description": (
            "Patient developed a severe skin rash and difficulty breathing within an hour of taking "
            "the first dose. Discontinued immediately and sought emergency care. Suspecting a possible "
            "contamination or mislabeling issue given the severity."
        ),
    },
    {
        "customer_name": "Vikram Nair",
        "customer_email": "vikram.nair@example.com",
        "product_name": "Amoxiclav 625mg Tablets",
        "batch_number": "AMX-2026-0417",
        "manufacturing_date": "2025-04-01",
        "expiry_date": "2027-03-31",
        "complaint_type": "Quality",
        "description": (
            "Two tablets in the blister pack are discolored yellow-brown and appear to be breaking apart. "
            "Same batch number as printed on the box. Have not taken the tablets yet."
        ),
    },
    {
        "customer_name": "Priya Menon",
        "customer_email": "priya.menon@example.com",
        "product_name": "Paracetamol 500mg Tablets",
        "batch_number": "PCM-2026-1102",
        "manufacturing_date": "2025-06-15",
        "expiry_date": "2028-06-14",
        "complaint_type": "Packaging",
        "description": (
            "Outer carton was damp and the strip inside was partially exposed to air due to a torn "
            "foil seal. Tablets look physically fine, just the packaging seal was compromised."
        ),
    },
]


def run():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        for entry in SAMPLE_COMPLAINTS:
            recent = (
                db.query(Complaint)
                .filter(Complaint.product_name == entry["product_name"])
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
                    "product_name": entry["product_name"],
                    "batch_number": entry["batch_number"],
                    "complaint_type": entry["complaint_type"],
                    "description": entry["description"],
                    "manufacturing_date": entry["manufacturing_date"],
                    "expiry_date": entry["expiry_date"],
                },
                existing_complaints,
            )

            suffix = "".join(random.choices(string.digits, k=6))
            complaint = Complaint(
                complaint_number=f"CMP-{datetime.utcnow().strftime('%Y%m')}-{suffix}",
                customer_name=entry["customer_name"],
                customer_email=entry["customer_email"],
                product_name=entry["product_name"],
                batch_number=entry["batch_number"],
                manufacturing_date=entry["manufacturing_date"],
                expiry_date=entry["expiry_date"],
                complaint_type=entry["complaint_type"],
                description=entry["description"],
                source_channel="Manual",
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
            )
            db.add(complaint)
            db.commit()
            print(f"Seeded {complaint.complaint_number} - {complaint.product_name} ({complaint.severity})")
    finally:
        db.close()


if __name__ == "__main__":
    run()
