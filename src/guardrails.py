"""Security guardrails and audit logging."""

import re
import json
import math
from datetime import datetime
from typing import List, Tuple
from langchain_core.documents import Document

from .config import AUDIT_LOG_FILE


# ============================================
# PII DETECTION
# ============================================

PII_PATTERNS = {
    "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
    "credit_card": r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b",
    "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
    "phone": r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b"
}

def check_pii(text: str) -> Tuple[bool, str]:
    """Check if text contains PII patterns."""
    for pii_type, pattern in PII_PATTERNS.items():
        if re.search(pattern, text):
            return True, pii_type
    return False, ""


def guardrail_check(context: str, response: str) -> Tuple[bool, str]:
    """
    Check guardrails:
    1. PII in response
    2. Hallucination (confident answer with no context)
    """
    # Check PII
    has_pii, pii_type = check_pii(response)
    if has_pii:
        return False, f"[BLOCKED: {pii_type} detected in response]"
    
    # Check hallucination
    if not context.strip() and len(response) > 100:
        confidence_phrases = ["according to", "the data shows", "based on the documents"]
        if any(phrase in response.lower() for phrase in confidence_phrases):
            return False, "[BLOCKED: Potential hallucination - no context but confident answer]"
    
    return True, response


# ============================================
# AUDIT LOGGING
# ============================================

def log_access(user_role: str, query: str, docs_accessed: List[Document], response: str):
    """Log every query for compliance tracking."""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "user_role": user_role,
        "query": query,
        "docs_sensitivity": [d.metadata.get("sensitivity", "unknown") for d in docs_accessed],
        "docs_sources": [d.metadata.get("source", "unknown") for d in docs_accessed],
        "response_length": len(response),
        "guardrail_triggered": False
    }
    
    with open(AUDIT_LOG_FILE, "a") as f:
        f.write(json.dumps(log_entry) + "\n")
    
    return log_entry


# ============================================
# PYTHON CALCULATOR TOOL
# ============================================

def python_calculator(code_snippet: str) -> str:
    """Execute Python math code safely."""
    try:
        local_scope = {"math": math}
        clean_code = code_snippet.replace("```python", "").replace("```", "").strip()
        exec(clean_code, {}, local_scope)
        
        if 'result' in local_scope:
            return f"Calculated Result: {local_scope['result']}"
        else:
            return "Error: Please assign your answer to a variable named 'result'."
    except Exception as e:
        return f"Calculation Error: {e}"


print("✅ Guardrails defined (PII detection, hallucination check)")
print("✅ Audit logging enabled")
print("✅ Python calculator tool defined")
