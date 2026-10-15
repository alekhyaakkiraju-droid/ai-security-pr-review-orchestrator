"""Agent 1 — Code Review.

Standalone node. Reads the PR from state, calls simple tools, writes
code_review so the Security Agent can read it next.
"""

from models.audit import append_audit
from models.debug import banner, show
from models.state import CodeReviewReport, PRReviewState, PullRequest


def analyze_changed_files(pr: PullRequest) -> dict:
    """Tool: look at paths + diffs (mocked analysis, no LLM)."""
    print("  [tool] analyze_changed_files()")
    paths = [f.path for f in pr.files]
    has_tests = any("test" in f.path for f in pr.files)
    has_docs = any("README" in f.path or '"""' in f.diff for f in pr.files)
    duplicate_login = sum("def login" in f.diff for f in pr.files) > 1
    return {
        "paths": paths,
        "has_tests": has_tests,
        "has_docs": has_docs,
        "duplicate_login": duplicate_login,
    }


def code_review_agent(state: PRReviewState) -> dict:
    banner("NODE: Code Review Agent")

    pr = PullRequest.model_validate(state["pr"])
    show("Received PR (from graph start)", pr.model_dump())

    analysis = analyze_changed_files(pr)
    show("Tool result", analysis)

    issues: list[str] = []
    if not analysis["has_tests"]:
        issues.append("missing unit tests")
    if analysis["duplicate_login"]:
        issues.append("duplicate logic")
    if not analysis["has_docs"]:
        issues.append("missing documentation")

    report = CodeReviewReport(summary=pr.title, issues=issues)
    show("OUTPUT  (written to state['code_review'])", report)

    return {
        "code_review": report.model_dump(),
        "audit_log": append_audit(
            state,
            agent="code_review_agent",
            action="reviewed_pr",
            result=f"issues={issues}",
        ),
    }
