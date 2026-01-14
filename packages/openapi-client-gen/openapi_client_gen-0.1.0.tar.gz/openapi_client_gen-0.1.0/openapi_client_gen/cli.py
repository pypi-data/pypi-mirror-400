import argparse
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

from .generators import generate_schemas, generate_service
from .parser import parse_openapi

try:
    __version__ = version("openapi-client-gen")
except PackageNotFoundError:
    __version__ = "0.0.0"


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="openapi-client-gen",
        description="Generate ExternalService client from OpenAPI specification",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --input openapi.json --output ./client
  %(prog)s -i openapi.json -o ./client --lowercase-enums
  %(prog)s -i openapi.json -o ./client --template custom_service.jinja2
        """,
    )

    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    parser.add_argument(
        "-i",
        "--input",
        type=Path,
        required=True,
        help="Path to OpenAPI JSON specification file",
    )

    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        required=True,
        help="Output directory for generated files",
    )

    parser.add_argument(
        "--template",
        type=Path,
        default=None,
        help="Path to custom Jinja2 template for service generation",
    )

    parser.add_argument(
        "--lowercase-enums",
        action="store_true",
        default=True,
        help="Convert enum values to lowercase (default: True)",
    )

    parser.add_argument(
        "--no-lowercase-enums",
        action="store_false",
        dest="lowercase_enums",
        help="Keep original enum values",
    )

    parser.add_argument(
        "--schemas-file",
        type=str,
        default="schemas.py",
        help="Name of the schemas output file (default: schemas.py)",
    )

    parser.add_argument(
        "--service-file",
        type=str,
        default="service.py",
        help="Name of the service output file (default: service.py)",
    )

    args = parser.parse_args()

    if not args.input.exists():
        parser.error(f"Input file does not exist: {args.input}")

    args.output.mkdir(parents=True, exist_ok=True)

    print(f"Parsing OpenAPI specification: {args.input}")
    spec = parse_openapi(args.input)
    print(f"  Found {len(spec.operations)} operations")
    print(f"  Found {len(spec.schema_names)} schemas")

    schemas_path = args.output / args.schemas_file
    print(f"Generating schemas: {schemas_path}")
    generate_schemas(
        spec_path=args.input,
        output_path=schemas_path,
        lowercase_enums=args.lowercase_enums,
    )

    service_path = args.output / args.service_file
    print(f"Generating service: {service_path}")
    generate_service(
        spec=spec,
        output_path=service_path,
        template_path=args.template,
    )

    init_path = args.output / "__init__.py"
    print(f"Generating __init__.py: {init_path}")
    init_content = """from .schemas import *
from .service import WebService

__all__ = ["WebService"]
"""
    init_path.write_text(init_content, encoding="utf-8")

    print("Done!")
    print("\nGenerated files:")
    print(f"  - {schemas_path}")
    print(f"  - {service_path}")
    print(f"  - {init_path}")


if __name__ == "__main__":
    main()
