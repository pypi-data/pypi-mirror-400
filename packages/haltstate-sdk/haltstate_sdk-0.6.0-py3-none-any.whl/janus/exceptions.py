class JanusError(Exception):
    """Base exception for Janus SDK."""


class JanusConnectionError(JanusError):
    """Raised when unable to connect to Janus API."""


class JanusAuthError(JanusError):
    """Raised when authentication fails."""


class JanusRateLimitError(JanusError):
    """Raised when rate limit is exceeded."""


class JanusApprovalTimeoutError(JanusError):
    """Raised when wait_for_approval() times out."""


class ApprovalPending(JanusError):
    """Raised by guard() when action requires human approval.

    This is not an error - it's a control flow signal. The calling script
    should exit gracefully and rely on retry logic (cron, scheduler) to
    resume when approval is granted.

    Attributes:
        approval_id: The unique ID for this approval request
        idempotency_key: The key used to track this request across retries
        action: The action that requires approval
    """
    def __init__(self, message: str, approval_id: str, idempotency_key: str, action: str):
        super().__init__(message)
        self.approval_id = approval_id
        self.idempotency_key = idempotency_key
        self.action = action


class ActionDenied(JanusError):
    """Raised by guard() when action is denied by policy.

    Attributes:
        reason: Why the action was denied
        policy_id: The policy that denied the action (if applicable)
    """
    def __init__(self, message: str, reason: str, policy_id: str = None):
        super().__init__(message)
        self.reason = reason
        self.policy_id = policy_id


class ActionExpired(JanusError):
    """Raised by guard() when a previous approval has expired.

    The action was previously pending but expired before being approved.
    A new approval request should be created.
    """
    def __init__(self, message: str, idempotency_key: str):
        super().__init__(message)
        self.idempotency_key = idempotency_key


class KillSwitchTriggered(JanusError):
    """Raised when the remote kill switch is activated.

    The agent should immediately cease all operations and exit.
    """
    pass
