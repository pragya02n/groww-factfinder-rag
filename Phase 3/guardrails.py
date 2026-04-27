"""
Phase 3: Guardrail & Safety Layer
- PII Masking: Detects PAN ([A-Z]{5}[0-9]{4}[A-Z]) and Aadhaar (12-digit).
- Intent Classification: Detects requests for investment advice.
- Refusal Logic: Factual-only mandate.
"""
import re

# --- PII REGEX PATTERNS ---
PAN_PATTERN = re.compile(r"\b[A-Z]{5}[0-9]{4}[A-Z]\b", re.IGNORECASE)
AADHAAR_PATTERN = re.compile(r"\b\d{12,16}\b") # Covers 12 and 16 digit formats

# --- ADVICE INTENT PATTERNS ---
ADVICE_KEYWORDS = [
    r"should i",
    r"buy",
    r"which is better",
    r"which is best",
    r"best for",
    r"10 years",
    r"20 years",
    r"long term",
    r"planning",
    r"retirement",
    r"horizon",
    r"good fund",
    r"is it good",
    r"suggestion",
    r"recommend",
    r"suggest",
    r"compare"
]
ADVICE_PATTERN = re.compile("|".join(ADVICE_KEYWORDS), re.IGNORECASE)

# --- MANDATORY FOOTER ---
RECENCY_STAMP = " | Last updated: March 2026."
REFUSAL_SOURCE = "\nSource: AMFI Investor Education"

def check_pii(text: str) -> str | None:
    """Detect PII (PAN or Aadhaar) and return refusal with citation."""
    if PAN_PATTERN.search(text) or AADHAAR_PATTERN.search(text):
        return (
            "For your security, I have redacted personal identifiers. Please only ask general factual questions."
            + REFUSAL_SOURCE 
            + RECENCY_STAMP
        )
    return None

def check_advice_intent(text: str) -> str | None:
    """Detect advice-seeking phrases and return refusal with citation."""
    if ADVICE_PATTERN.search(text):
        return (
            "I can provide the factual data for these funds, but I cannot offer investment advice or recommend a specific choice. Please consult a financial advisor for personalized planning."
            + REFUSAL_SOURCE 
            + RECENCY_STAMP
        )
    return None

def apply_guardrails(user_input: str) -> str | None:
    """
    Master check function for all inputs.
    Returns the required refusal string if blocked, otherwise None.
    """
    pii_block = check_pii(user_input)
    if pii_block:
        return pii_block
    
    advice_block = check_advice_intent(user_input)
    if advice_block:
        return advice_block
    
    return None
