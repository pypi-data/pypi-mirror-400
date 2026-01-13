from __future__ import annotations

from typing import Any, Dict, List
from random import randint, choice
import string

from fastapptest.core.schema_extractor import PydanticModel, PydanticField
from fastapptest.core.endpoint_extractor import Endpoint  # Your Endpoint class


def generate_dummy_value(field_type: str | None) -> Any:
    """
    Generate a dummy value for a field based on its type.
    """
    if field_type is None:
        return "string"
    field_type = field_type.lower()

    if "str" in field_type:
        return "".join(choice(string.ascii_letters) for _ in range(6))
    elif "int" in field_type:
        return randint(1, 100)
    elif "float" in field_type:
        return round(randint(1, 100) + randint(0, 99)/100, 2)
    elif "bool" in field_type:
        return choice([True, False])
    elif "list" in field_type:
        return []
    elif "dict" in field_type:
        return {}
    else:
        # fallback
        return f"sample_{field_type}"


def generate_payload_from_model(model: PydanticModel) -> Dict[str, Any]:
    """
    Generate a JSON-compatible dict from a PydanticModel
    """
    payload: Dict[str, Any] = {}
    for field in model.fields:
        payload[field.name] = field.default if field.default is not None else generate_dummy_value(field.type_annotation)
    return payload


def generate_payloads_for_endpoints(
    endpoints: List[Endpoint],
    models: List[PydanticModel],
) -> Dict[str, Dict[str, Any]]:
    """
    Generate payloads for POST/PUT/PATCH endpoints.

    Returns a dict:
    {
        endpoint_path: {"method": "POST", "body": {...}}
    }
    """
    payloads: Dict[str, Dict[str, Any]] = {}
    model_map = {model.name: model for model in models}

    for ep in endpoints:
        # ep.methods is a set of HTTP methods
        methods_upper = {m.upper() for m in ep.methods}

        # Determine if endpoint has a body
        if any(m in ["POST", "PUT", "PATCH"] for m in methods_upper):
            body_model_name = getattr(ep, "body_model_name", None)  # may be set in tests
            if body_model_name and body_model_name in model_map:
                body_model = model_map[body_model_name]
                body_payload = generate_payload_from_model(body_model)
            else:
                body_payload = {}

            # Pick first method for payload
            payloads[ep.path] = {"method": list(ep.methods)[0], "body": body_payload}

        else:
            # GET, DELETE usually no body
            payloads[ep.path] = {"method": list(ep.methods)[0], "body": None}

    return payloads
