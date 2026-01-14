import re
from pathlib import Path
from typing import Optional

from jinja2 import Environment, FileSystemLoader

from ..models import Operation, ParsedSpec

TEMPLATES_DIR = Path(__file__).parent.parent / "templates"


def _extract_schema_names(type_str: str) -> set[str]:
    basic_types = {"Any", "None", "str", "int", "float", "bool", "dict", "bytes"}
    schemas = set()

    for match in re.findall(r"\b([A-Z][a-zA-Z0-9_]*)\b", type_str):
        if match not in basic_types and match not in {"List", "Optional", "Union", "Dict"}:
            schemas.add(match)

    return schemas


def _get_schema_imports(operations: list[Operation]) -> list[str]:
    imports = set()

    for op in operations:
        imports.update(_extract_schema_names(op.response_type))

        if op.request_body_type:
            imports.update(_extract_schema_names(op.request_body_type))

    return sorted(imports)


def generate_service(
    spec: ParsedSpec,
    output_path: Path,
    template_path: Optional[Path] = None,
) -> None:
    if template_path and template_path.exists():
        env = Environment(
            loader=FileSystemLoader(template_path.parent),
            trim_blocks=True,
            lstrip_blocks=True,
        )
        template = env.get_template(template_path.name)
    else:
        env = Environment(
            loader=FileSystemLoader(TEMPLATES_DIR),
            trim_blocks=True,
            lstrip_blocks=True,
        )
        template = env.get_template("service.py.jinja2")

    schema_imports = _get_schema_imports(spec.operations)

    content = template.render(
        operations=spec.operations,
        schema_imports=schema_imports,
        title=spec.title,
        version=spec.version,
    )

    output_path.write_text(content, encoding="utf-8")
