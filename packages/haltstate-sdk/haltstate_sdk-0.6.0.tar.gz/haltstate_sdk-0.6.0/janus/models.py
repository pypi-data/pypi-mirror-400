from dataclasses import dataclass
from enum import Enum
from typing import Optional, Dict, Any


class Decision(Enum):
    ALLOW = "ALLOW"
    DENY = "DENY"
    APPROVAL_REQUIRED = "APPROVAL_REQUIRED"


@dataclass
class CheckResult:
    decision: Decision
    reason: str
    policy_id: Optional[str]
    latency_ms: int
    request_id: str
    approval_id: Optional[str] = None  # Set when decision is APPROVAL_REQUIRED

    @property
    def allowed(self) -> bool:
        return self.decision == Decision.ALLOW

    @property
    def denied(self) -> bool:
        return self.decision == Decision.DENY

    @property
    def requires_approval(self) -> bool:
        return self.decision == Decision.APPROVAL_REQUIRED


@dataclass
class CheckRequest:
    agent_id: str
    action: str
    params: Dict[str, Any]


@dataclass
class ReportRequest:
    request_id: str
    agent_id: str
    action: str
    status: str  # success, failure, error
    result: Optional[Dict[str, Any]] = None


class ApprovalStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"  # Server-side expiry: no action within time limit


@dataclass
class ApprovalDecision:
    """Represents an approval decision event from the SSE stream or catch-up query."""
    request_id: str
    status: ApprovalStatus
    approver: Optional[str]
    reason: Optional[str]
    agent_id: Optional[str]
    action: Optional[str]
    timestamp: Optional[str]
    is_catchup: bool = False  # True if this came from catch-up, not real-time

    @property
    def approved(self) -> bool:
        return self.status == ApprovalStatus.APPROVED

    @property
    def rejected(self) -> bool:
        return self.status == ApprovalStatus.REJECTED

    @property
    def expired(self) -> bool:
        """True if approval expired server-side (no action within time limit)."""
        return self.status == ApprovalStatus.EXPIRED
