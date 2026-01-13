from __future__ import annotations

from pathlib import Path
from typing import Dict, Any, List
import requests

from fastapptest.core.payload_generator import generate_payloads_for_endpoints
from fastapptest.core.schema_extractor import PydanticModel
from fastapptest.core.endpoint_extractor import Endpoint

BASE_URL = "http://127.0.0.1:8000"  # Replace with actual base URL when testing FastAPI app


def run_endpoint_tests(
    endpoints: List[Endpoint],
    models: List[PydanticModel],
    base_url: str = BASE_URL
) -> Dict[str, Dict[str, Any]]:
    """
    Automatically execute HTTP requests for all endpoints using generated payloads.

    Returns:
    {
        "path::METHOD": {
            "method": str,
            "body": dict | None,
            "status_code": int | None,
            "response": Any
        }
    }
    """
    results: Dict[str, Dict[str, Any]] = {}

    # Generate payloads (compatible with existing generator)
    payloads = generate_payloads_for_endpoints(endpoints, models)

    for ep in endpoints:
        for method in ep.methods:
            method = method.upper()
            key = f"{ep.path}::{method}"
            full_url = base_url.rstrip("/") + ep.path

            body = None
            payload_key = ep.path

            if payload_key in payloads:
                body = payloads[payload_key].get("body")

            try:
                if method == "GET":
                    resp = requests.get(full_url)
                elif method == "POST":
                    resp = requests.post(full_url, json=body)
                elif method == "PUT":
                    resp = requests.put(full_url, json=body)
                elif method == "PATCH":
                    resp = requests.patch(full_url, json=body)
                elif method == "DELETE":
                    resp = requests.delete(full_url)
                else:
                    resp = None

                results[key] = {
                    "method": method,
                    "body": body,
                    "status_code": resp.status_code if resp else None,
                    "response": resp.json() if resp and resp.content else None,
                }

            except Exception as e:
                results[key] = {
                    "method": method,
                    "body": body,
                    "status_code": None,
                    "response": str(e),
                }

    return results


def save_results_to_file(results: Dict[str, Dict[str, Any]], file_path: Path) -> None:
    """
    Save the results dict to a JSON file for review.
    """
    import json

    file_path.write_text(json.dumps(results, indent=4), encoding="utf-8")


if __name__ == "__main__":
    """
    Example usage:

    python -m core.test_generator
    """
    from core.schema_extractor import extract_pydantic_models
    from core.endpoint_extractor import extract_endpoints

    # Paths (adjust as needed for your FastAPI project)
    project_root = Path(__file__).resolve().parents[1]
    routers_file = project_root / "new_app" / "src" / "new_app" / "routers" / "users.py"
    schema_file = project_root / "new_app" / "src" / "new_app" / "schemas" / "user.py"

    # Extract models & endpoints
    models = extract_pydantic_models(schema_file)
    endpoints = extract_endpoints(routers_file)

    # Assign body_model_name for POST/PUT/PATCH endpoints (for testing)
    for ep in endpoints:
        if any(m.upper() in ["POST", "PUT", "PATCH"] for m in ep.methods):
            ep.body_model_name = "UserCreate"

    # Run tests
    results = run_endpoint_tests(endpoints, models, BASE_URL)

    # Save results
    save_results_to_file(results, project_root / "fastapi_test_results.json")

    print("Test execution complete. Results saved to fastapi_test_results.json")
