import ast
import tempfile
from pathlib import Path

import pytest

from openapi_client_gen import generate_schemas, generate_service, parse_openapi

SPECS_DIR = Path(__file__).parent.parent / "specs"

SPEC_FILES = [
    "empty.json",
    "simple_crud.json",
    "with_enums.json",
    "medium.json",
    "bulk_operations.json",
]


@pytest.fixture(params=SPEC_FILES)
def spec_path(request):
    path = SPECS_DIR / request.param
    if not path.exists():
        pytest.skip(f"Spec file not found: {path}")
    return path


class TestRealSpecs:
    def test_parse_spec(self, spec_path):
        spec = parse_openapi(spec_path)
        assert spec.title
        assert spec.version

    def test_generate_schemas(self, spec_path):
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir) / "schemas.py"
            generate_schemas(spec_path, output)

            if spec_path.name == "empty.json":
                return

            assert output.exists()
            content = output.read_text()
            ast.parse(content)

    def test_generate_service(self, spec_path):
        with tempfile.TemporaryDirectory() as tmpdir:
            spec = parse_openapi(spec_path)
            output = Path(tmpdir) / "service.py"
            generate_service(spec, output)

            assert output.exists()
            content = output.read_text()
            ast.parse(content)
            assert "class WebService" in content

    def test_full_generation(self, spec_path):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            spec = parse_openapi(spec_path)

            schemas_path = tmpdir / "schemas.py"
            service_path = tmpdir / "service.py"

            generate_schemas(spec_path, schemas_path)
            generate_service(spec, service_path)

            if spec_path.name != "empty.json":
                assert schemas_path.exists()
                schemas_content = schemas_path.read_text()
                ast.parse(schemas_content)

            assert service_path.exists()
            service_content = service_path.read_text()
            ast.parse(service_content)


class TestSpecificSpecs:
    def test_empty_spec_has_no_operations(self):
        spec = parse_openapi(SPECS_DIR / "empty.json")
        assert len(spec.operations) == 0
        assert len(spec.schema_names) == 0

    def test_simple_crud_has_basic_operations(self):
        spec = parse_openapi(SPECS_DIR / "simple_crud.json")
        assert len(spec.operations) > 0
        methods = {op.method for op in spec.operations}
        assert "get" in methods or "post" in methods

    def test_with_enums_generates_enum_classes(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir) / "schemas.py"
            generate_schemas(SPECS_DIR / "with_enums.json", output)
            content = output.read_text()
            assert "Enum" in content

    def test_medium_spec_generates_multiple_schemas(self):
        spec = parse_openapi(SPECS_DIR / "medium.json")
        assert len(spec.schema_names) >= 5

    def test_bulk_operations_has_multiple_endpoints(self):
        spec = parse_openapi(SPECS_DIR / "bulk_operations.json")
        assert len(spec.operations) >= 3
