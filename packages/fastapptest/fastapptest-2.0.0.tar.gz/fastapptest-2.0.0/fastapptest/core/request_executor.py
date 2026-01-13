# core/request_executor.py

from typing import Dict, Any
import requests


def execute_request(
    base_url: str,
    path: str,
    method: str,
    body: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """
    Execute HTTP request and return response info
    """
    url = base_url.rstrip("/") + path
    method = method.upper()

    try:
        if method == "GET":
            resp = requests.get(url)
        elif method == "POST":
            resp = requests.post(url, json=body)
        elif method == "PUT":
            resp = requests.put(url, json=body)
        elif method == "PATCH":
            resp = requests.patch(url, json=body)
        elif method == "DELETE":
            resp = requests.delete(url)
        else:
            return {"error": f"Unsupported method: {method}"}

        return {
            "status_code": resp.status_code,
            "response": resp.json() if resp.content else None,
        }

    except Exception as exc:
        return {"error": str(exc)}
