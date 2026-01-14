from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("openapi-client-gen")
except PackageNotFoundError:
    __version__ = "0.0.0"

from .cli import main
from .parser import parse_openapi
from .models import Operation, Parameter, ParsedSpec
from .generators import generate_schemas, generate_service
from .utils import safe_name, safe_function_name, safe_enum_member

__all__ = [
    "__version__",
    "main",
    "parse_openapi",
    "Operation",
    "Parameter",
    "ParsedSpec",
    "generate_schemas",
    "generate_service",
    "safe_name",
    "safe_function_name",
    "safe_enum_member",
]
