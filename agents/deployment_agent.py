"""Agent 3 — Deployment Readiness.

Reads code review + security + guardrail outputs, then recommends what to do.
Human approval runs AFTER this node.
"""

from models.audit import append_audit
from models.debug import banner, show
from models.state import (
    ApprovalDecision,
    CodeReviewReport,
    DeploymentRecommendation,
    PolicyDecision,
    PRReviewState,
    SecurityReport,
)


def deployment_agent(state: PRReviewState) -> dict:
    banner("NODE: Deployment Readiness Agent")

    code_review = CodeReviewReport.model_validate(state["code_review"])
    security = SecurityReport.model_validate(state["security_report"])
    policy = PolicyDecision.model_validate(state["policy_decision"])

    show("From Code Review Agent", code_review)
    show("From Security Agent", security)
    show("From Guardrail", policy)

    actions: list[str] = []
    if "missing unit tests" in code_review.issues:
        actions.append("add unit tests")
    if "missing documentation" in code_review.issues:
        actions.append("add documentation")
    if "duplicate logic" in code_review.issues:
        actions.append("remove duplicate logic")
    if security.has_hardcoded_secret:
        actions.append("remove secret")
    if security.has_critical_vulnerability:
        actions.append("upgrade vulnerable dependency")
    if any(f.startswith("outdated package") for f in security.findings):
        actions.append("upgrade outdated packages")

    if not policy.allowed:
        status = "blocked"
    elif actions:
        status = "ready_with_changes"
    else:
        status = "ready"

    recommendation = DeploymentRecommendation(status=status, required_actions=actions)
    show("OUTPUT  (written to state['deployment_recommendation'])", recommendation)

    return {
        "deployment_recommendation": recommendation.model_dump(),
        "audit_log": append_audit(
            state,
            agent="deployment_agent",
            action="recommend_deployment",
            result=f"status={status}; actions={actions}",
        ),
    }


def human_approval_node(state: PRReviewState) -> dict:
    """If Security Agent risk is high, a human must approve. Otherwise auto-approve.

    human_decision is injected from main.py so this demo does not block on input().
    Flip --approve / --reject while debugging.
    """
    banner("NODE: Human Approval")

    security = SecurityReport.model_validate(state["security_report"])
    human_decision = state.get("human_decision") or "auto"
    show("Security risk", {"risk": security.risk})
    print(f"\nhuman_decision from CLI: {human_decision}")

    if security.risk == "high":
        if human_decision == "approve":
            approval = ApprovalDecision(
                required=True,
                decision="approved",
                reason="High risk — human approved the PR",
            )
        elif human_decision == "reject":
            approval = ApprovalDecision(
                required=True,
                decision="rejected",
                reason="High risk — human rejected the PR",
            )
        else:
            approval = ApprovalDecision(
                required=True,
                decision="pending",
                reason="High risk — re-run with --approve or --reject",
            )
    else:
        approval = ApprovalDecision(
            required=False,
            decision="auto_approved",
            reason="Risk is low/medium — auto approved",
        )

    show("OUTPUT  (written to state['approval'])", approval)

    return {
        "approval": approval.model_dump(),
        "audit_log": append_audit(
            state,
            agent="human_approval",
            action="decide",
            result=approval.decision,
        ),
    }
