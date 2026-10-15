"""Deterministic policy. No LLM. Same inputs always produce the same allow/block.

Rules:
  - critical vulnerability  -> block
  - hardcoded secret        -> block
  - risk low or medium      -> continue (unless a block rule already fired)
"""

from models.audit import append_audit
from models.debug import banner, show
from models.state import PolicyDecision, PRReviewState, SecurityReport


def evaluate_policy(report: SecurityReport) -> PolicyDecision:
    blocked: list[str] = []

    if report.has_critical_vulnerability:
        blocked.append("critical vulnerability")
    if report.has_hardcoded_secret:
        blocked.append("hardcoded secret")

    return PolicyDecision(allowed=not blocked, blocked_reasons=blocked)


def guardrail_node(state: PRReviewState) -> dict:
    banner("NODE: Guardrail (deterministic Python, not an agent)")

    report = SecurityReport.model_validate(state["security_report"])
    show("Input from Security Agent", report)
    decision = evaluate_policy(report)
    show("OUTPUT  (written to state['policy_decision'])", decision)

    return {
        "policy_decision": decision.model_dump(),
        "audit_log": append_audit(
            state,
            agent="policy_engine",
            action="evaluate_policy",
            result=f"allowed={decision.allowed}; reasons={decision.blocked_reasons}",
        ),
    }
