"""Agent 2 — Security.

A2A handoff: this node reads state['code_review'] that Agent 1 wrote.
It also scans the PR diffs with deterministic tools (regex + version list).
"""

import re

from models.audit import append_audit
from models.debug import banner, show
from models.state import PRReviewState, PullRequest, SecurityReport

SECRET_PATTERNS = [
    re.compile(r"sk_live_[A-Za-z0-9]+"),
    re.compile(r"api[_-]?key\s*=\s*['\"][^'\"]+['\"]", re.I),
    re.compile(r"password\s*=\s*['\"][^'\"]+['\"]", re.I),
]

OUTDATED_PACKAGES = {"requests==2.25.1", "flask==2.0.1"}
CRITICAL_CVES = {"log4j==2.14.1"}


def scan_secrets(pr: PullRequest) -> list[str]:
    """Tool: regex scan of diffs. Deterministic — same input, same hits."""
    print("  [tool] scan_secrets()")
    hits: list[str] = []
    for file in pr.files:
        for pattern in SECRET_PATTERNS:
            if pattern.search(file.diff):
                hits.append(f"hardcoded secret in {file.path}")
                break
    return hits


def check_dependencies(pr: PullRequest) -> tuple[list[str], bool]:
    """Tool: compare lock-style pins against a tiny denylist."""
    print("  [tool] check_dependencies()")
    findings: list[str] = []
    critical = False
    for dep in pr.dependencies:
        if dep in CRITICAL_CVES:
            findings.append(f"critical vulnerability: {dep}")
            critical = True
        elif dep in OUTDATED_PACKAGES:
            findings.append(f"outdated package: {dep}")
    return findings, critical


def security_agent(state: PRReviewState) -> dict:
    banner("NODE: Security Agent")

    show("Received from Code Review Agent", state.get("code_review"))
    pr = PullRequest.model_validate(state["pr"])

    secret_hits = scan_secrets(pr)
    dep_findings, critical = check_dependencies(pr)
    findings = secret_hits + dep_findings

    if secret_hits or critical:
        risk = "high"
    elif findings:
        risk = "medium"
    else:
        risk = "low"

    report = SecurityReport(
        risk=risk,
        findings=findings,
        has_hardcoded_secret=bool(secret_hits),
        has_critical_vulnerability=critical,
    )
    show("OUTPUT  (written to state['security_report'])", report)

    return {
        "security_report": report.model_dump(),
        "audit_log": append_audit(
            state,
            agent="security_agent",
            action="scanned_pr",
            result=f"risk={risk}; findings={findings}",
        ),
    }
