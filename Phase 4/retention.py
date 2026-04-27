"""
Phase 4 — Persistence & Contextual Retention Module
====================================================
Handles:
  1. Cross-Session Continuity – remembers past topics per user
  2. Insight Archiving – "Personal Insight Vault" for high-value facts
  3. Retention Loop – generates forward-looking data hooks

Storage: local JSON file (user_profile.json) beside this script.
Zero impact on existing RAG/guardrail layers.
"""

import json
import os
import re
from datetime import datetime, timedelta

# ---------- File paths ----------
_DIR = os.path.dirname(os.path.abspath(__file__))
PROFILE_PATH = os.path.join(_DIR, "user_profile.json")


# ================================================================
# 1. Profile / Context Store
# ================================================================

def _load_profile() -> dict:
    """Load the user profile from disk, or return a blank scaffold."""
    if os.path.exists(PROFILE_PATH):
        try:
            with open(PROFILE_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return {
        "topics": [],          # list of {"topic": str, "timestamp": str, "query": str}
        "vault": [],           # list of {"insight": str, "query": str, "timestamp": str}
        "interest_sectors": [] # e.g. ["Equity", "ELSS", "Mid-Cap"]
    }


def _save_profile(profile: dict):
    """Persist the profile to disk."""
    with open(PROFILE_PATH, "w", encoding="utf-8") as f:
        json.dump(profile, f, indent=2, ensure_ascii=False)


# ================================================================
# 2. Cross-Session Continuity
# ================================================================

_TOPIC_KEYWORDS = {
    "exit load":    "Exit Load",
    "expense":      "Expense Ratio",
    "sip":          "SIP / Investment Limits",
    "lock-in":      "Lock-in Period",
    "lock in":      "Lock-in Period",
    "elss":         "ELSS / Tax Saver",
    "tax":          "ELSS / Tax Saver",
    "nav":          "NAV",
    "riskometer":   "Risk Assessment",
    "risk":         "Risk Assessment",
    "benchmark":    "Benchmark",
    "aum":          "AUM",
    "manager":      "Fund Manager",
    "objective":    "Investment Objective",
    "statement":    "Account Statement",
    "download":     "Account Statement",
    "mid-cap":      "Mid-Cap Funds",
    "flexi":        "Flexi Cap Funds",
    "top 100":      "Large Cap (Top 100)",
    "large cap":    "Large Cap (Top 100)",
    "retirement":   "Retirement Planning",
}


def _detect_topics(query: str) -> list[str]:
    """Return a list of topic labels found in the query."""
    q = query.lower()
    found = []
    for kw, label in _TOPIC_KEYWORDS.items():
        if kw in q and label not in found:
            found.append(label)
    return found


def record_query(query: str):
    """Record a user query into the profile (topics + raw query)."""
    profile = _load_profile()
    topics = _detect_topics(query)
    ts = datetime.now().isoformat()

    for t in topics:
        profile["topics"].append({
            "topic": t,
            "timestamp": ts,
            "query": query
        })

    # Update interest sectors (simple dedup, keep last 20)
    for t in topics:
        if t not in profile["interest_sectors"]:
            profile["interest_sectors"].append(t)
    profile["interest_sectors"] = profile["interest_sectors"][-20:]

    # Keep last 100 topic entries
    profile["topics"] = profile["topics"][-100:]
    _save_profile(profile)


def get_context_bridge(query: str) -> str | None:
    """
    If the current query overlaps with a previous topic, return a
    bridging sentence.  Returns None if no overlap is found.
    """
    profile = _load_profile()
    if not profile["topics"]:
        return None

    current_topics = _detect_topics(query)
    if not current_topics:
        return None

    # Find the most recent matching past topic
    past_lookup = {}  # topic -> most recent entry
    for entry in profile["topics"]:
        past_lookup[entry["topic"]] = entry  # last write wins (chronological)

    for ct in current_topics:
        if ct in past_lookup:
            past_entry = past_lookup[ct]
            # Don't bridge if the past entry is from the same minute (same turn)
            try:
                past_dt = datetime.fromisoformat(past_entry["timestamp"])
                if (datetime.now() - past_dt).total_seconds() < 60:
                    continue
            except (ValueError, TypeError):
                pass
            return f"Building on our previous discussion about **{ct}** — "

    return None


# ================================================================
# 3. Insight Archiving ("Personal Insight Vault")
# ================================================================

def save_insight(query: str, answer: str):
    """Archive a Q-A pair into the user's Personal Insight Vault."""
    profile = _load_profile()
    profile["vault"].append({
        "query": query,
        "insight": answer[:500],  # cap length
        "timestamp": datetime.now().isoformat()
    })
    # Keep vault at max 50 entries
    profile["vault"] = profile["vault"][-50:]
    _save_profile(profile)


def remove_insight(index: int):
    """Remove an insight from the vault by its absolute index."""
    profile = _load_profile()
    vault = profile.get("vault", [])
    if 0 <= index < len(vault):
        vault.pop(index)
        profile["vault"] = vault
        _save_profile(profile)


def get_vault() -> list[dict]:
    """Return the full insight vault."""
    return _load_profile().get("vault", [])


def get_vault_count() -> int:
    """Return the number of saved insights."""
    return len(get_vault())


def is_high_value_response(answer: str) -> bool:
    """
    Heuristic: a response is "high-value" if it contains structured
    data points like percentages, rupee amounts, specific dates, or
    multi-step procedures.
    """
    indicators = [
        r"₹[\d,]+",            # rupee amounts
        r"\d+\.?\d*\s*%",      # percentages
        r"Step \d+",           # procedural steps
        r"\d+ year",           # duration mentions
        r"crore",              # AUM figures
        r"lock-in",            # regulatory facts
    ]
    score = sum(1 for pat in indicators if re.search(pat, answer, re.IGNORECASE))
    return score >= 2


# ================================================================
# 4. Retention Loop — Forward-Looking Data Hooks
# ================================================================

_FUND_EVENT_CALENDAR = {
    "Exit Load":            "the next NAV update cycle",
    "Expense Ratio":        "the upcoming monthly factsheet release",
    "SIP / Investment Limits": "the next SEBI circular update",
    "Lock-in Period":       "the regulatory review date",
    "ELSS / Tax Saver":     "the upcoming tax-filing season (July 2026)",
    "NAV":                  "tomorrow's NAV declaration",
    "Risk Assessment":      "the next quarterly riskometer review",
    "Benchmark":            "the next benchmark rebalance date",
    "AUM":                  "the next monthly AUM disclosure",
    "Fund Manager":         "the next annual report release",
    "Investment Objective":  "the next Scheme Information Document update",
    "Account Statement":    "the next CAS generation cycle",
    "Mid-Cap Funds":        "the next quarterly factsheet (June 2026)",
    "Flexi Cap Funds":      "the next quarterly factsheet (June 2026)",
    "Large Cap (Top 100)":  "the next quarterly factsheet (June 2026)",
    "Retirement Planning":  "the next SEBI investor awareness update",
}


def get_retention_hook(query: str) -> str | None:
    """
    Generate a forward-looking "reason to return" sentence based on
    the topics detected in the query.
    """
    topics = _detect_topics(query)
    if not topics:
        return None

    # Pick the most specific topic (last matched = most specific)
    primary_topic = topics[-1]
    event = _FUND_EVENT_CALENDAR.get(primary_topic)
    if not event:
        return None

    return (
        f"📅 **Data Hook:** Since we've logged your interest in *{primary_topic}*, "
        f"check back around **{event}** — I'll have updated metrics ready for you."
    )


def get_past_interests_summary() -> str | None:
    """
    Return a short summary of the user's past interest areas
    for the sidebar / profile card.
    """
    profile = _load_profile()
    sectors = profile.get("interest_sectors", [])
    if not sectors:
        return None
    return ", ".join(sectors[-6:])
