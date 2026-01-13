from __future__ import annotations
from datetime import datetime, timezone
from typing import Any, Dict, Optional, List, Union
import uuid
import requests
import os
from urllib.parse import urlencode

from .types import (
    Actor, Action, Evidence, Decision, Policy, Check,
    Agent, CreateAgentInput, UpdateAgentInput
)
from .utils import to_jsonable, normalize_checks


class AccountabilityLayerOptions:
    def __init__(
        self,
        endpoint: Optional[str] = None,
        api_key: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None
    ):
        self.endpoint = endpoint
        self.api_key = api_key
        self.headers = headers or {}


class AgentsAPI:
    """Agent operations namespace"""

    def __init__(self, client: "AccountabilityLayer"):
        self._client = client

    def register(self, input: CreateAgentInput) -> Agent:
        """Register a new agent"""
        return self._client._post("/agents", input)

    def list(self, status: Optional[str] = None, limit: Optional[int] = None) -> List[Agent]:
        """List all agents for the organization"""
        params = {}
        if status:
            params["status"] = status
        if limit:
            params["limit"] = str(limit)
        qs = urlencode(params) if params else ""
        return self._client._get(f"/agents{('?' + qs) if qs else ''}")

    def get(self, agent_id: str) -> Agent:
        """Get a single agent by ID"""
        return self._client._get(f"/agents/{agent_id}")

    def update(self, agent_id: str, input: UpdateAgentInput) -> Agent:
        """Update an agent"""
        return self._client._patch(f"/agents/{agent_id}", input)

    def delete(self, agent_id: str) -> Dict[str, Any]:
        """Delete (disable) an agent"""
        return self._client._delete(f"/agents/{agent_id}")

    def list_actions(self, agent_id: str, status: Optional[str] = None, limit: Optional[int] = None) -> List[Action]:
        """List actions for an agent"""
        params = {}
        if status:
            params["status"] = status
        if limit:
            params["limit"] = str(limit)
        qs = urlencode(params) if params else ""
        return self._client._get(f"/agents/{agent_id}/actions{('?' + qs) if qs else ''}")


class AccountabilityLayer:
    UA = "apaai-python/0.2.0"

    def __init__(self, opts: Optional[AccountabilityLayerOptions] = None):
        if opts is None:
            opts = AccountabilityLayerOptions()
        
        self.base = (opts.endpoint or "http://localhost:8787").rstrip("/")
        self.api_key = opts.api_key
        self.extra_headers = opts.headers
        self.session = requests.Session()
        
        # Set default headers
        self.session.headers.update({
            "Content-Type": "application/json",
            "User-Agent": self.UA,
            **self.extra_headers
        })
        
        if self.api_key:
            self.session.headers["x-api-key"] = self.api_key

    def _request(self, method: str, path: str, json: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Core request helper"""
        url = f"{self.base}{path}"
        
        try:
            response = self.session.request(method, url, json=json, timeout=30)
            response.raise_for_status()
            
            # Handle 204 No Content
            if response.status_code == 204:
                return {}
                
            return response.json()
        except requests.exceptions.RequestException as e:
            if hasattr(e, 'response') and e.response is not None:
                detail = e.response.text if e.response.text else ""
                msg = f"APAAI {method} {path} -> {e.response.status_code} {e.response.reason}"
                if detail.strip():
                    msg += f" :: {detail}"
                raise RuntimeError(msg) from e
            else:
                raise RuntimeError(f"APAAI {method} {path} -> {str(e)}") from e

    def _get(self, path: str) -> Dict[str, Any]:
        return self._request("GET", path)

    def _post(self, path: str, body: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return self._request("POST", path, json=body)

    def _patch(self, path: str, body: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return self._request("PATCH", path, json=body)

    def _delete(self, path: str) -> Dict[str, Any]:
        return self._request("DELETE", path)

    # ---- Agent management API ----

    @property
    def agents(self) -> AgentsAPI:
        """Agent management API"""
        if not hasattr(self, '_agents'):
            self._agents = AgentsAPI(self)
        return self._agents

    # ---- High-level methods (1:1 with protocol) ----

    def createAction(self, action: Action) -> Decision:
        """Propose/create an action; returns a decision + actionId"""
        return self._post("/actions", action)

    def submitEvidence(self, ev: Evidence) -> Dict[str, Any]:
        """Submit evidence (checks) for an action"""
        return self._post("/evidence", ev)

    def getPolicy(self, action_type: Optional[str] = None) -> Policy:
        """Fetch policy; optionally scoped to an actionType"""
        path = "/policy"
        if action_type:
            path = f"{path}?actionType={action_type}"
        return self._get(path)

    def setPolicy(self, policy: Policy) -> Policy:
        """Set/replace policy"""
        return self._post("/policy", policy)

    def getAction(self, action_id: str) -> Action:
        """Read single action"""
        return self._get(f"/actions/{action_id}")

    def listActions(self, filters: Optional[Dict[str, Union[str, int, bool]]] = None) -> List[Action]:
        """List actions with optional filters"""
        params = {}
        if filters:
            for k, v in filters.items():
                if v is not None:
                    params[k] = str(v)
        
        qs = urlencode(params) if params else ""
        path = f"/actions{('?' + qs) if qs else ''}"
        return self._get(path)

    def getEvidence(self, action_id: str) -> Evidence:
        """Read evidence for an action"""
        return self._get(f"/evidence/{action_id}")

    def approveAction(self, action_id: str, approver: Optional[str] = None) -> Dict[str, Any]:
        """Approve an action (human-in-the-loop)"""
        return self._post(f"/approve/{action_id}", {"approver": approver})

    def rejectAction(self, action_id: str, reason: Optional[str] = None) -> Dict[str, Any]:
        """Reject an action (human-in-the-loop)"""
        return self._post(f"/reject/{action_id}", {"reason": reason})

    # ---- Convenience methods ----

    def propose(
        self,
        *,
        type: str,
        actor: Actor,
        target: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
        id: Optional[str] = None,
        timestamp: Optional[str] = None,
        agent_id: Optional[str] = None,
    ) -> Decision:
        """Propose an action (id/timestamp auto-filled if absent)"""
        action_id = id or str(uuid.uuid4())
        action_timestamp = timestamp or datetime.now(tz=timezone.utc).isoformat().replace("+00:00", "Z")

        action: Action = {
            "id": action_id,
            "timestamp": action_timestamp,
            "type": type,
            "actor": to_jsonable(actor),
            "target": target,
            "params": to_jsonable(params) if params else None,
        }
        if agent_id:
            action["agentId"] = agent_id
        return self.createAction(action)

    def evidence(self, action_id: str, checks: List[Check]) -> Dict[str, Any]:
        """Submit evidence for an action"""
        ev: Evidence = {
            "actionId": action_id,
            "checks": normalize_checks(checks),
        }
        return self.submitEvidence(ev)

    def policy(self, action_type: Optional[str] = None) -> Policy:
        """Get policy for an action type"""
        return self.getPolicy(action_type)

    def approve(self, action_id: str, approver: Optional[str] = None) -> Dict[str, Any]:
        """Approve an action"""
        return self.approveAction(action_id, approver)

    def reject(self, action_id: str, reason: Optional[str] = None) -> Dict[str, Any]:
        """Reject an action"""
        return self.rejectAction(action_id, reason)

    # ---- Manager interfaces (for backwards compatibility) ----

    @property
    def policies(self):
        """Policy management interface."""
        return PolicyManager(self)

    @property
    def human(self):
        """Human-in-the-loop interface."""
        return HumanManager(self)

    @property
    def actions(self):
        """Action management interface."""
        return ActionManager(self)


class PolicyManager:
    def __init__(self, client: AccountabilityLayer):
        self.client = client

    def evaluate(self, action_id: str) -> Dict[str, Any]:
        """Evaluate policy for an action."""
        action = self.client.getAction(action_id)
        policy = self.client.policy(action["type"])
        return {"status": action["status"], "checks": action.get("checks", [])}

    def enforce(self, action_type: str) -> Dict[str, Any]:
        """Enforce policy for an action type."""
        return self.client.policy(action_type)

    def set(self, policy: Policy) -> Policy:
        """Set a policy."""
        return self.client.setPolicy(policy)


class HumanManager:
    def __init__(self, client: AccountabilityLayer):
        self.client = client

    def approve(self, action_id: str, approver: Optional[str] = None) -> Dict[str, Any]:
        """Approve an action."""
        return self.client.approve(action_id, approver)

    def reject(self, action_id: str, reason: Optional[str] = None) -> Dict[str, Any]:
        """Reject an action."""
        return self.client.reject(action_id, reason)


class EvidenceManager:
    def __init__(self, client: AccountabilityLayer):
        self.client = client

    def add(self, action_id: str, checks: List[Check]) -> Dict[str, Any]:
        """Add evidence for an action."""
        return self.client.evidence(action_id, checks)

    def get(self, action_id: str) -> Evidence:
        """Get evidence for an action."""
        return self.client.getEvidence(action_id)


class ActionManager:
    def __init__(self, client: AccountabilityLayer):
        self.client = client

    def get(self, action_id: str) -> Action:
        """Get an action by ID."""
        return self.client.getAction(action_id)

    def list(self, filters: Optional[Dict[str, Any]] = None) -> List[Action]:
        """List actions with optional filters."""
        return self.client.listActions(filters)


# ---- Singleton + Convenience API (backwards & ergonomic) ----

_client = AccountabilityLayer(
    AccountabilityLayerOptions(
        endpoint=os.getenv('APAAI_ENDPOINT'),
        api_key=os.getenv('APAAI_KEY')
    )
)


def configure(opts: Optional[AccountabilityLayerOptions] = None):
    """Reconfigure the global client (useful for apps/tests)"""
    global _client
    _client = AccountabilityLayer(opts)


def propose(
    *,
    type: str,
    actor: Actor,
    target: Optional[str] = None,
    params: Optional[Dict[str, Any]] = None,
    id: Optional[str] = None,
    timestamp: Optional[str] = None,
    agent_id: Optional[str] = None,
) -> Decision:
    """Propose an action (id/timestamp auto-filled if absent)"""
    return _client.propose(
        type=type,
        actor=actor,
        target=target,
        params=params,
        id=id,
        timestamp=timestamp,
        agent_id=agent_id,
    )


def evidence(action_id: str, checks: List[Check]) -> Dict[str, Any]:
    """Submit evidence for an action"""
    return _client.evidence(action_id, checks)


def policy(action_type: Optional[str] = None) -> Policy:
    """Get policy for an action type"""
    return _client.policy(action_type)


def approve(action_id: str, approver: Optional[str] = None) -> Dict[str, Any]:
    """Approve an action"""
    return _client.approve(action_id, approver)


def reject(action_id: str, reason: Optional[str] = None) -> Dict[str, Any]:
    """Reject an action"""
    return _client.reject(action_id, reason)


def getAction(action_id: str) -> Action:
    """Get an action by ID"""
    return _client.getAction(action_id)


def listActions(filters: Optional[Dict[str, Any]] = None) -> List[Action]:
    """List actions with optional filters"""
    return _client.listActions(filters)


def getEvidence(action_id: str) -> Evidence:
    """Get evidence for an action"""
    return _client.getEvidence(action_id)


def setPolicy(policy: Policy) -> Policy:
    """Set a policy"""
    return _client.setPolicy(policy)


# Legacy compatibility
ApaaiClient = AccountabilityLayer
TraceClient = AccountabilityLayer