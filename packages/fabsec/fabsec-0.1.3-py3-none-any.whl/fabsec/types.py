# fabsec/types.py
from __future__ import annotations
from typing import Any, Dict, List, Optional, TypedDict, Literal


class CoachResponse(TypedDict, total=False):
    ok: bool
    audit_id: str
    context: Dict[str, Any]
    risk: Dict[str, Any]
    ai_summary: Optional[str]
    is_attack: Optional[bool]
    attack_type: Optional[str]
    attack_families: List[str]
    indicators: List[Any]
    coach: Dict[str, Any]


class CopilotResponse(TypedDict, total=False):
    answer: str
    reasoning: str
    risk_summary: str
    key_findings: List[Any]
    recommended_actions: List[Any]
    context_used: Dict[str, Any]


class LicenseMeResponse(TypedDict, total=False):
    ok: bool
    api_key_status: Optional[str]
    app_id: Optional[str]
    plan: Optional[str]
    features: Dict[str, Any]
