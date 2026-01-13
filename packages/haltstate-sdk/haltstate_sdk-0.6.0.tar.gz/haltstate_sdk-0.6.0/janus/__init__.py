from .client import JanusClient, Permit
from .async_client import AsyncJanusClient
from .models import CheckResult, Decision, ApprovalDecision, ApprovalStatus
from .decorators import janus_guard, openai_guard
from .exceptions import (
    JanusError,
    JanusConnectionError,
    JanusAuthError,
    JanusRateLimitError,
    JanusApprovalTimeoutError,
    ApprovalPending,
    ActionDenied,
    ActionExpired,
    KillSwitchTriggered,
)

__all__ = [
    # Clients
    "JanusClient",
    "AsyncJanusClient",
    # Models
    "CheckResult",
    "Decision",
    "ApprovalDecision",
    "ApprovalStatus",
    "Permit",
    # Decorators
    "janus_guard",
    "openai_guard",
    # Exceptions
    "JanusError",
    "JanusConnectionError",
    "JanusAuthError",
    "JanusRateLimitError",
    "JanusApprovalTimeoutError",
    # Guard pattern exceptions (control flow)
    "ApprovalPending",
    "ActionDenied",
    "ActionExpired",
    "KillSwitchTriggered",
]

__version__ = "0.5.0"  # Idempotent Guard pattern for autonomous agents
