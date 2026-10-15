"""Mock pull requests. No GitHub API — swap this file later if you want real PRs."""

from models.state import ChangedFile, PullRequest

RISKY_PR = PullRequest(
    id="PR-142",
    title="Add login API for the payments service",
    author="alex.developer",
    dependencies=["requests==2.25.1", "flask==2.0.1"],
    files=[
        ChangedFile(
            path="app/auth.py",
            language="python",
            diff=(
                "def login(user, password):\n"
                "    token = 'sk_live_51H4rdc0d3dT0ken'\n"
                "    if user == 'admin':\n"
                "        return token\n"
            ),
        ),
        ChangedFile(
            path="app/utils.py",
            language="python",
            diff=(
                "def login_helper(user, password):\n"
                "    token = 'sk_live_51H4rdc0d3dT0ken'\n"
                "    return token\n"
            ),
        ),
    ],
)

CLEAN_PR = PullRequest(
    id="PR-143",
    title="Add health check endpoint",
    author="alex.developer",
    dependencies=["requests==2.32.3", "flask==3.0.3"],
    files=[
        ChangedFile(
            path="app/health.py",
            language="python",
            diff=(
                "def health():\n"
                '    """Return liveness for the load balancer."""\n'
                '    return {"status": "ok"}\n'
            ),
        ),
        ChangedFile(
            path="tests/test_health.py",
            language="python",
            diff=(
                "def test_health():\n"
                '    assert health()["status"] == "ok"\n'
            ),
        ),
    ],
)
