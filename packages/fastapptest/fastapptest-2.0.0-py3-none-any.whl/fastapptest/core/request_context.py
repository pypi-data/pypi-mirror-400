# core/request_context.py

from typing import Dict, Any, List
import re

from fastapptest.core.endpoint_extractor import Endpoint
from fastapptest.core.schema_extractor import PydanticModel


def extract_path_params(path: str) -> List[str]:
    """Extract {param} from path"""
    return re.findall(r"{(.*?)}", path)


def prompt_path_params(path: str) -> str:
    """Ask user for path parameter values"""
    params = extract_path_params(path)
    final_path = path

    for param in params:
        value = input(f"Enter value for path parameter '{param}': ").strip()
        final_path = final_path.replace(f"{{{param}}}", value)

    return final_path


def prompt_body(model: PydanticModel) -> Dict[str, Any]:
    """Prompt user for request body fields"""
    print("\nRequest Body Schema:", model.name)
    print("-" * 40)

    body: Dict[str, Any] = {}

    for field_name, field_type in model.fields.items():
        required = not field_type.startswith("Optional")
        prompt = f"{field_name} ({field_type})"
        prompt += " [required]: " if required else " [optional]: "

        value = input(prompt).strip()

        if value == "":
            if required:
                print(f"[ERROR] '{field_name}' is required")
                return prompt_body(model)
            body[field_name] = None
        else:
            body[field_name] = value

    return body


def build_request_context(
    endpoint: Endpoint,
    models: List[PydanticModel],
) -> Dict[str, Any]:
    """
    Builds final request context interactively
    """
    # Path params
    final_path = prompt_path_params(endpoint.path)

    # Body
    body = None
    if endpoint.body_model_name:
        model = next(
            (m for m in models if m.name == endpoint.body_model_name),
            None,
        )
        if model:
            body = prompt_body(model)

    return {
        "path": final_path,
        "method": endpoint.methods[0],
        "body": body,
    }
