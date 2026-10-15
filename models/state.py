"""Shared graph state + structured agent outputs.

LangGraph keeps one PRReviewState object and passes it node to node.
That shared state is how agents talk to each other (A2A).

Pydantic models below are the "contracts" each agent must fill in.
If a field is missing or the wrong type, Pydantic fails fast — helpful when debugging.
"""

from datetime import datetime
from typing import Literal, Optional, TypedDict

from pydantic import BaseModel, Field


class ChangedFile(BaseModel):
    path: str
    language: str
    diff: str


class PullRequest(BaseModel):
    id: str
    title: str
    author: str
    files: list[ChangedFile]
    dependencies: list[str] = Field(default_factory=list)


class CodeReviewReport(BaseModel):
    summary: str
    issues: list[str]


class SecurityReport(BaseModel):
    risk: Literal["low", "medium", "high"]
    findings: list[str]
    has_hardcoded_secret: bool = False
    has_critical_vulnerability: bool = False


class PolicyDecision(BaseModel):
    """Output of deterministic Python — not an LLM."""

    allowed: bool
    blocked_reasons: list[str]


class DeploymentRecommendation(BaseModel):
    status: Literal["ready", "ready_with_changes", "blocked"]
    required_actions: list[str]


class ApprovalDecision(BaseModel):
    required: bool
    decision: Literal["auto_approved", "approved", "rejected", "pending"]
    reason: str


class AuditEvent(BaseModel):
    timestamp: datetime
    agent: str
    action: str
    result: str


class PRReviewState(TypedDict):
    """LangGraph state. Every node reads this and returns a partial update.

    Tip while debugging: print(state.keys()) inside any node to see
    which agents have already written their results.
    """

    pr: dict
    code_review: Optional[dict]
    security_report: Optional[dict]
    policy_decision: Optional[dict]
    deployment_recommendation: Optional[dict]
    approval: Optional[dict]
    human_decision: str  # "approve" | "reject" | "auto"  (set in main.py)
    audit_log: list[dict]
