import json
from pathlib import Path
from typing import Any

from .models import Operation, Parameter, ParsedSpec
from .utils import safe_function_name


def _clean_schema_name(name: str) -> str:
    cleaned = name.replace("[", "").replace("]", "")
    parts = cleaned.split("_")
    return "".join(parts)


def _get_python_type(schema: dict[str, Any], spec: dict[str, Any]) -> str:
    if "$ref" in schema:
        ref = schema["$ref"]
        schema_name = ref.split("/")[-1]
        return _clean_schema_name(schema_name)

    if "anyOf" in schema:
        types = []
        for sub in schema["anyOf"]:
            if sub.get("type") == "null":
                continue
            types.append(_get_python_type(sub, spec))
        if len(types) == 1:
            return f"Optional[{types[0]}]"
        return f"Optional[Union[{', '.join(types)}]]"

    if "allOf" in schema:
        for sub in schema["allOf"]:
            if "$ref" in sub:
                return _get_python_type(sub, spec)
        return "dict"

    if "oneOf" in schema:
        types = [_get_python_type(sub, spec) for sub in schema["oneOf"]]
        if len(types) == 1:
            return types[0]
        return f"Union[{', '.join(types)}]"

    schema_type = schema.get("type", "Any")

    if schema_type == "array":
        items = schema.get("items", {})
        item_type = _get_python_type(items, spec)
        return f"List[{item_type}]"

    type_map = {
        "string": "str",
        "integer": "int",
        "number": "float",
        "boolean": "bool",
        "object": "dict",
        "null": "None",
    }

    return type_map.get(schema_type, "Any")


def _get_response_type(responses: dict[str, Any], spec: dict[str, Any]) -> str:
    success = responses.get("200", {})
    content = success.get("content", {})
    json_content = content.get("application/json", {})
    schema = json_content.get("schema", {})

    if not schema:
        return "Any"

    return _get_python_type(schema, spec)


def _parse_operation(
    path: str, method: str, operation: dict[str, Any], spec: dict[str, Any]
) -> Operation:
    parameters = []

    for param in operation.get("parameters", []):
        param_schema = param.get("schema", {})
        python_type = _get_python_type(param_schema, spec)

        if not param.get("required", False) and not python_type.startswith("Optional"):
            python_type = f"Optional[{python_type}]"

        parameters.append(
            Parameter(
                name=param["name"],
                python_type=python_type,
                required=param.get("required", False),
                in_=param.get("in", "query"),
                description=param.get("description"),
            )
        )

    request_body = operation.get("requestBody", {})
    request_body_type = None
    if request_body:
        content = request_body.get("content", {})
        json_content = content.get("application/json", {})
        schema = json_content.get("schema", {})
        if schema:
            request_body_type = _get_python_type(schema, spec)

    response_type = _get_response_type(operation.get("responses", {}), spec)

    return Operation(
        operation_id=operation.get("operationId", f"{method}_{path}"),
        path=path,
        method=method,
        summary=operation.get("summary"),
        parameters=parameters,
        request_body_type=request_body_type,
        response_type=response_type,
    )


def parse_openapi(spec_path: Path) -> ParsedSpec:
    with open(spec_path, encoding="utf-8") as f:
        spec = json.load(f)

    info = spec.get("info", {})
    operations = []
    used_function_names: set[str] = set()

    for path, path_item in spec.get("paths", {}).items():
        for method in ["get", "post", "put", "delete", "patch"]:
            if method in path_item:
                operation = _parse_operation(path, method, path_item[method], spec)
                operation.function_name_override = safe_function_name(
                    operation.function_name, used_function_names
                )
                operations.append(operation)

    schemas = spec.get("components", {}).get("schemas", {})
    schema_names = list(schemas.keys())

    return ParsedSpec(
        title=info.get("title", "API"),
        version=info.get("version", "1.0.0"),
        operations=operations,
        schema_names=schema_names,
    )
