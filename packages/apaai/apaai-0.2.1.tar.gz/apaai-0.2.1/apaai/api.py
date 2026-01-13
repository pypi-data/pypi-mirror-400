from typing import Any, Dict, Optional
import requests
import os
import uuid
from datetime import datetime, timezone
from urllib.parse import urlencode

# Module-level singleton
_api = None

def configure(endpoint: Optional[str] = None, api_key: Optional[str] = None):
    """Configure the global API instance."""
    global _api
    _api = ApaaiAPI(endpoint, api_key)

def _get_api() -> 'ApaaiAPI':
    """Get the configured API instance."""
    global _api
    if _api is None:
        _api = ApaaiAPI(os.getenv('APAAI_ENDPOINT'), os.getenv('APAAI_KEY'))
    return _api

def propose(
    *,
    type: str,
    actor: Dict[str, Any],
    target: Optional[str] = None,
    params: Optional[Dict[str, Any]] = None,
    id: Optional[str] = None,
    timestamp: Optional[str] = None,
) -> Dict[str, Any]:
    """Propose an action."""
    return _get_api().create_action({
        "id": id or str(uuid.uuid4()),
        "timestamp": timestamp or datetime.now(tz=timezone.utc).isoformat().replace("+00:00", "Z"),
        "type": type,
        "actor": actor,
        "target": target,
        "params": params,
    })

def evidence(action_id: str, checks: list) -> Dict[str, Any]:
    """Submit evidence for an action."""
    return _get_api().submit_evidence({
        "actionId": action_id,
        "checks": checks,
    })

def policy(action_type: Optional[str] = None) -> Dict[str, Any]:
    """Get policy for an action type."""
    return _get_api().get_policy(action_type)

def approve(action_id: str, approver: Optional[str] = None) -> Dict[str, Any]:
    """Approve an action."""
    return _get_api().approve_action(action_id, approver)

def reject(action_id: str, reason: Optional[str] = None) -> Dict[str, Any]:
    """Reject an action."""
    return _get_api().reject_action(action_id, reason)

def getAction(action_id: str) -> Dict[str, Any]:
    """Get an action by ID."""
    return _get_api().get_action(action_id)

def listActions(filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """List actions with optional filters."""
    return _get_api().list_actions(filters)

def getEvidence(action_id: str) -> Dict[str, Any]:
    """Get evidence for an action."""
    return _get_api().get_evidence(action_id)

def setPolicy(policy: Dict[str, Any]) -> Dict[str, Any]:
    """Set a policy."""
    return _get_api().set_policy(policy)

class ApaaiAPI:
    def __init__(self, endpoint: Optional[str] = None, api_key: Optional[str] = None):
        self._endpoint = (endpoint or "http://localhost:8787").rstrip("/")
        self._api_key = api_key
        self._session = requests.Session()
        self._headers = {"Content-Type": "application/json"}
        if api_key:
            self._headers["Authorization"] = f"Bearer {api_key}"

    def _url(self, path: str) -> str:
        return f"{self._endpoint}{path}"

    def _request(self, method: str, path: str, json: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        res = self._session.request(method, self._url(path), json=json, headers=self._headers, timeout=30)
        res.raise_for_status()
        return res.json()

    def create_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        return self._request("POST", "/actions", json=action)

    def submit_evidence(self, ev: Dict[str, Any]) -> Dict[str, Any]:
        return self._request("POST", "/evidence", json=ev)

    def get_policy(self, action_type: Optional[str] = None) -> Dict[str, Any]:
        path = "/policy"
        if action_type:
            qs = urlencode({"actionType": action_type})
            path = f"{path}?{qs}"
        return self._request("GET", path)

    def set_policy(self, policy: Dict[str, Any]) -> Dict[str, Any]:
        return self._request("POST", "/policy", json=policy)

    def get_action(self, action_id: str) -> Dict[str, Any]:
        return self._request("GET", f"/actions/{action_id}")

    def list_actions(self, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        path = "/actions"
        if filters:
            qs = urlencode(filters)
            path = f"{path}?{qs}"
        return self._request("GET", path)

    def get_evidence(self, action_id: str) -> Dict[str, Any]:
        return self._request("GET", f"/evidence/{action_id}")

    def approve_action(self, action_id: str, approver: Optional[str] = None) -> Dict[str, Any]:
        return self._request("POST", f"/approve/{action_id}", json={"approver": approver})

    def reject_action(self, action_id: str, reason: Optional[str] = None) -> Dict[str, Any]:
        return self._request("POST", f"/reject/{action_id}", json={"reason": reason})
