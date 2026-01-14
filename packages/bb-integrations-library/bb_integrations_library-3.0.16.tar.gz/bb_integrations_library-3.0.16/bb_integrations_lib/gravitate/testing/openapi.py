import json

import httpx
from functools import lru_cache


@lru_cache(maxsize=10)
def get_openapi(url: str) -> dict:
    """Download OpenAPI schema from URL and return as dict."""
    response = httpx.get(url)
    response.raise_for_status()
    return response.json()


def get_updated_supply_and_dispatch_openapi_json(url: str, schemas_to_include: list[str]):
    """Update the supply and dispatch JSON file with the latest published schemas."""
    schema = get_openapi(url)
    fully_filtered = filter_schemas_by_references(filter_based_on_tag(schema, schemas_to_include))
    return json.dumps(fully_filtered)


def filter_based_on_tag(data: dict, criteria: list[str]) -> dict:
    """Filter OpenAPI paths based on tags."""
    filtered_data = data.copy()
    filtered_paths = {}

    for path, methods in data.get("paths", {}).items():
        matching_methods = {}
        for method, operation in methods.items():
            if isinstance(operation, dict):
                tags = operation.get("tags", [])
                if any(tag in tags for tag in criteria):
                    matching_methods[method] = operation
        if matching_methods:
            filtered_paths[path] = matching_methods

    filtered_data["paths"] = filtered_paths
    return filtered_data


def filter_schemas_by_references(data: dict) -> dict:
    filtered_data = data.copy()
    referenced_schemas = set()
    for path, methods in data.get("paths", {}).items():
        for method, operation in methods.items():
            if isinstance(operation, dict):
                _collect_schema_references(operation, referenced_schemas)
    if "components" in data and "schemas" in data["components"]:
        filtered_data["components"] = data["components"].copy()
        filtered_data["components"]["schemas"] = {
            name: schema for name, schema in data["components"]["schemas"].items()
            if name in referenced_schemas
        }
    return filtered_data


def _collect_schema_references(obj, referenced_schemas):
    if isinstance(obj, dict):
        for key, value in obj.items():
            if key == "$ref" and isinstance(value, str):
                if value.startswith("#/components/schemas/"):
                    schema_name = value.split("/")[-1]
                    referenced_schemas.add(schema_name)
            else:
                _collect_schema_references(value, referenced_schemas)
    elif isinstance(obj, list):
        for item in obj:
            _collect_schema_references(item, referenced_schemas)


