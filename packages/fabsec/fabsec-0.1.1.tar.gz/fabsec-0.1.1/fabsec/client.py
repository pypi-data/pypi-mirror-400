# fabsec/client.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional, Union

try:
    import requests
except Exception as e:  # pragma: no cover
    raise RuntimeError("Le SDK FabSec nécessite 'requests'. Installe: pip install requests") from e

from .errors import FabSecHTTPError

DEFAULT_TIMEOUT: Union[int, float] = 15


@dataclass
class FabSecClient:
    api_key: str
    base_url: str = "http://127.0.0.1:8080"
    timeout: Union[int, float] = DEFAULT_TIMEOUT

    def _headers(self) -> Dict[str, str]:
        return {
            "X-FabSec-ApiKey": self.api_key,
            "Content-Type": "application/json",
        }

    def _request(self, method: str, path: str, *, params=None, json=None) -> Dict[str, Any]:
        url = self.base_url.rstrip("/") + path

        r = requests.request(
            method=method,
            url=url,
            headers=self._headers(),
            params=params,
            json=json,
            timeout=self.timeout,
        )

        # essaie JSON, sinon texte
        try:
            data = r.json()
        except Exception:
            data = None

        if r.status_code >= 400:
            if isinstance(data, dict) and "detail" in data:
                detail = data["detail"]
            else:
                detail = r.text
            raise FabSecHTTPError(r.status_code, detail, r.text)

        # normalise réponse
        if isinstance(data, dict):
            return data
        if isinstance(data, list):
            return {"items": data}
        return {"raw": r.text}

    # -------------------------
    # Core endpoints
    # -------------------------
    def ingest(self, event: Dict[str, Any]) -> Dict[str, Any]:
        return self._request("POST", "/v1/ingest", json=event)

    def coach_audit(self, audit_id: str) -> Dict[str, Any]:
        return self._request("GET", f"/v1/coach/audit/{audit_id}")

    def compare_user(self, user_id: str, boundary_iso: str, app_id: Optional[str] = None) -> Dict[str, Any]:
        params = {"boundary": boundary_iso}
        if app_id:
            params["app_id"] = app_id
        return self._request("GET", f"/v1/compare/user/{user_id}", params=params)

    def copilot_query(
        self,
        question: str,
        *,
        app_id: Optional[str] = None,
        user_id: Optional[str] = None,
        incident_id: Optional[str] = None,
        limit: int = 50,
    ) -> Dict[str, Any]:
        payload = {
            "question": question,
            "app_id": app_id,
            "user_id": user_id,
            "incident_id": incident_id,
            "limit": int(limit),
        }
        return self._request("POST", "/v1/copilot/query", json=payload)

    # -------------------------
    # License
    # -------------------------
    def license_me(self) -> Dict[str, Any]:
        return self._request("GET", "/v1/license/me")

    def license_telemetry(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return self._request("POST", "/v1/license/telemetry", json=payload)

    # -------------------------
    # Feedback
    # -------------------------
    def feedback_create(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return self._request("POST", "/v1/feedback", json=payload)

    def feedback_recent(self, app_id: Optional[str] = None, limit: int = 20) -> Dict[str, Any]:
        params: Dict[str, Any] = {"limit": int(limit)}
        if app_id:
            params["app_id"] = app_id
        return self._request("GET", "/v1/feedback/recent", params=params)

    # -------------------------
    # Observer
    # -------------------------
    def observer_recommendation_create(self, app_id: str, audits_limit: int = 300) -> Dict[str, Any]:
        params = {"audits_limit": int(audits_limit)}
        return self._request("POST", f"/v1/observer/recommendation/{app_id}", params=params)

    def observer_recommendations_list(self, app_id: str, limit: int = 50) -> Dict[str, Any]:
        params = {"limit": int(limit)}
        return self._request("GET", f"/v1/observer/recommendations/{app_id}", params=params)

    def observer_recommendation_by_id(self, proposal_id: str) -> Dict[str, Any]:
        return self._request("GET", f"/v1/observer/recommendation/by-id/{proposal_id}")

    # -------------------------
    # Policies
    # -------------------------
    def policy_from_text(self, text: str, app_id: Optional[str] = None, status: Optional[str] = None) -> Dict[str, Any]:
        payload = {"text": text, "app_id": app_id, "status": status}
        return self._request("POST", "/v1/policies/from-text", json=payload)

    def policies_list(self, app_id: Optional[str] = None, status: Optional[str] = "ACTIVE") -> Dict[str, Any]:
        params: Dict[str, Any] = {"status": status}
        if app_id:
            params["app_id"] = app_id
        return self._request("GET", "/v1/policies", params=params)

    # -------------------------
    # Profile / Graph / RedTeam
    # -------------------------
    def profile_user(self, user_id: str) -> Dict[str, Any]:
        return self._request("GET", f"/v1/profile/user/{user_id}")

    def graph_user(self, user_id: str) -> Dict[str, Any]:
        return self._request("GET", f"/v1/graph/user/{user_id}")

    def redteam_plan_create(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return self._request("POST", "/v1/redteam/plan", json=payload)

    def redteam_plans_list(self, app_id: Optional[str] = None) -> Dict[str, Any]:
        params: Dict[str, Any] = {}
        if app_id:
            params["app_id"] = app_id
        return self._request("GET", "/v1/redteam/plans", params=params)

    def redteam_plan_get(self, plan_id: str) -> Dict[str, Any]:
        return self._request("GET", f"/v1/redteam/plan/{plan_id}")
