import keyword
import re
import subprocess
import sys
from pathlib import Path


PYTHON_RESERVED = set(keyword.kwlist) | {"True", "False", "None", "type", "id"}


def _safe_enum_member(value: str, existing: set[str]) -> str:
    name = value.lower()
    name = re.sub(r"[^a-z0-9_]", "_", name)

    if name and name[0].isdigit():
        name = f"value_{name}"

    if not name:
        name = "empty"

    if name in PYTHON_RESERVED:
        name = f"{name}_"

    original = name
    counter = 1
    while name in existing:
        name = f"{original}_{counter}"
        counter += 1
    existing.add(name)

    return name


def _postprocess_enums(content: str, lowercase_enums: bool = True) -> str:
    if not lowercase_enums:
        return content

    enum_pattern = re.compile(
        r"(class\s+\w+Enum\s*\([^)]*Enum[^)]*\)\s*:)(.*?)(?=\nclass|\Z)",
        re.DOTALL,
    )

    def process_enum(match: re.Match) -> str:
        class_def = match.group(1)
        body = match.group(2)

        def lowercase_member(m: re.Match) -> str:
            name = m.group(1).lower()
            value = m.group(2).lower()
            return f'{name} = "{value}"'

        body = re.sub(r'(\w+)\s*=\s*"([^"]+)"', lowercase_member, body)
        return class_def + body

    return enum_pattern.sub(process_enum, content)


def _fix_imports(content: str) -> str:
    if "datetime" in content and "from datetime import" not in content:
        content = "from datetime import datetime\n" + content

    if "List[" in content and "from typing import" in content:
        content = re.sub(
            r"from typing import ([^\n]+)",
            lambda m: f"from typing import {m.group(1)}"
            if "List" in m.group(1)
            else f"from typing import List, {m.group(1)}",
            content,
        )

    return content


def generate_schemas(
    spec_path: Path,
    output_path: Path,
    lowercase_enums: bool = False,
) -> None:
    cmd = [
        sys.executable,
        "-m",
        "datamodel_code_generator",
        "--input",
        str(spec_path),
        "--output",
        str(output_path),
        "--input-file-type",
        "openapi",
        "--output-model-type",
        "pydantic_v2.BaseModel",
        "--use-standard-collections",
        "--use-union-operator",
        "--field-constraints",
        "--use-annotated",
        "--collapse-root-models",
        "--enum-field-as-literal",
        "one",
    ]

    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        print(f"Warning: datamodel-codegen failed: {e.stderr}")
        print("Generating basic schemas manually...")
        _generate_basic_schemas(spec_path, output_path)
        return

    content = output_path.read_text(encoding="utf-8")
    content = _postprocess_enums(content, lowercase_enums)
    content = _fix_imports(content)
    output_path.write_text(content, encoding="utf-8")


def _clean_schema_name(name: str) -> str:
    cleaned = name.replace("[", "").replace("]", "")
    if "-" in cleaned:
        parts = cleaned.split("-")
        cleaned = "".join(part.capitalize() if i > 0 else part for i, part in enumerate(parts))
    parts = cleaned.split("_")
    return "".join(parts)


def _build_field_args(prop_schema: dict, is_required: bool) -> str:
    args = []

    if "default" in prop_schema:
        default_val = prop_schema["default"]
        if isinstance(default_val, str):
            args.append(f'default="{default_val}"')
        elif isinstance(default_val, bool):
            args.append(f"default={default_val}")
        elif default_val is None:
            args.append("default=None")
        else:
            args.append(f"default={default_val}")
    elif is_required:
        args.append("...")
    else:
        args.append("default=None")

    if "minLength" in prop_schema:
        args.append(f"min_length={prop_schema['minLength']}")
    if "maxLength" in prop_schema:
        args.append(f"max_length={prop_schema['maxLength']}")
    if "pattern" in prop_schema:
        pattern = prop_schema["pattern"].replace("\\", "\\\\").replace('"', '\\"')
        args.append(f'pattern=r"{pattern}"')

    if "minimum" in prop_schema:
        args.append(f"ge={prop_schema['minimum']}")
    if "maximum" in prop_schema:
        args.append(f"le={prop_schema['maximum']}")
    if "exclusiveMinimum" in prop_schema:
        args.append(f"gt={prop_schema['exclusiveMinimum']}")
    if "exclusiveMaximum" in prop_schema:
        args.append(f"lt={prop_schema['exclusiveMaximum']}")

    if "description" in prop_schema:
        desc = prop_schema["description"].replace('"', '\\"').replace("\n", " ")
        args.append(f'description="{desc}"')

    return ", ".join(args)


def _generate_basic_schemas(spec_path: Path, output_path: Path) -> None:
    import json

    with open(spec_path, encoding="utf-8") as f:
        spec = json.load(f)

    schemas = spec.get("components", {}).get("schemas", {})
    lines = [
        "from datetime import datetime",
        "from enum import Enum",
        "from typing import Any, Dict, List, Optional",
        "",
        "from pydantic import BaseModel, Field",
        "",
        "",
    ]

    for name, schema in schemas.items():
        if schema.get("type") == "string" and "enum" in schema:
            clean_name = _clean_schema_name(name)
            lines.append(f"class {clean_name}(Enum):")
            used_members: set[str] = set()
            for value in schema["enum"]:
                member_name = _safe_enum_member(str(value), used_members)
                member_value = str(value).lower()
                lines.append(f'    {member_name} = "{member_value}"')
            lines.append("")
            lines.append("")

    for name, schema in schemas.items():
        if schema.get("type") == "object":
            clean_name = _clean_schema_name(name)

            additional_props = schema.get("additionalProperties")
            if additional_props is True:
                lines.append(f"class {clean_name}(BaseModel):")
                lines.append('    model_config = {"extra": "allow"}')
                lines.append("")
                lines.append("")
                continue
            elif isinstance(additional_props, dict):
                value_type = _schema_to_type(additional_props, schemas)
                lines.append(f"{clean_name} = Dict[str, {value_type}]")
                lines.append("")
                lines.append("")
                continue

            lines.append(f"class {clean_name}(BaseModel):")

            if "description" in schema:
                desc = schema["description"].replace('"""', "'''")
                lines.append(f'    """{desc}"""')
                lines.append("")

            props = schema.get("properties", {})
            required = schema.get("required", [])

            if not props:
                lines.append("    pass")
            else:
                for prop_name, prop_schema in props.items():
                    python_type = _schema_to_type(prop_schema, schemas)
                    is_required = prop_name in required

                    if prop_schema.get("nullable") and "Optional" not in python_type:
                        python_type = f"Optional[{python_type}]"

                    field_args = _build_field_args(prop_schema, is_required)
                    lines.append(f"    {prop_name}: {python_type} = Field({field_args})")

            lines.append("")
            lines.append("")

    output_path.write_text("\n".join(lines), encoding="utf-8")


def _schema_to_type(schema: dict, all_schemas: dict) -> str:
    if "$ref" in schema:
        ref_name = schema["$ref"].split("/")[-1]
        return _clean_schema_name(ref_name)

    if "anyOf" in schema:
        types = [_schema_to_type(s, all_schemas) for s in schema["anyOf"] if s.get("type") != "null"]
        if len(types) == 1:
            return f"Optional[{types[0]}]"
        return f"Optional[{types[0]}]"

    type_map = {
        "string": "str",
        "integer": "int",
        "number": "float",
        "boolean": "bool",
        "array": "List",
    }

    schema_type = schema.get("type", "Any")

    if schema_type == "array":
        items = schema.get("items", {})
        item_type = _schema_to_type(items, all_schemas)
        return f"List[{item_type}]"

    if schema.get("format") == "date-time":
        return "datetime"

    return type_map.get(schema_type, "Any")
