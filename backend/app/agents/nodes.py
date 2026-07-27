from app.agents.state import ComplaintAgentState
from app.agents.llm import call_llm_json


def completeness_check_node(state: ComplaintAgentState) -> ComplaintAgentState:
    """Checks whether the complaint has enough information for a pharma QMS investigation."""
    prompt = f"""You are a Quality Assurance reviewer at a pharmaceutical manufacturing company.
Assess whether the following customer complaint has enough information to begin an investigation.

Required context for a complete pharma complaint: product name, batch/lot number, clear description
of the defect/issue, and (ideally) manufacturing/expiry date and how the issue was discovered.

Product: {state.get('product_name')}
Batch Number: {state.get('batch_number')}
Complaint Type: {state.get('complaint_type')}
Manufacturing Date: {state.get('manufacturing_date')}
Expiry Date: {state.get('expiry_date')}
Description: {state.get('description')}

Respond ONLY with a JSON object, no other text:
{{
  "completeness_score": <float 0.0-1.0>,
  "missing_fields": [<list of missing or unclear field names as strings>]
}}
"""
    result = call_llm_json(prompt)
    state["completeness_score"] = result.get("completeness_score", 0.5)
    state["missing_fields"] = result.get("missing_fields", [])
    return state


def risk_classification_node(state: ComplaintAgentState) -> ComplaintAgentState:
    """Classifies the complaint's risk/severity per typical pharma QMS risk categories."""
    prompt = f"""You are a Quality Assurance risk assessor at a pharmaceutical manufacturing company.
Classify the risk level of this customer complaint using these categories: Low, Medium, High, Critical.

Guidance:
- Critical: potential patient safety issue, adverse health event, contamination, wrong product/label
- High: product defect affecting efficacy or safety perception, sterility/potency concerns
- Medium: quality defect not directly safety-related (e.g. packaging damage, discoloration)
- Low: cosmetic, delivery, or non-product issues

Complaint Type: {state.get('complaint_type')}
Description: {state.get('description')}

Respond ONLY with a JSON object, no other text:
{{
  "risk_classification": "<Low|Medium|High|Critical>",
  "risk_reasoning": "<1-2 sentence justification>"
}}
"""
    result = call_llm_json(prompt)
    state["risk_classification"] = result.get("risk_classification", "Medium")
    state["risk_reasoning"] = result.get("risk_reasoning", "")
    return state


def summary_node(state: ComplaintAgentState) -> ComplaintAgentState:
    """Produces a concise investigator-facing summary of the complaint."""
    prompt = f"""Summarize the following pharmaceutical customer complaint in 2-3 sentences for a
quality investigator who needs the key facts quickly (product, batch, issue, any safety concern).

Product: {state.get('product_name')}
Batch Number: {state.get('batch_number')}
Complaint Type: {state.get('complaint_type')}
Description: {state.get('description')}

Respond ONLY with a JSON object, no other text:
{{
  "summary": "<2-3 sentence summary>"
}}
"""
    result = call_llm_json(prompt)
    state["summary"] = result.get("summary", "")
    return state


def root_cause_capa_node(state: ComplaintAgentState) -> ComplaintAgentState:
    """Suggests a plausible root cause and CAPA (Corrective and Preventive Action) for the complaint."""
    prompt = f"""You are a Quality Assurance investigator at a pharmaceutical manufacturing plant.
Based on this complaint, suggest a plausible root cause hypothesis and a preliminary CAPA
(Corrective and Preventive Action) recommendation. These are starting hypotheses for a human
investigator, not final conclusions.

Product: {state.get('product_name')}
Batch Number: {state.get('batch_number')}
Complaint Type: {state.get('complaint_type')}
Description: {state.get('description')}
Risk Classification: {state.get('risk_classification')}

Respond ONLY with a JSON object, no other text:
{{
  "root_cause_suggestion": "<1-2 sentence plausible root cause hypothesis>",
  "capa_suggestion": "<1-2 sentence preliminary CAPA recommendation>"
}}
"""
    result = call_llm_json(prompt)
    state["root_cause_suggestion"] = result.get("root_cause_suggestion", "")
    state["capa_suggestion"] = result.get("capa_suggestion", "")
    return state


def duplicate_detection_node(state: ComplaintAgentState) -> ComplaintAgentState:
    """Compares against recent complaints (passed in via existing_complaints) to flag likely duplicates."""
    existing = state.get("existing_complaints") or []
    if not existing:
        state["duplicate_of"] = None
        return state

    existing_text = "\n".join(
        f"- {c.get('complaint_number')}: product={c.get('product_name')}, "
        f"batch={c.get('batch_number')}, description={c.get('description')}"
        for c in existing
    )

    prompt = f"""You are checking whether a new pharmaceutical complaint is a likely duplicate of any
recent complaint already on file. A duplicate means same product, same batch, and a substantially
similar issue described (not just the same product line).

New Complaint:
Product: {state.get('product_name')}
Batch Number: {state.get('batch_number')}
Description: {state.get('description')}

Recent complaints on file:
{existing_text}

Respond ONLY with a JSON object, no other text:
{{
  "is_duplicate": <true|false>,
  "duplicate_of": "<complaint_number if is_duplicate is true, else null>"
}}
"""
    result = call_llm_json(prompt)
    state["duplicate_of"] = result.get("duplicate_of") if result.get("is_duplicate") else None
    return state
