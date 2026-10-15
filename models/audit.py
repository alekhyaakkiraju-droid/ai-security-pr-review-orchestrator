from datetime import datetime, timezone

from models.state import AuditEvent, PRReviewState


def append_audit(state: PRReviewState, agent: str, action: str, result: str) -> list[dict]:
    """Copy the existing log and add one event. Returned from each node."""
    event = AuditEvent(
        timestamp=datetime.now(timezone.utc),
        agent=agent,
        action=action,
        result=result,
    )
    return list(state.get("audit_log") or []) + [event.model_dump()]
