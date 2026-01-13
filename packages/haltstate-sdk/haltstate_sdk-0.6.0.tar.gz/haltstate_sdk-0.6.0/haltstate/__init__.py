# HaltState SDK - re-exports from janus for new branding
# Backward compatible: both `from haltstate import HaltStateClient` and
# `from janus import JanusClient` continue to work.

from janus.client import JanusClient as HaltStateClient, Permit
from janus.async_client import AsyncJanusClient as AsyncHaltStateClient
from janus.models import CheckResult, Decision, ApprovalDecision, ApprovalStatus
from janus.decorators import janus_guard as haltstate_guard, openai_guard
from janus.exceptions import (
    JanusError as HaltStateError,
    JanusConnectionError as HaltStateConnectionError,
    JanusAuthError as HaltStateAuthError,
    JanusRateLimitError as HaltStateRateLimitError,
    JanusApprovalTimeoutError as HaltStateApprovalTimeoutError,
    ApprovalPending,
    ActionDenied,
    ActionExpired,
    KillSwitchTriggered,
)

# Keep Janus names as aliases for full backward compatibility
from janus import (
    JanusClient,
    AsyncJanusClient,
    janus_guard,
    JanusError,
    JanusConnectionError,
    JanusAuthError,
    JanusRateLimitError,
    JanusApprovalTimeoutError,
)

__all__ = [
    # HaltState branded names (new)
    "HaltStateClient",
    "AsyncHaltStateClient",
    "haltstate_guard",
    "HaltStateError",
    "HaltStateConnectionError",
    "HaltStateAuthError",
    "HaltStateRateLimitError",
    "HaltStateApprovalTimeoutError",
    # Janus names (backward compatible)
    "JanusClient",
    "AsyncJanusClient",
    "janus_guard",
    "JanusError",
    "JanusConnectionError",
    "JanusAuthError",
    "JanusRateLimitError",
    "JanusApprovalTimeoutError",
    # Shared models
    "CheckResult",
    "Decision",
    "ApprovalDecision",
    "ApprovalStatus",
    "Permit",
    "openai_guard",
    # Control flow exceptions
    "ApprovalPending",
    "ActionDenied",
    "ActionExpired",
    "KillSwitchTriggered",
]

__version__ = "0.5.0"
