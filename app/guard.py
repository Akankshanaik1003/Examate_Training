MAX_CHARS = 500
INJECTION_PATTERNS = [
    "ignore previous instructions",
    "ignore all previous",
    "disregard the above",
    "reveal your prompt",
    "system prompt",
    "you are now",
]


def check_input(question):
    """Return (ok, message). Empty input is left to the route, which returns 422."""
    q = (question or "").strip()
    if len(q) > MAX_CHARS:
        return False, f"Question too long (max {MAX_CHARS} characters)."
    low = q.lower()
    if any(p in low for p in INJECTION_PATTERNS):
        return False, "Rejected: looks like a prompt-injection attempt."
    return True, q