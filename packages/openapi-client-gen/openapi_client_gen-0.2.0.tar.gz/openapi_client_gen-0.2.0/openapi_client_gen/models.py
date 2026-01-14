from dataclasses import dataclass, field
from typing import Optional

from .utils import safe_name


@dataclass
class Parameter:
    name: str
    python_type: str
    required: bool = False
    in_: str = "query"
    description: Optional[str] = None

    @property
    def safe_name(self) -> str:
        return safe_name(self.name)

    @property
    def signature(self) -> str:
        name = self.safe_name
        if self.required:
            return f"{name}: {self.python_type}"
        return f"{name}: {self.python_type} = None"


@dataclass
class Operation:
    operation_id: str
    path: str
    method: str
    summary: Optional[str] = None
    parameters: list[Parameter] = field(default_factory=list)
    request_body_type: Optional[str] = None
    response_type: str = "Any"
    function_name_override: Optional[str] = None

    @property
    def function_name(self) -> str:
        if self.function_name_override:
            return self.function_name_override
        name = self.operation_id
        for suffix in ["_api_v1_", "_api_", "__get", "__post", "__put", "__delete", "__patch"]:
            if suffix in name:
                name = name.split(suffix)[0]
        return name

    @property
    def path_params(self) -> list[Parameter]:
        return [p for p in self.parameters if p.in_ == "path"]

    @property
    def query_params(self) -> list[Parameter]:
        return [p for p in self.parameters if p.in_ == "query"]

    @property
    def required_query_params(self) -> list[Parameter]:
        return [p for p in self.query_params if p.required]

    @property
    def optional_query_params(self) -> list[Parameter]:
        return [p for p in self.query_params if not p.required]

    @property
    def has_query_params(self) -> bool:
        return len(self.query_params) > 0

    @property
    def has_body(self) -> bool:
        return self.request_body_type is not None

    @property
    def formatted_path(self) -> str:
        path = self.path
        for param in self.path_params:
            path = path.replace("{" + param.name + "}", "{" + param.safe_name + "}")
        if self.path_params:
            return f'f"{path}"'
        return f'"{path}"'


@dataclass
class ParsedSpec:
    title: str
    version: str
    operations: list[Operation] = field(default_factory=list)
    schema_names: list[str] = field(default_factory=list)
