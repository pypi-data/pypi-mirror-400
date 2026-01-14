import json
import tempfile
from pathlib import Path

import pytest

from openapi_client_gen.parser import (
    _clean_schema_name,
    _get_python_type,
    _get_response_type,
    _parse_operation,
    parse_openapi,
)


class TestCleanSchemaName:
    def test_simple_name_unchanged(self):
        assert _clean_schema_name("User") == "User"
        assert _clean_schema_name("Mission") == "Mission"
        assert _clean_schema_name("MissionDisplay") == "MissionDisplay"

    def test_removes_underscores(self):
        assert _clean_schema_name("Response_List") == "ResponseList"
        assert _clean_schema_name("Mission_Display") == "MissionDisplay"

    def test_removes_brackets(self):
        assert _clean_schema_name("List[User]") == "ListUser"
        assert _clean_schema_name("Response[Data]") == "ResponseData"

    def test_complex_generic_names(self):
        assert _clean_schema_name("ResponseList_MissionDisplay_") == "ResponseListMissionDisplay"
        assert _clean_schema_name("Page_User_") == "PageUser"
        assert _clean_schema_name("Result_List_Item__") == "ResultListItem"


class TestGetPythonType:
    def test_ref_type(self):
        schema = {"$ref": "#/components/schemas/User"}
        assert _get_python_type(schema, {}) == "User"

    def test_ref_with_underscores(self):
        schema = {"$ref": "#/components/schemas/ResponseList_MissionDisplay_"}
        assert _get_python_type(schema, {}) == "ResponseListMissionDisplay"

    def test_string_type(self):
        schema = {"type": "string"}
        assert _get_python_type(schema, {}) == "str"

    def test_integer_type(self):
        schema = {"type": "integer"}
        assert _get_python_type(schema, {}) == "int"

    def test_number_type(self):
        schema = {"type": "number"}
        assert _get_python_type(schema, {}) == "float"

    def test_boolean_type(self):
        schema = {"type": "boolean"}
        assert _get_python_type(schema, {}) == "bool"

    def test_object_type(self):
        schema = {"type": "object"}
        assert _get_python_type(schema, {}) == "dict"

    def test_null_type(self):
        schema = {"type": "null"}
        assert _get_python_type(schema, {}) == "None"

    def test_array_type_simple(self):
        schema = {"type": "array", "items": {"type": "string"}}
        assert _get_python_type(schema, {}) == "List[str]"

    def test_array_type_with_ref(self):
        schema = {"type": "array", "items": {"$ref": "#/components/schemas/User"}}
        assert _get_python_type(schema, {}) == "List[User]"

    def test_anyof_single_type(self):
        schema = {
            "anyOf": [
                {"type": "string"},
                {"type": "null"},
            ]
        }
        assert _get_python_type(schema, {}) == "Optional[str]"

    def test_anyof_multiple_types(self):
        schema = {
            "anyOf": [
                {"type": "string"},
                {"type": "integer"},
                {"type": "null"},
            ]
        }
        assert _get_python_type(schema, {}) == "Optional[Union[str, int]]"

    def test_anyof_with_ref(self):
        schema = {
            "anyOf": [
                {"$ref": "#/components/schemas/Status"},
                {"type": "null"},
            ]
        }
        assert _get_python_type(schema, {}) == "Optional[Status]"

    def test_allof_with_ref(self):
        schema = {
            "allOf": [
                {"$ref": "#/components/schemas/BaseModel"},
                {"type": "object", "properties": {"extra": {"type": "string"}}},
            ]
        }
        assert _get_python_type(schema, {}) == "BaseModel"

    def test_allof_without_ref(self):
        schema = {
            "allOf": [
                {"type": "object", "properties": {"a": {"type": "string"}}},
                {"type": "object", "properties": {"b": {"type": "string"}}},
            ]
        }
        assert _get_python_type(schema, {}) == "dict"

    def test_oneof_single(self):
        schema = {
            "oneOf": [
                {"$ref": "#/components/schemas/User"},
            ]
        }
        assert _get_python_type(schema, {}) == "User"

    def test_oneof_multiple(self):
        schema = {
            "oneOf": [
                {"$ref": "#/components/schemas/User"},
                {"$ref": "#/components/schemas/Admin"},
            ]
        }
        assert _get_python_type(schema, {}) == "Union[User, Admin]"

    def test_unknown_type(self):
        schema = {"type": "unknown"}
        assert _get_python_type(schema, {}) == "Any"

    def test_no_type(self):
        schema = {}
        assert _get_python_type(schema, {}) == "Any"


class TestGetResponseType:
    def test_success_response_with_schema(self):
        responses = {
            "200": {
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/User"}
                    }
                }
            }
        }
        assert _get_response_type(responses, {}) == "User"

    def test_success_response_array(self):
        responses = {
            "200": {
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "array",
                            "items": {"$ref": "#/components/schemas/User"},
                        }
                    }
                }
            }
        }
        assert _get_response_type(responses, {}) == "List[User]"

    def test_no_200_response(self):
        responses = {
            "201": {"content": {"application/json": {"schema": {"type": "object"}}}}
        }
        assert _get_response_type(responses, {}) == "Any"

    def test_no_content(self):
        responses = {"200": {"description": "Success"}}
        assert _get_response_type(responses, {}) == "Any"

    def test_no_json_content(self):
        responses = {"200": {"content": {"text/plain": {"schema": {"type": "string"}}}}}
        assert _get_response_type(responses, {}) == "Any"

    def test_empty_schema(self):
        responses = {"200": {"content": {"application/json": {"schema": {}}}}}
        assert _get_response_type(responses, {}) == "Any"


class TestParseOperation:
    def test_simple_get_operation(self):
        operation = {
            "operationId": "get_users_api_v1_users__get",
            "summary": "Get Users",
            "responses": {
                "200": {
                    "content": {
                        "application/json": {
                            "schema": {"type": "array", "items": {"$ref": "#/components/schemas/User"}}
                        }
                    }
                }
            },
        }

        result = _parse_operation("/api/v1/users/", "get", operation, {})

        assert result.operation_id == "get_users_api_v1_users__get"
        assert result.path == "/api/v1/users/"
        assert result.method == "get"
        assert result.summary == "Get Users"
        assert result.response_type == "List[User]"
        assert len(result.parameters) == 0

    def test_operation_with_query_params(self):
        operation = {
            "operationId": "search_users",
            "parameters": [
                {
                    "name": "search",
                    "in": "query",
                    "required": False,
                    "schema": {"type": "string"},
                },
                {
                    "name": "limit",
                    "in": "query",
                    "required": False,
                    "schema": {"type": "integer"},
                },
            ],
            "responses": {"200": {}},
        }

        result = _parse_operation("/users/", "get", operation, {})

        assert len(result.parameters) == 2
        assert result.parameters[0].name == "search"
        assert result.parameters[0].python_type == "Optional[str]"
        assert result.parameters[0].required is False
        assert result.parameters[1].name == "limit"
        assert result.parameters[1].python_type == "Optional[int]"

    def test_operation_with_path_params(self):
        operation = {
            "operationId": "get_user",
            "parameters": [
                {
                    "name": "user_id",
                    "in": "path",
                    "required": True,
                    "schema": {"type": "integer"},
                },
            ],
            "responses": {"200": {}},
        }

        result = _parse_operation("/users/{user_id}", "get", operation, {})

        assert len(result.parameters) == 1
        assert result.parameters[0].name == "user_id"
        assert result.parameters[0].in_ == "path"
        assert result.parameters[0].required is True
        assert result.parameters[0].python_type == "int"

    def test_operation_with_request_body(self):
        operation = {
            "operationId": "create_user",
            "requestBody": {
                "required": True,
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/UserCreate"}
                    }
                },
            },
            "responses": {"200": {}},
        }

        result = _parse_operation("/users/", "post", operation, {})

        assert result.request_body_type == "UserCreate"

    def test_operation_with_anyof_param(self):
        operation = {
            "operationId": "get_items",
            "parameters": [
                {
                    "name": "status",
                    "in": "query",
                    "required": False,
                    "schema": {
                        "anyOf": [
                            {"$ref": "#/components/schemas/StatusEnum"},
                            {"type": "null"},
                        ]
                    },
                },
            ],
            "responses": {"200": {}},
        }

        result = _parse_operation("/items/", "get", operation, {})

        assert result.parameters[0].python_type == "Optional[StatusEnum]"


class TestParseOpenapi:
    @pytest.fixture
    def minimal_spec(self):
        return {
            "openapi": "3.0.0",
            "info": {"title": "Test API", "version": "1.0.0"},
            "paths": {},
        }

    @pytest.fixture
    def spec_with_operations(self):
        return {
            "openapi": "3.0.0",
            "info": {"title": "User API", "version": "2.0.0"},
            "paths": {
                "/users/": {
                    "get": {
                        "operationId": "list_users",
                        "responses": {"200": {}},
                    },
                    "post": {
                        "operationId": "create_user",
                        "responses": {"200": {}},
                    },
                },
                "/users/{id}": {
                    "get": {
                        "operationId": "get_user",
                        "parameters": [
                            {"name": "id", "in": "path", "required": True, "schema": {"type": "integer"}}
                        ],
                        "responses": {"200": {}},
                    },
                },
            },
            "components": {
                "schemas": {
                    "User": {"type": "object"},
                    "UserCreate": {"type": "object"},
                }
            },
        }

    def _write_spec(self, spec: dict) -> Path:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(spec, f)
            return Path(f.name)

    def test_minimal_spec(self, minimal_spec):
        path = self._write_spec(minimal_spec)
        try:
            result = parse_openapi(path)

            assert result.title == "Test API"
            assert result.version == "1.0.0"
            assert len(result.operations) == 0
            assert len(result.schema_names) == 0
        finally:
            path.unlink()

    def test_spec_with_operations(self, spec_with_operations):
        path = self._write_spec(spec_with_operations)
        try:
            result = parse_openapi(path)

            assert result.title == "User API"
            assert result.version == "2.0.0"
            assert len(result.operations) == 3
            assert len(result.schema_names) == 2
            assert "User" in result.schema_names
            assert "UserCreate" in result.schema_names
        finally:
            path.unlink()

    def test_function_name_collision_handling(self):
        spec = {
            "openapi": "3.0.0",
            "info": {"title": "API", "version": "1.0.0"},
            "paths": {
                "/v1/users/": {
                    "get": {
                        "operationId": "get_users_api_v1_users__get",
                        "responses": {"200": {}},
                    },
                },
                "/v2/users/": {
                    "get": {
                        "operationId": "get_users_api_v2_users__get",
                        "responses": {"200": {}},
                    },
                },
            },
        }

        path = self._write_spec(spec)
        try:
            result = parse_openapi(path)

            function_names = [op.function_name for op in result.operations]
            assert len(function_names) == len(set(function_names))
            assert "get_users" in function_names
            assert "get_users_1" in function_names
        finally:
            path.unlink()

    def test_all_http_methods_parsed(self):
        spec = {
            "openapi": "3.0.0",
            "info": {"title": "API", "version": "1.0.0"},
            "paths": {
                "/resource/": {
                    "get": {"operationId": "get_resource", "responses": {"200": {}}},
                    "post": {"operationId": "create_resource", "responses": {"200": {}}},
                    "put": {"operationId": "update_resource", "responses": {"200": {}}},
                    "delete": {"operationId": "delete_resource", "responses": {"200": {}}},
                    "patch": {"operationId": "patch_resource", "responses": {"200": {}}},
                },
            },
        }

        path = self._write_spec(spec)
        try:
            result = parse_openapi(path)

            methods = {op.method for op in result.operations}
            assert methods == {"get", "post", "put", "delete", "patch"}
        finally:
            path.unlink()

    def test_reserved_word_in_param(self):
        spec = {
            "openapi": "3.0.0",
            "info": {"title": "API", "version": "1.0.0"},
            "paths": {
                "/items/": {
                    "get": {
                        "operationId": "get_items",
                        "parameters": [
                            {"name": "id", "in": "query", "schema": {"type": "integer"}},
                            {"name": "type", "in": "query", "schema": {"type": "string"}},
                            {"name": "class", "in": "query", "schema": {"type": "string"}},
                        ],
                        "responses": {"200": {}},
                    },
                },
            },
        }

        path = self._write_spec(spec)
        try:
            result = parse_openapi(path)

            op = result.operations[0]
            param_names = [p.name for p in op.parameters]
            assert "id" in param_names
            assert "type" in param_names
            assert "class" in param_names

            safe_names = [p.safe_name for p in op.parameters]
            assert "id_" in safe_names
            assert "type_" in safe_names
            assert "class_" in safe_names
        finally:
            path.unlink()
