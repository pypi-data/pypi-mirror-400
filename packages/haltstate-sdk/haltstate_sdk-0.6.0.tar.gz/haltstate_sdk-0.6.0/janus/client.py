import uuid
import json
import time
import threading
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List, Callable

import httpx

from contextlib import contextmanager
from dataclasses import dataclass

from .models import CheckResult, Decision, ApprovalDecision, ApprovalStatus
from .exceptions import (
    JanusError, JanusConnectionError, JanusAuthError, JanusRateLimitError,
    JanusApprovalTimeoutError, ApprovalPending, ActionDenied, ActionExpired,
    KillSwitchTriggered,
)

_log = logging.getLogger("janus.client")


@dataclass
class Permit:
    """Proof of approval for audit logging.

    This object is yielded by guard() when an action is approved.
    It contains the approval metadata for audit trails.
    """
    approval_id: str
    action: str
    idempotency_key: str
    approved_at: str
    approver: Optional[str]

    def to_audit_dict(self) -> Dict[str, Any]:
        """Return a dictionary suitable for audit logging."""
        return {
            "approval_id": self.approval_id,
            "action": self.action,
            "idempotency_key": self.idempotency_key,
            "approved_at": self.approved_at,
            "approver": self.approver,
        }


class JanusClient:
    """Synchronous Janus SDK client with automatic approval callback support."""

    DEFAULT_BASE_URL = "https://krystalunity.com"
    DEFAULT_TIMEOUT = 5.0

    def __init__(
        self,
        tenant_id: str,
        api_key: str,
        base_url: Optional[str] = None,
        timeout: Optional[float] = None,
        fail_open: bool = False,
        retry_count: int = 2,
        enable_kill_switch: bool = False,
        kill_switch_interval: float = 30.0,
        agent_id: str = "default",
    ):
        """
        Initialize the Janus client.

        Args:
            tenant_id: Your Janus tenant ID
            api_key: Your Janus API key
            base_url: Override the default API base URL
            timeout: Request timeout in seconds
            fail_open: If True, allow actions when Janus is unreachable
            retry_count: Number of retries for failed requests
            enable_kill_switch: Enable background heartbeat for remote termination
            kill_switch_interval: Heartbeat polling interval in seconds (default 30s)
            agent_id: Identifier for this agent instance
        """
        self.tenant_id = tenant_id
        self.api_key = api_key
        self.base_url = (base_url or self.DEFAULT_BASE_URL).rstrip("/")
        self.timeout = timeout or self.DEFAULT_TIMEOUT
        self.fail_open = fail_open
        self.retry_count = retry_count
        self.agent_id = agent_id

        self._client = httpx.Client(
            timeout=self.timeout,
            headers={
                "Content-Type": "application/json",
                "X-Tenant-Id": self.tenant_id,
                "X-API-Key": self.api_key,
                "X-Admin-Token": self.api_key,  # Also send as admin token for approval endpoints
            },
        )

        # Approval callback infrastructure
        self._approval_callback: Optional[Callable[[ApprovalDecision], None]] = None
        self._pending_approvals: Dict[str, Dict[str, Any]] = {}  # request_id -> metadata
        self._listener_thread: Optional[threading.Thread] = None
        self._listener_stop_event = threading.Event()

        # Kill switch infrastructure
        self._kill_switch_enabled = enable_kill_switch
        self._kill_switch_interval = kill_switch_interval
        self._heartbeat_thread: Optional[threading.Thread] = None
        self._heartbeat_stop_event = threading.Event()

        self._listener_started = threading.Event()
        self._last_seen: Optional[str] = None

        # Start heartbeat if enabled
        if enable_kill_switch:
            self._start_heartbeat()

    def check(self, action: str, params: Dict[str, Any], agent_id: str = "default") -> CheckResult:
        request_id = str(uuid.uuid4())

        for attempt in range(self.retry_count + 1):
            try:
                response = self._client.post(
                    f"{self.base_url}/api/sentinel/action/check",
                    json={"agent_id": agent_id, "action": action, "params": params},
                )

                if response.status_code == 401:
                    raise JanusAuthError("Invalid API key")
                if response.status_code == 429:
                    if attempt < self.retry_count:
                        continue
                    raise JanusRateLimitError("Rate limit exceeded")
                if response.status_code >= 400:
                    raise JanusError(f"API error: {response.text}")

                data = response.json()
                decision = Decision(data["decision"])
                approval_id = data.get("approval_id") or data.get("request_id")

                result = CheckResult(
                    decision=decision,
                    reason=data.get("reason", ""),
                    policy_id=data.get("policy_id"),
                    latency_ms=data.get("latency_ms", 0),
                    request_id=request_id,
                    approval_id=approval_id if decision == Decision.APPROVAL_REQUIRED else None,
                )

                # Track pending approvals for callback matching
                if result.requires_approval and result.approval_id:
                    self._pending_approvals[result.approval_id] = {
                        "action": action,
                        "agent_id": agent_id,
                        "params": params,
                        "created_at": datetime.now(timezone.utc).isoformat(),
                    }

                return result

            except httpx.RequestError as exc:
                if attempt < self.retry_count:
                    continue
                if self.fail_open:
                    return CheckResult(
                        decision=Decision.ALLOW,
                        reason="Fail-open: connection error",
                        policy_id=None,
                        latency_ms=0,
                        request_id=request_id,
                    )
                raise JanusConnectionError(f"Connection failed: {exc}")

        # Should not reach here
        raise JanusError("Unknown error")

    # =========================================================================
    # Idempotent Guard Pattern (for autonomous agents / cron jobs)
    # =========================================================================

    @contextmanager
    def guard(
        self,
        action: str,
        params: Optional[Dict[str, Any]] = None,
        idempotency_key: Optional[str] = None,
        agent_id: str = "default",
    ):
        """
        Context manager for idempotent, process-safe action gating.

        This is the recommended pattern for autonomous agents and cron jobs.
        The guard handles the full lifecycle:
        - ALLOWED: Enters the block, yields a Permit for audit
        - DENIED: Raises ActionDenied
        - PENDING: Raises ApprovalPending (script should exit, retry later)
        - EXPIRED: Raises ActionExpired (previous approval expired)

        The idempotency_key ensures the same logical action is tracked across
        process restarts. Use a deterministic key based on your action context
        (e.g., f"daily-backup-{date.today()}").

        Args:
            action: The action name to check against policy
            params: Action parameters for policy evaluation
            idempotency_key: Unique key for this action instance. If not provided,
                             a new UUID is generated (not recommended for cron jobs).
            agent_id: Identifier for the agent making the request

        Yields:
            Permit: Proof of approval with audit metadata

        Raises:
            ApprovalPending: Action requires human approval. Exit and retry later.
            ActionDenied: Action was denied by policy.
            ActionExpired: Previous approval expired before execution.

        Example:
            from janus import JanusClient, ApprovalPending, ActionDenied
            from datetime import date

            client = JanusClient(tenant_id="...", api_key="...")

            def nightly_maintenance():
                # Deterministic key ensures same request across retries
                op_key = f"prune-logs-{date.today()}"

                try:
                    with client.guard("prune_logs", {"days": 30}, idempotency_key=op_key) as permit:
                        # Only executes when APPROVED
                        prune_logs(days=30)
                        print(f"Action approved by {permit.approver}")

                except ApprovalPending as e:
                    print(f"Awaiting approval for {e.idempotency_key}. Will retry.")
                    exit(0)  # Cron will retry later

                except ActionDenied as e:
                    print(f"Denied: {e.reason}")
                    exit(1)
        """
        params = params or {}
        key = idempotency_key or str(uuid.uuid4())

        # Check with idempotency key
        for attempt in range(self.retry_count + 1):
            try:
                response = self._client.post(
                    f"{self.base_url}/api/sentinel/action/guard",
                    json={
                        "agent_id": agent_id,
                        "action": action,
                        "params": params,
                        "idempotency_key": key,
                    },
                )

                if response.status_code == 401:
                    raise JanusAuthError("Invalid API key")
                if response.status_code == 429:
                    if attempt < self.retry_count:
                        time.sleep(1)
                        continue
                    raise JanusRateLimitError("Rate limit exceeded")
                if response.status_code >= 400:
                    raise JanusError(f"API error: {response.text}")

                data = response.json()
                status = data.get("status")
                approval_id = data.get("approval_id", key)

                if status == "allowed" or status == "approved":
                    # Action is approved - yield permit and execute
                    permit = Permit(
                        approval_id=approval_id,
                        action=action,
                        idempotency_key=key,
                        approved_at=data.get("approved_at", datetime.now(timezone.utc).isoformat()),
                        approver=data.get("approver"),
                    )
                    try:
                        yield permit
                        # Report success after block completes
                        self._report_guard_outcome(key, "success", action, agent_id)
                    except Exception as e:
                        # Report failure if block throws
                        self._report_guard_outcome(key, "error", action, agent_id, str(e))
                        raise
                    return

                elif status == "denied":
                    raise ActionDenied(
                        f"Action '{action}' denied: {data.get('reason', 'Policy violation')}",
                        reason=data.get("reason", "Policy violation"),
                        policy_id=data.get("policy_id"),
                    )

                elif status == "pending":
                    raise ApprovalPending(
                        f"Action '{action}' requires approval. Approval ID: {approval_id}",
                        approval_id=approval_id,
                        idempotency_key=key,
                        action=action,
                    )

                elif status == "expired":
                    raise ActionExpired(
                        f"Previous approval for '{action}' expired. Key: {key}",
                        idempotency_key=key,
                    )

                else:
                    raise JanusError(f"Unknown guard status: {status}")

            except httpx.RequestError as exc:
                if attempt < self.retry_count:
                    time.sleep(1)
                    continue
                raise JanusConnectionError(f"Connection failed: {exc}")

        raise JanusError("Guard check failed after retries")

    def _report_guard_outcome(
        self,
        idempotency_key: str,
        outcome: str,
        action: str,
        agent_id: str,
        error: str = None,
    ) -> None:
        """Report the outcome of a guarded action (internal)."""
        try:
            self._client.post(
                f"{self.base_url}/api/sentinel/action/guard/report",
                json={
                    "idempotency_key": idempotency_key,
                    "action": action,
                    "agent_id": agent_id,
                    "outcome": outcome,
                    "error": error,
                },
            )
        except Exception:
            # Best-effort reporting
            pass

    # =========================================================================
    # Blocking Approval Wait (for cron jobs / one-shot scripts)
    # =========================================================================

    def wait_for_approval(
        self,
        approval_id: str,
        timeout: float = 3600,
        poll_interval: float = 5.0,
        max_poll_interval: float = 30.0,
    ) -> ApprovalDecision:
        """
        Block until an approval decision is made (for cron jobs / one-shot scripts).

        This is the synchronous polling alternative to on_approval() callbacks.
        Use this when your script needs to wait for approval before proceeding.

        Args:
            approval_id: The approval_id from CheckResult.approval_id
            timeout: Maximum time to wait in seconds (default 1 hour)
            poll_interval: Initial polling interval in seconds (default 5s)
            max_poll_interval: Maximum polling interval after backoff (default 30s)

        Returns:
            ApprovalDecision with the final status (approved/rejected)

        Raises:
            JanusApprovalTimeoutError: If timeout is reached before decision
            JanusAuthError: If authentication fails
            JanusError: For other API errors

        Example:
            result = client.check("prune_logs", {"days": 30})
            if result.requires_approval:
                print(f"Waiting for approval of {result.approval_id}...")
                decision = client.wait_for_approval(result.approval_id, timeout=3600)
                if decision.approved:
                    prune_logs(days=30)
                else:
                    print(f"Rejected: {decision.reason}")
        """
        start_time = time.time()
        current_interval = poll_interval
        backoff_factor = 1.5

        while True:
            elapsed = time.time() - start_time
            if elapsed >= timeout:
                raise JanusApprovalTimeoutError(
                    f"Approval {approval_id} not decided within {timeout}s timeout"
                )

            try:
                response = self._client.get(
                    f"{self.base_url}/api/sentinel/approval/{approval_id}",
                )

                if response.status_code == 401:
                    raise JanusAuthError("Invalid API key")
                if response.status_code == 404:
                    raise JanusError(f"Approval {approval_id} not found")
                if response.status_code >= 400:
                    raise JanusError(f"API error: {response.text}")

                data = response.json()
                status = data.get("status")

                if status in ("approved", "rejected", "expired"):
                    return ApprovalDecision(
                        request_id=approval_id,
                        status=ApprovalStatus(status),
                        approver=data.get("approver"),
                        reason=data.get("reason"),
                        agent_id=data.get("agent_id"),
                        action=data.get("action"),
                        timestamp=data.get("decided_at"),
                        is_catchup=False,
                    )

                # Still pending - wait and retry with backoff
                _log.debug(f"Approval {approval_id} still pending, waiting {current_interval}s...")
                time.sleep(current_interval)
                current_interval = min(current_interval * backoff_factor, max_poll_interval)

            except httpx.RequestError as exc:
                _log.warning(f"Connection error while polling: {exc}, retrying...")
                time.sleep(current_interval)
                current_interval = min(current_interval * backoff_factor, max_poll_interval)

    def report(
        self,
        check_result: CheckResult,
        status: str,
        result: Optional[Dict[str, Any]] = None,
        agent_id: str = "default",
        action: Optional[str] = None,
    ) -> None:
        payload = {
            "request_id": check_result.request_id,
            "agent_id": agent_id,
            "action": action or "",
            "status": status,
            "decision": check_result.decision.value,
            "policy_id": check_result.policy_id,
            "result": result,
        }
        try:
            self._client.post(f"{self.base_url}/api/sentinel/action/report", json=payload)
        except Exception:
            # Best-effort; swallow errors
            return

    def close(self) -> None:
        """Close the client and stop any background listeners."""
        self._stop_heartbeat()
        self._stop_approval_listener()
        self._client.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    # =========================================================================
    # Kill Switch - Background Heartbeat for Remote Termination
    # =========================================================================

    def _start_heartbeat(self) -> None:
        """Start the background heartbeat thread for kill switch monitoring."""
        if self._heartbeat_thread and self._heartbeat_thread.is_alive():
            return

        self._heartbeat_stop_event.clear()
        self._heartbeat_thread = threading.Thread(
            target=self._run_heartbeat,
            daemon=True,
            name="janus-kill-switch-heartbeat",
        )
        self._heartbeat_thread.start()
        _log.debug("Kill switch heartbeat started (interval: %ss)", self._kill_switch_interval)

    def _stop_heartbeat(self) -> None:
        """Stop the background heartbeat thread."""
        if self._heartbeat_thread and self._heartbeat_thread.is_alive():
            self._heartbeat_stop_event.set()
            self._heartbeat_thread.join(timeout=2.0)

    def _run_heartbeat(self) -> None:
        """Background thread that polls for kill switch signals."""
        import _thread

        while not self._heartbeat_stop_event.is_set():
            try:
                response = self._client.get(
                    f"{self.base_url}/api/sentinel/heartbeat",
                    params={"agent_id": self.agent_id},
                )

                if response.status_code == 200:
                    data = response.json()
                    status = data.get("status")

                    if status == "KILL":
                        _log.warning("Kill switch triggered! Terminating agent...")
                        # Interrupt the main thread
                        _thread.interrupt_main()
                        return

                    elif status == "PAUSE":
                        _log.info("Agent pause requested, waiting...")
                        # Could implement pause logic here

            except Exception as e:
                _log.debug(f"Heartbeat failed: {e}")
                # Don't crash on heartbeat failures

            # Wait for next heartbeat
            self._heartbeat_stop_event.wait(timeout=self._kill_switch_interval)

    def is_kill_switch_active(self) -> bool:
        """Check if the kill switch heartbeat is running."""
        return self._heartbeat_thread is not None and self._heartbeat_thread.is_alive()

    # =========================================================================
    # Approval Callback System - Automatic SSE Listener
    # =========================================================================

    def on_approval(
        self,
        callback: Callable[[ApprovalDecision], None],
        catch_up_hours: int = 24,
    ) -> None:
        """
        Register a callback for approval decisions and start background listener.

        Once registered, the SDK automatically:
        1. Starts a background SSE listener thread
        2. Catches up on any decisions from the last N hours
        3. Fires your callback for each decision (matched to pending requests)

        Args:
            callback: Function called with ApprovalDecision when a decision arrives.
                      Called for ALL decisions, not just pending ones from this client.
            catch_up_hours: Hours of history to catch up on startup (default 24)

        Example:
            def handle_approval(decision):
                if decision.approved:
                    print(f"Request {decision.request_id} approved!")
                else:
                    print(f"Request {decision.request_id} rejected: {decision.reason}")

            client.on_approval(handle_approval)
            result = client.check("deploy", {"model": "gpt-5"})
            # callback fires automatically when admin decides
        """
        self._approval_callback = callback

        # Calculate catch-up timestamp
        catch_up_since = datetime.now(timezone.utc)
        catch_up_since = catch_up_since.replace(
            hour=catch_up_since.hour - catch_up_hours if catch_up_since.hour >= catch_up_hours else 0
        )
        self._last_seen = catch_up_since.isoformat()

        # Start listener if not already running
        if self._listener_thread is None or not self._listener_thread.is_alive():
            self._listener_stop_event.clear()
            self._listener_started.clear()
            self._listener_thread = threading.Thread(
                target=self._run_approval_listener,
                daemon=True,
                name="janus-approval-listener",
            )
            self._listener_thread.start()
            # Wait for connection (up to 5 seconds)
            self._listener_started.wait(timeout=5.0)

    def _stop_approval_listener(self) -> None:
        """Stop the background approval listener."""
        if self._listener_thread and self._listener_thread.is_alive():
            self._listener_stop_event.set()
            self._listener_thread.join(timeout=2.0)

    def _run_approval_listener(self) -> None:
        """Background thread that listens for approval decisions via SSE."""
        url = f"{self.base_url}/api/sentinel/approvals/stream"
        params = {"tenant_id": self.tenant_id}
        if self._last_seen:
            params["last_seen"] = self._last_seen

        while not self._listener_stop_event.is_set():
            try:
                with httpx.Client(
                    timeout=httpx.Timeout(None, connect=10.0),
                    headers={
                        "Accept": "text/event-stream",
                        "X-Tenant-Id": self.tenant_id,
                        "X-API-Key": self.api_key,
                        "X-Admin-Token": self.api_key,
                    },
                ) as sse_client:
                    with sse_client.stream("GET", url, params=params) as response:
                        if response.status_code == 401:
                            _log.error("Approval listener: Invalid API key")
                            break
                        if response.status_code >= 400:
                            _log.error(f"Approval listener: HTTP {response.status_code}")
                            break

                        for line in response.iter_lines():
                            if self._listener_stop_event.is_set():
                                return

                            if not line:
                                continue

                            if line.startswith(":"):
                                # Heartbeat
                                continue

                            if line.startswith("data: "):
                                try:
                                    data = json.loads(line[6:])
                                except json.JSONDecodeError:
                                    continue

                                event_type = data.get("type")

                                if event_type == "CONNECTED":
                                    self._listener_started.set()
                                    _log.debug("Approval listener connected")
                                    continue

                                if event_type == "ERROR":
                                    _log.error(f"Approval listener error: {data.get('message')}")
                                    continue

                                if event_type == "APPROVAL_DECISION":
                                    decision = ApprovalDecision(
                                        request_id=data["request_id"],
                                        status=ApprovalStatus(data["status"]),
                                        approver=data.get("approver"),
                                        reason=data.get("reason"),
                                        agent_id=data.get("agent_id"),
                                        action=data.get("action"),
                                        timestamp=data.get("timestamp"),
                                        is_catchup=data.get("catchup", False),
                                    )

                                    # Update last_seen for reconnection
                                    if decision.timestamp:
                                        self._last_seen = decision.timestamp

                                    # Remove from pending if tracked
                                    self._pending_approvals.pop(decision.request_id, None)

                                    # Fire callback
                                    if self._approval_callback:
                                        try:
                                            self._approval_callback(decision)
                                        except Exception as e:
                                            _log.error(f"Approval callback error: {e}")

            except Exception as e:
                if not self._listener_stop_event.is_set():
                    _log.warning(f"Approval listener disconnected: {e}, reconnecting...")
                    self._listener_stop_event.wait(timeout=2.0)  # Backoff before retry

    def is_listening(self) -> bool:
        """Check if the approval listener is running."""
        return self._listener_thread is not None and self._listener_thread.is_alive()

    def pending_approval_count(self) -> int:
        """Get the number of pending approval requests tracked by this client."""
        return len(self._pending_approvals)

    # =========================================================================
    # Approval Notifications - Catch-up Query (Sync)
    # =========================================================================

    def get_approvals_since(
        self,
        since: str,
        limit: int = 100,
    ) -> List[ApprovalDecision]:
        """
        Fetch approval decisions since a given timestamp.
        Use this for catch-up or polling-based integrations.

        Note: For real-time SSE subscriptions, use AsyncJanusClient.subscribe_approvals()

        Args:
            since: ISO timestamp (e.g., "2025-01-01T00:00:00Z")
            limit: Maximum number of decisions to return (1-500)

        Returns:
            List of ApprovalDecision objects ordered by decided_at ascending
        """
        try:
            response = self._client.get(
                f"{self.base_url}/api/sentinel/approvals/since",
                params={"tenant_id": self.tenant_id, "since": since, "limit": limit},
            )

            if response.status_code == 401:
                raise JanusAuthError("Invalid API key")
            if response.status_code >= 400:
                raise JanusError(f"API error: {response.text}")

            data = response.json()
            decisions = []
            for d in data.get("decisions", []):
                decisions.append(ApprovalDecision(
                    request_id=d["request_id"],
                    status=ApprovalStatus(d["status"]),
                    approver=d.get("approver"),
                    reason=d.get("reason"),
                    agent_id=d.get("agent_id"),
                    action=d.get("action"),
                    timestamp=d.get("decided_at"),
                    is_catchup=True,
                ))
            return decisions

        except httpx.RequestError as exc:
            raise JanusConnectionError(f"Connection failed: {exc}")
