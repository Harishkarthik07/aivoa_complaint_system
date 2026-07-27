from typing import TypedDict, Optional, List


class ComplaintAgentState(TypedDict, total=False):
    # Input
    product_name: str
    batch_number: str
    complaint_type: str
    description: str
    manufacturing_date: Optional[str]
    expiry_date: Optional[str]
    existing_complaints: List[dict]  # recent complaints for duplicate check, e.g. [{"complaint_number", "product_name", "batch_number", "description"}]

    # Output (filled in by nodes as the graph runs)
    completeness_score: Optional[float]
    missing_fields: Optional[List[str]]
    risk_classification: Optional[str]
    risk_reasoning: Optional[str]
    summary: Optional[str]
    root_cause_suggestion: Optional[str]
    capa_suggestion: Optional[str]
    duplicate_of: Optional[str]
