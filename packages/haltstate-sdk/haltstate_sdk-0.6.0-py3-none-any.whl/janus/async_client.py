import uuid
import json
from datetime import datetime
from typing import Dict, Any, Optional, List, AsyncIterator, Callable

import httpx

from .models import CheckResult, Decision, ApprovalDecision, ApprovalStatus
from .exceptions import JanusError, JanusConnectionError, JanusAuthError, JanusRateLimitError, JanusApprovalTimeoutError


class AsyncJanusClient:
    """Asynchronous Janus SDK client."""

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
    ):
        self.tenant_id = tenant_id
        self.api_key = api_key
        self.base_url = (base_url or self.DEFAULT_BASE_URL).rstrip("/")
        self.timeout = timeout or self.DEFAULT_TIMEOUT
        self.fail_open = fail_open
        self.retry_count = retry_count

        self._client = httpx.AsyncClient(
            timeout=self.timeout,
            headers={
                "Content-Type": "application/json",
                "X-Tenant-Id": self.tenant_id,
                "X-API-Key": self.api_key,
                "X-Admin-Token": self.api_key,  # Also send as admin token for approval endpoints
            },
        )

    async def check(self, action: str, params: Dict[str, Any], agent_id: str = "default") -> CheckResult:
        request_id = str(uuid.uuid4())

        for attempt in range(self.retry_count + 1):
            try:
                response = await self._client.post(
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

                return CheckResult(
                    decision=decision,
                    reason=data.get("reason", ""),
                    policy_id=data.get("policy_id"),
                    latency_ms=data.get("latency_ms", 0),
                    request_id=request_id,
                    approval_id=approval_id if decision == Decision.APPROVAL_REQUIRED else None,
                )

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

        raise JanusError("Unknown error")

    async def report(
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
            await self._client.post(f"{self.base_url}/api/sentinel/action/report", json=payload)
        except Exception:
            return

    async def close(self) -> None:
        await self._client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self.close()

    # =========================================================================
    # Approval Notifications - SSE Stream & Catch-up
    # =========================================================================

    async def get_approvals_since(
        self,
        since: str,
        limit: int = 100,
    ) -> List[ApprovalDecision]:
        """
        Fetch approval decisions since a given timestamp.
        Use this for catch-up when reconnecting or for polling-based integrations.

        Args:
            since: ISO timestamp (e.g., "2025-01-01T00:00:00Z")
            limit: Maximum number of decisions to return (1-500)

        Returns:
            List of ApprovalDecision objects ordered by decided_at ascending
        """
        try:
            response = await self._client.get(
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

    async def subscribe_approvals(
        self,
        last_seen: Optional[str] = None,
        on_connected: Optional[Callable[[], None]] = None,
    ) -> AsyncIterator[ApprovalDecision]:
        """
        Subscribe to real-time approval decision notifications via SSE.

        This is an async generator that yields ApprovalDecision objects as they arrive.
        The connection is kept alive with heartbeats from the server.

        Args:
            last_seen: Optional ISO timestamp for catch-up. If provided, any decisions
                       made after this timestamp will be sent first before real-time events.
            on_connected: Optional callback invoked when SSE connection is established.

        Yields:
            ApprovalDecision objects as they arrive

        Example:
            async for decision in client.subscribe_approvals(last_seen="2025-01-01T00:00:00Z"):
                if decision.approved:
                    print(f"Request {decision.request_id} was approved!")
                elif decision.rejected:
                    print(f"Request {decision.request_id} was rejected: {decision.reason}")
        """
        url = f"{self.base_url}/api/sentinel/approvals/stream"
        params = {"tenant_id": self.tenant_id}
        if last_seen:
            params["last_seen"] = last_seen

        # Use a separate client for SSE with longer timeout
        async with httpx.AsyncClient(
            timeout=httpx.Timeout(None, connect=10.0),  # No read timeout for SSE
            headers={
                "Accept": "text/event-stream",
                "X-Tenant-Id": self.tenant_id,
                "X-API-Key": self.api_key,
                "X-Admin-Token": self.api_key,  # Admin token for approval endpoints
            },
        ) as sse_client:
            try:
                async with sse_client.stream("GET", url, params=params) as response:
                    if response.status_code == 401:
                        raise JanusAuthError("Invalid API key")
                    if response.status_code >= 400:
                        raise JanusError(f"SSE connection failed: {response.status_code}")

                    async for line in response.aiter_lines():
                        if not line:
                            continue

                        # SSE format: "data: {...}" or ": heartbeat ..."
                        if line.startswith(":"):
                            # Heartbeat/comment, ignore
                            continue

                        if line.startswith("data: "):
                            try:
                                data = json.loads(line[6:])  # Skip "data: " prefix
                            except json.JSONDecodeError:
                                continue

                            event_type = data.get("type")

                            if event_type == "CONNECTED":
                                if on_connected:
                                    on_connected()
                                continue

                            if event_type == "ERROR":
                                raise JanusError(f"SSE error: {data.get('message')}")

                            if event_type == "APPROVAL_DECISION":
                                yield ApprovalDecision(
                                    request_id=data["request_id"],
                                    status=ApprovalStatus(data["status"]),
                                    approver=data.get("approver"),
                                    reason=data.get("reason"),
                                    agent_id=data.get("agent_id"),
                                    action=data.get("action"),
                                    timestamp=data.get("timestamp"),
                                    is_catchup=data.get("catchup", False),
                                )

            except httpx.RequestError as exc:
                raise JanusConnectionError(f"SSE connection failed: {exc}")

    async def wait_for_approval(
        self,
        approval_id: str,
        timeout: float = 3600,
        poll_interval: float = 5.0,
        max_poll_interval: float = 30.0,
    ) -> ApprovalDecision:
        """
        Wait for a specific approval request to be decided (async version).

        Uses polling with exponential backoff. For long-running async services,
        consider using subscribe_approvals() instead.

        Args:
            approval_id: The approval_id from CheckResult.approval_id
            timeout: Maximum time to wait in seconds (default 1 hour)
            poll_interval: Initial polling interval in seconds (default 5s)
            max_poll_interval: Maximum polling interval after backoff (default 30s)

        Returns:
            ApprovalDecision when the request is decided

        Raises:
            JanusApprovalTimeoutError: If timeout is exceeded
            JanusAuthError: If authentication fails
            JanusError: For other API errors

        Example:
            result = await client.check("prune_logs", {"days": 30})
            if result.requires_approval:
                decision = await client.wait_for_approval(result.approval_id)
                if decision.approved:
                    await prune_logs(days=30)
        """
        import asyncio
        import time

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
                response = await self._client.get(
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
                await asyncio.sleep(current_interval)
                current_interval = min(current_interval * backoff_factor, max_poll_interval)

            except httpx.RequestError:
                await asyncio.sleep(current_interval)
                current_interval = min(current_interval * backoff_factor, max_poll_interval)
