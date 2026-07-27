import json
import re
from langchain_groq import ChatGroq
from app.core.config import settings

_llm = None


def get_llm(temperature: float = 0.0):
    global _llm
    if _llm is None:
        _llm = ChatGroq(
            api_key=settings.GROQ_API_KEY,
            model=settings.GROQ_MODEL,
            temperature=temperature,
        )
    return _llm


def call_llm_json(prompt: str) -> dict:
    """Calls the LLM and expects a JSON object back. Strips markdown fences if present."""
    llm = get_llm()
    response = llm.invoke(prompt)
    text = response.content.strip()
    text = re.sub(r"^```json|^```|```$", "", text, flags=re.MULTILINE).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Best-effort: extract the first {...} block
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        raise
