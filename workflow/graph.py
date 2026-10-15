"""LangGraph wiring.

Each node is a Python function. Edges are the arrows between them.
State flows left to right; later agents read earlier agents' keys.

    START
      -> code_review
      -> security
      -> guardrail          (deterministic)
      -> deployment
      -> human_approval
      -> END
"""

from langgraph.graph import END, START, StateGraph

from agents.code_review_agent import code_review_agent
from agents.deployment_agent import deployment_agent, human_approval_node
from agents.security_agent import security_agent
from guardrails.policy_engine import guardrail_node
from models.state import PRReviewState


def build_graph():
    graph = StateGraph(PRReviewState)

    graph.add_node("code_review", code_review_agent)
    graph.add_node("security", security_agent)
    graph.add_node("guardrail", guardrail_node)
    graph.add_node("deployment", deployment_agent)
    graph.add_node("human_approval", human_approval_node)

    graph.add_edge(START, "code_review")
    graph.add_edge("code_review", "security")
    graph.add_edge("security", "guardrail")
    graph.add_edge("guardrail", "deployment")
    graph.add_edge("deployment", "human_approval")
    graph.add_edge("human_approval", END)

    return graph.compile()
