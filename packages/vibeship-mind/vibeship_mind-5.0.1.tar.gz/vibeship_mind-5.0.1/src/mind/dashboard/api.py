"""Dashboard API client.

Fetches data from the Mind v5 API for visualization.
"""

import os

import httpx


class DashboardAPI:
    """Client for fetching dashboard data from Mind API."""

    def __init__(self, base_url: str = None):
        self.base_url = base_url or os.environ.get("MIND_API_URL", "http://localhost:8080")
        self._client = httpx.Client(base_url=self.base_url, timeout=10.0)

    def health(self) -> dict:
        """Get system health status."""
        try:
            response = self._client.get("/health")
            return response.json()
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def ready(self) -> dict:
        """Get detailed readiness status."""
        try:
            response = self._client.get("/ready")
            return response.json()
        except Exception as e:
            return {"status": "error", "services": {}, "error": str(e)}

    def metrics(self) -> str:
        """Get Prometheus metrics."""
        try:
            response = self._client.get("/metrics")
            return response.text
        except Exception:
            return ""

    def get_memories(
        self,
        user_id: str,
        query: str = "",
        limit: int = 20,
        min_salience: float = 0.0,
    ) -> dict:
        """Retrieve memories for a user."""
        try:
            response = self._client.post(
                "/v1/memories/retrieve",
                json={
                    "user_id": user_id,
                    "query": query or "all memories",
                    "limit": limit,
                    "min_salience": min_salience,
                },
            )
            if response.status_code == 200:
                return response.json()
            return {"memories": [], "error": response.text}
        except Exception as e:
            return {"memories": [], "error": str(e)}

    def get_decisions(self, user_id: str, limit: int = 20) -> dict:
        """Get decision context for a user."""
        try:
            response = self._client.post(
                "/v1/decisions/context",
                json={"user_id": user_id, "query": "recent decisions"},
            )
            if response.status_code == 200:
                return response.json()
            return {"decisions": [], "error": response.text}
        except Exception as e:
            return {"decisions": [], "error": str(e)}

    def admin_status(self) -> dict:
        """Get admin system status."""
        try:
            response = self._client.get("/v1/admin/status")
            if response.status_code == 200:
                return response.json()
            return {"error": response.text}
        except Exception as e:
            return {"error": str(e)}

    def dlq_stats(self) -> dict:
        """Get Dead Letter Queue stats."""
        try:
            response = self._client.get("/v1/admin/dlq/stats")
            if response.status_code == 200:
                return response.json()
            return {"total_messages": 0, "error": response.text}
        except Exception as e:
            return {"total_messages": 0, "error": str(e)}

    def pattern_effectiveness(self) -> dict:
        """Get pattern effectiveness metrics."""
        try:
            response = self._client.get("/v1/admin/patterns/effectiveness")
            if response.status_code == 200:
                return response.json()
            return {"patterns": [], "error": response.text}
        except Exception as e:
            return {"patterns": [], "error": str(e)}

    def anomalies(self) -> dict:
        """Get detected anomalies."""
        try:
            response = self._client.get("/anomalies")
            if response.status_code == 200:
                return response.json()
            return {"anomalies": [], "error": response.text}
        except Exception as e:
            return {"anomalies": [], "error": str(e)}

    def parse_metrics(self) -> dict:
        """Parse Prometheus metrics into a dict."""
        raw = self.metrics()
        if not raw:
            return {}

        parsed = {}
        for line in raw.split("\n"):
            if line.startswith("#") or not line.strip():
                continue
            try:
                # Simple parsing for basic metrics
                if " " in line:
                    name, value = line.rsplit(" ", 1)
                    # Clean up the name
                    base_name = name.split("{")[0] if "{" in name else name
                    parsed[base_name] = float(value)
            except (ValueError, IndexError):
                continue
        return parsed


# Global API instance
_api: DashboardAPI | None = None


def get_api() -> DashboardAPI:
    """Get or create the API client."""
    global _api
    if _api is None:
        _api = DashboardAPI()
    return _api
