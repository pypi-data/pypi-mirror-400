import json
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest


class TestEndToEndGeneration:
    @pytest.fixture
    def full_openapi_spec(self):
        return {
            "openapi": "3.0.0",
            "info": {"title": "Test API", "version": "1.0.0"},
            "paths": {
                "/users/": {
                    "get": {
                        "operationId": "list_users_api_v1_users__get",
                        "summary": "List all users",
                        "parameters": [
                            {"name": "search", "in": "query", "required": False, "schema": {"type": "string"}},
                            {"name": "status", "in": "query", "required": False, "schema": {"anyOf": [{"$ref": "#/components/schemas/UserStatus"}, {"type": "null"}]}},
                            {"name": "limit", "in": "query", "required": False, "schema": {"type": "integer"}},
                        ],
                        "responses": {"200": {"content": {"application/json": {"schema": {"type": "array", "items": {"$ref": "#/components/schemas/User"}}}}}},
                    },
                    "post": {
                        "operationId": "create_user_api_v1_users__post",
                        "summary": "Create new user",
                        "requestBody": {"required": True, "content": {"application/json": {"schema": {"$ref": "#/components/schemas/UserCreate"}}}},
                        "responses": {"200": {"content": {"application/json": {"schema": {"$ref": "#/components/schemas/User"}}}}},
                    },
                },
                "/users/{id}/": {
                    "get": {
                        "operationId": "get_user_api_v1_users__id___get",
                        "summary": "Get user by ID",
                        "parameters": [{"name": "id", "in": "path", "required": True, "schema": {"type": "integer"}}],
                        "responses": {"200": {"content": {"application/json": {"schema": {"$ref": "#/components/schemas/User"}}}}},
                    },
                    "put": {
                        "operationId": "update_user_api_v1_users__id___put",
                        "summary": "Update user",
                        "parameters": [{"name": "id", "in": "path", "required": True, "schema": {"type": "integer"}}],
                        "requestBody": {"required": True, "content": {"application/json": {"schema": {"$ref": "#/components/schemas/UserUpdate"}}}},
                        "responses": {"200": {"content": {"application/json": {"schema": {"$ref": "#/components/schemas/User"}}}}},
                    },
                    "delete": {
                        "operationId": "delete_user_api_v1_users__id___delete",
                        "summary": "Delete user",
                        "parameters": [{"name": "id", "in": "path", "required": True, "schema": {"type": "integer"}}],
                        "responses": {"200": {"description": "Success"}},
                    },
                },
                "/items/": {
                    "get": {
                        "operationId": "get_items_api_v1_items__get",
                        "summary": "Get items with reserved params",
                        "parameters": [
                            {"name": "type", "in": "query", "required": False, "schema": {"type": "string"}},
                            {"name": "class", "in": "query", "required": False, "schema": {"type": "string"}},
                        ],
                        "responses": {"200": {"content": {"application/json": {"schema": {"type": "array", "items": {"$ref": "#/components/schemas/Item"}}}}}},
                    },
                },
            },
            "components": {
                "schemas": {
                    "UserStatus": {"type": "string", "enum": ["ACTIVE", "INACTIVE", "PENDING", "active"]},
                    "User": {
                        "type": "object",
                        "required": ["id", "name", "status"],
                        "properties": {
                            "id": {"type": "integer"},
                            "name": {"type": "string"},
                            "email": {"anyOf": [{"type": "string"}, {"type": "null"}]},
                            "status": {"$ref": "#/components/schemas/UserStatus"},
                            "created_at": {"type": "string", "format": "date-time"},
                        },
                    },
                    "UserCreate": {"type": "object", "required": ["name"], "properties": {"name": {"type": "string"}, "email": {"type": "string"}}},
                    "UserUpdate": {"type": "object", "properties": {"name": {"type": "string"}, "email": {"type": "string"}, "status": {"$ref": "#/components/schemas/UserStatus"}}},
                    "Item": {"type": "object", "properties": {"id": {"type": "integer"}, "type": {"type": "string"}, "tags": {"type": "array", "items": {"type": "string"}}}},
                }
            },
        }

    def _write_spec_and_generate(self, spec: dict) -> tuple[str, str]:
        from openapi_client_gen.generators.schemas import generate_schemas
        from openapi_client_gen.generators.service import generate_service
        from openapi_client_gen.parser import parse_openapi

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            spec_path = tmpdir_path / "openapi.json"
            spec_path.write_text(json.dumps(spec))

            schemas_path = tmpdir_path / "schemas.py"
            generate_schemas(spec_path, schemas_path, lowercase_enums=True)

            parsed = parse_openapi(spec_path)
            service_path = tmpdir_path / "service.py"
            generate_service(parsed, service_path)

            return schemas_path.read_text(), service_path.read_text()

    def test_full_generation_workflow(self, full_openapi_spec):
        schemas_content, service_content = self._write_spec_and_generate(full_openapi_spec)

        assert "class UserStatus(Enum):" in schemas_content
        assert "class User(BaseModel):" in schemas_content
        assert "class UserCreate(BaseModel):" in schemas_content
        assert "class UserUpdate(BaseModel):" in schemas_content
        assert "class Item(BaseModel):" in schemas_content

        assert "class WebService(ExternalService):" in service_content
        assert "async def list_users(" in service_content
        assert "async def create_user(" in service_content
        assert "async def get_user(" in service_content
        assert "async def update_user(" in service_content
        assert "async def delete_user(" in service_content
        assert "async def get_items(" in service_content

    def test_reserved_words_handled_in_generated_code(self, full_openapi_spec):
        schemas_content, service_content = self._write_spec_and_generate(full_openapi_spec)

        assert "id_: int" in service_content
        assert 'f"/users/{id_}/"' in service_content

        assert "type_: Optional[str]" in service_content
        assert "class_: Optional[str]" in service_content
        assert '"type": type_' in service_content
        assert '"class": class_' in service_content

    def test_enum_collision_handled(self, full_openapi_spec):
        schemas_content, _ = self._write_spec_and_generate(full_openapi_spec)

        assert "active" in schemas_content.lower()

    def test_datetime_fields_generated(self, full_openapi_spec):
        schemas_content, _ = self._write_spec_and_generate(full_openapi_spec)

        assert "datetime" in schemas_content.lower() or "AwareDatetime" in schemas_content
        assert "created_at" in schemas_content

    def test_optional_fields_generated(self, full_openapi_spec):
        schemas_content, _ = self._write_spec_and_generate(full_openapi_spec)

        assert "Optional" in schemas_content or "| None" in schemas_content
        assert "email:" in schemas_content

    def test_array_fields_generated(self, full_openapi_spec):
        schemas_content, _ = self._write_spec_and_generate(full_openapi_spec)

        assert "List" in schemas_content or "list[" in schemas_content
        assert "tags" in schemas_content

    def test_generated_schemas_are_valid_python(self, full_openapi_spec):
        schemas_content, _ = self._write_spec_and_generate(full_openapi_spec)

        compile(schemas_content, "<string>", "exec")

    def test_generated_service_is_valid_python(self, full_openapi_spec):
        _, service_content = self._write_spec_and_generate(full_openapi_spec)

        compile(service_content, "<string>", "exec")

    def test_imports_are_complete(self, full_openapi_spec):
        schemas_content, service_content = self._write_spec_and_generate(full_openapi_spec)

        assert "from enum import Enum" in schemas_content
        assert "BaseModel" in schemas_content

        assert "from external_service import ExternalService, HTTPResponse" in service_content
        assert "from typing import" in service_content

    def test_filter_params_method_present(self, full_openapi_spec):
        _, service_content = self._write_spec_and_generate(full_openapi_spec)

        assert "def _filter_params(" in service_content
        assert "isinstance(v, bool)" in service_content
        assert "isinstance(v, Enum)" in service_content


class TestCLIIntegration:
    @pytest.fixture
    def simple_spec(self):
        return {
            "openapi": "3.0.0",
            "info": {"title": "CLI Test API", "version": "1.0.0"},
            "paths": {
                "/health/": {
                    "get": {
                        "operationId": "health_check",
                        "responses": {"200": {}},
                    }
                }
            },
            "components": {
                "schemas": {
                    "Status": {"type": "string", "enum": ["OK", "ERROR"]}
                }
            },
        }

    def test_cli_generates_files(self, simple_spec):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            spec_path = tmpdir_path / "openapi.json"
            spec_path.write_text(json.dumps(simple_spec))

            output_dir = tmpdir_path / "output"
            output_dir.mkdir()

            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "openapi_client_gen.cli",
                    "-i",
                    str(spec_path),
                    "-o",
                    str(output_dir),
                ],
                capture_output=True,
                text=True,
                cwd=Path(__file__).parent.parent,
            )

            assert result.returncode == 0, f"CLI failed: {result.stderr}"

            assert (output_dir / "schemas.py").exists()
            assert (output_dir / "service.py").exists()

    def test_cli_with_lowercase_enums_disabled(self, simple_spec):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            spec_path = tmpdir_path / "openapi.json"
            spec_path.write_text(json.dumps(simple_spec))

            output_dir = tmpdir_path / "output"
            output_dir.mkdir()

            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "openapi_client_gen.cli",
                    "-i",
                    str(spec_path),
                    "-o",
                    str(output_dir),
                    "--no-lowercase-enums",
                ],
                capture_output=True,
                text=True,
                cwd=Path(__file__).parent.parent,
            )

            assert result.returncode == 0, f"CLI failed: {result.stderr}"

            assert (output_dir / "schemas.py").exists()
            assert (output_dir / "service.py").exists()


class TestEdgeCases:
    def test_empty_spec(self):
        from openapi_client_gen.generators.schemas import generate_schemas
        from openapi_client_gen.generators.service import generate_service
        from openapi_client_gen.parser import parse_openapi

        spec = {
            "openapi": "3.0.0",
            "info": {"title": "Empty API", "version": "1.0.0"},
            "paths": {},
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            spec_path = tmpdir_path / "openapi.json"
            spec_path.write_text(json.dumps(spec))

            schemas_path = tmpdir_path / "schemas.py"
            generate_schemas(spec_path, schemas_path)

            parsed = parse_openapi(spec_path)
            service_path = tmpdir_path / "service.py"
            generate_service(parsed, service_path)

            schemas_content = schemas_path.read_text()
            service_content = service_path.read_text()

            compile(schemas_content, "<string>", "exec")
            compile(service_content, "<string>", "exec")

            assert "class WebService(ExternalService):" in service_content

    def test_deeply_nested_refs(self):
        from openapi_client_gen.generators.schemas import generate_schemas
        from openapi_client_gen.generators.service import generate_service
        from openapi_client_gen.parser import parse_openapi

        spec = {
            "openapi": "3.0.0",
            "info": {"title": "Nested API", "version": "1.0.0"},
            "paths": {
                "/teams/": {
                    "get": {
                        "operationId": "get_teams",
                        "responses": {"200": {"content": {"application/json": {"schema": {"type": "array", "items": {"$ref": "#/components/schemas/Team"}}}}}},
                    }
                }
            },
            "components": {
                "schemas": {
                    "Team": {"type": "object", "properties": {"name": {"type": "string"}, "members": {"type": "array", "items": {"$ref": "#/components/schemas/User"}}}},
                    "User": {"type": "object", "properties": {"name": {"type": "string"}, "address": {"$ref": "#/components/schemas/Address"}}},
                    "Address": {"type": "object", "properties": {"street": {"type": "string"}, "city": {"type": "string"}}},
                }
            },
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            spec_path = tmpdir_path / "openapi.json"
            spec_path.write_text(json.dumps(spec))

            schemas_path = tmpdir_path / "schemas.py"
            generate_schemas(spec_path, schemas_path)

            schemas_content = schemas_path.read_text()

            assert "class Team(BaseModel):" in schemas_content
            assert "class User(BaseModel):" in schemas_content
            assert "class Address(BaseModel):" in schemas_content

    def test_operation_id_with_special_chars(self):
        from openapi_client_gen.generators.service import generate_service
        from openapi_client_gen.parser import parse_openapi

        spec = {
            "openapi": "3.0.0",
            "info": {"title": "Special API", "version": "1.0.0"},
            "paths": {
                "/data/": {
                    "get": {"operationId": "get-data-v1", "responses": {"200": {}}},
                    "post": {"operationId": "create.data.v1", "responses": {"200": {}}},
                }
            },
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            spec_path = tmpdir_path / "openapi.json"
            spec_path.write_text(json.dumps(spec))

            parsed = parse_openapi(spec_path)
            service_path = tmpdir_path / "service.py"
            generate_service(parsed, service_path)

            service_content = service_path.read_text()

            assert "async def get_data_v1(" in service_content
            assert "async def create_data_v1(" in service_content

    def test_duplicate_operation_names(self):
        from openapi_client_gen.generators.service import generate_service
        from openapi_client_gen.parser import parse_openapi

        spec = {
            "openapi": "3.0.0",
            "info": {"title": "Duplicate API", "version": "1.0.0"},
            "paths": {
                "/v1/users/": {"get": {"operationId": "get_users_v1_users__get", "responses": {"200": {}}}},
                "/v2/users/": {"get": {"operationId": "get_users_v2_users__get", "responses": {"200": {}}}},
            },
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            spec_path = tmpdir_path / "openapi.json"
            spec_path.write_text(json.dumps(spec))

            parsed = parse_openapi(spec_path)

            function_names = [op.function_name for op in parsed.operations]
            assert len(function_names) == len(set(function_names))

    def test_all_http_methods(self):
        from openapi_client_gen.generators.service import generate_service
        from openapi_client_gen.parser import parse_openapi

        spec = {
            "openapi": "3.0.0",
            "info": {"title": "Methods API", "version": "1.0.0"},
            "paths": {
                "/resource/": {
                    "get": {"operationId": "get_resource", "responses": {"200": {}}},
                    "post": {"operationId": "create_resource", "responses": {"200": {}}},
                    "put": {"operationId": "update_resource", "responses": {"200": {}}},
                    "delete": {"operationId": "delete_resource", "responses": {"200": {}}},
                    "patch": {"operationId": "patch_resource", "responses": {"200": {}}},
                }
            },
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            spec_path = tmpdir_path / "openapi.json"
            spec_path.write_text(json.dumps(spec))

            parsed = parse_openapi(spec_path)
            service_path = tmpdir_path / "service.py"
            generate_service(parsed, service_path)

            service_content = service_path.read_text()

            assert "await self.get(" in service_content
            assert "await self.post(" in service_content
            assert "await self.put(" in service_content
            assert "await self.delete(" in service_content
            assert "await self.patch(" in service_content

    def test_multiple_path_params(self):
        from openapi_client_gen.generators.service import generate_service
        from openapi_client_gen.parser import parse_openapi

        spec = {
            "openapi": "3.0.0",
            "info": {"title": "Nested API", "version": "1.0.0"},
            "paths": {
                "/users/{user_id}/posts/{post_id}/comments/{comment_id}": {
                    "get": {
                        "operationId": "get_comment",
                        "parameters": [
                            {"name": "user_id", "in": "path", "required": True, "schema": {"type": "integer"}},
                            {"name": "post_id", "in": "path", "required": True, "schema": {"type": "integer"}},
                            {"name": "comment_id", "in": "path", "required": True, "schema": {"type": "integer"}},
                        ],
                        "responses": {"200": {}},
                    }
                }
            },
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            spec_path = tmpdir_path / "openapi.json"
            spec_path.write_text(json.dumps(spec))

            parsed = parse_openapi(spec_path)
            service_path = tmpdir_path / "service.py"
            generate_service(parsed, service_path)

            service_content = service_path.read_text()

            assert "user_id: int" in service_content
            assert "post_id: int" in service_content
            assert "comment_id: int" in service_content
            assert 'f"/users/{user_id}/posts/{post_id}/comments/{comment_id}"' in service_content
