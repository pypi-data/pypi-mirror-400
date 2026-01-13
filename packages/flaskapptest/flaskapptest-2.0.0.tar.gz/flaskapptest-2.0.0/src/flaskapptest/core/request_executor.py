# flaskapptest/core/request_executor.py

import requests
from typing import Dict, Any


class RequestExecutor:
    """
    Executes HTTP requests to Flask endpoints.
    """

    def __init__(self, base_url: str, timeout: int = 10) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def execute(
        self,
        method: str,
        path: str,
        payload: Dict,
        headers: Dict | None = None,
    ) -> Dict[str, Any]:

        url = self._build_url(path, payload.get("path", {}))

        try:
            response = requests.request(
                method=method,
                url=url,
                params=payload.get("query"),
                json=payload.get("body"),
                headers=headers,
                timeout=self.timeout,
            )
        except requests.RequestException as exc:
            return {
                "error": str(exc),
                "status_code": None,
                "body": None,
            }

        return {
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "body": self._safe_json(response),
        }

    def _build_url(self, path: str, path_params: Dict) -> str:
        """
        Injects path params into URL.
        """
        for key, value in path_params.items():
            path = path.replace(f"<{key}>", str(value))
        return f"{self.base_url}{path}"

    def _safe_json(self, response: requests.Response):
        try:
            return response.json()
        except ValueError:
            return response.text
