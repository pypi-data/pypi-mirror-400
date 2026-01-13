# core/validators.py

from typing import Any, Dict, Optional, Union
from pydantic import BaseModel, ValidationError

class Validator:
    """
    Core response validator for FastAPI endpoints.
    Ensures correctness, reliability, and production readiness.
    """

    @staticmethod
    def validate_status(
        response: Dict[str, Any],
        expected_status: int = 200
    ) -> bool:
        """
        Validate HTTP status code.
        """
        status = response.get("status_code")
        if status is None:
            return False
        return status == expected_status

    @staticmethod
    def validate_schema(
        response: Dict[str, Any],
        model: Optional[BaseModel] = None
    ) -> bool:
        """
        Validate response JSON against a Pydantic model.
        """
        if not model:
            return True  # Nothing to validate
        data = response.get("response")
        if data is None:
            return False
        try:
            model.parse_obj(data)
            return True
        except ValidationError:
            return False

    @staticmethod
    def validate_content(
        response: Dict[str, Any],
        required_fields: Optional[list[str]] = None
    ) -> bool:
        """
        Ensure response contains required fields.
        """
        data = response.get("response", {})
        if not required_fields:
            return True
        if not isinstance(data, dict):
            return False
        return all(field in data for field in required_fields)

    @classmethod
    def validate(
        cls,
        response: Dict[str, Any],
        expected_status: int = 200,
        model: Optional[BaseModel] = None,
        required_fields: Optional[list[str]] = None
    ) -> Dict[str, Union[bool, str]]:
        """
        Full validation: status + schema + content
        Returns dict with 'passed' and 'error' keys.
        """
        passed = True
        errors = []

        if not cls.validate_status(response, expected_status):
            passed = False
            errors.append(f"Expected status {expected_status}, got {response.get('status_code')}")

        if model and not cls.validate_schema(response, model):
            passed = False
            errors.append("Response does not match schema")

        if required_fields and not cls.validate_content(response, required_fields):
            passed = False
            errors.append(f"Missing required fields: {required_fields}")

        return {"passed": passed, "error": "; ".join(errors) if errors else ""}
