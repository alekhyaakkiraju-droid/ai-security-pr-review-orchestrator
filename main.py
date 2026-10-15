"""Run the PR review graph with mocked pull request data.

Examples:
  python main.py
  python main.py --scenario clean
  python main.py --approve
  python main.py --reject
"""

import argparse
import json
import sys
from pathlib import Path

# Allow `python main.py` from this folder without installing a package.
sys.path.insert(0, str(Path(__file__).resolve().parent))

from models.debug import banner, show
from models.pr_data import CLEAN_PR, RISKY_PR
from workflow.graph import build_graph


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="AI Security PR Review Orchestrator")
    parser.add_argument(
        "--scenario",
        choices=["risky", "clean"],
        default="risky",
        help="risky = secret + outdated deps (default). clean = auto-approve path.",
    )
    parser.add_argument(
        "--approve",
        action="store_true",
        help="Simulate a human approving a high-risk PR.",
    )
    parser.add_argument(
        "--reject",
        action="store_true",
        help="Simulate a human rejecting a high-risk PR.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    pr = CLEAN_PR if args.scenario == "clean" else RISKY_PR

    if args.reject:
        human_decision = "reject"
    elif args.approve:
        human_decision = "approve"
    else:
        human_decision = "auto"

    banner("START: Developer created a Pull Request")
    show("Mock PR", pr)

    app = build_graph()
    final_state = app.invoke(
        {
            "pr": pr.model_dump(),
            "code_review": None,
            "security_report": None,
            "policy_decision": None,
            "deployment_recommendation": None,
            "approval": None,
            "human_decision": human_decision,
            "audit_log": [],
        }
    )

    banner("END: Final graph state")
    show("code_review", final_state["code_review"])
    show("security_report", final_state["security_report"])
    show("policy_decision", final_state["policy_decision"])
    show("deployment_recommendation", final_state["deployment_recommendation"])
    show("approval", final_state["approval"])
    show("audit_log", final_state["audit_log"])

    print("\nPretty one-liner for copy/paste:")
    print(
        json.dumps(
            {
                "code_review": final_state["code_review"],
                "security": final_state["security_report"],
                "guardrail": final_state["policy_decision"],
                "deployment": final_state["deployment_recommendation"],
                "approval": final_state["approval"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
