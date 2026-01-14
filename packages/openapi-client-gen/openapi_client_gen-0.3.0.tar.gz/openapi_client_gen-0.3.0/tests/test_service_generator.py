import tempfile
from pathlib import Path

from openapi_client_gen.generators.service import _get_schema_imports, generate_service
from openapi_client_gen.models import Operation, Parameter, ParsedSpec


class TestGetSchemaImports:
    def test_empty_operations(self):
        assert _get_schema_imports([]) == []

    def test_basic_types_not_imported(self):
        ops = [
            Operation(
                operation_id="get_item",
                path="/items",
                method="get",
                response_type="Any",
            ),
            Operation(
                operation_id="get_count",
                path="/count",
                method="get",
                response_type="int",
            ),
        ]
        assert _get_schema_imports(ops) == []

    def test_schema_from_response_type(self):
        ops = [
            Operation(
                operation_id="get_user",
                path="/users/{id}",
                method="get",
                response_type="User",
            ),
        ]
        assert "User" in _get_schema_imports(ops)

    def test_schema_from_request_body(self):
        ops = [
            Operation(
                operation_id="create_user",
                path="/users",
                method="post",
                request_body_type="UserCreate",
                response_type="User",
            ),
        ]
        imports = _get_schema_imports(ops)
        assert "User" in imports
        assert "UserCreate" in imports

    def test_list_response_extracts_inner_type(self):
        ops = [
            Operation(
                operation_id="get_users",
                path="/users",
                method="get",
                response_type="List[User]",
            ),
        ]
        imports = _get_schema_imports(ops)
        assert "User" in imports
        assert "List[User]" not in imports

    def test_imports_sorted(self):
        ops = [
            Operation(
                operation_id="op1", path="/", method="get", response_type="Zebra"
            ),
            Operation(
                operation_id="op2", path="/", method="get", response_type="Apple"
            ),
            Operation(
                operation_id="op3", path="/", method="get", response_type="Mango"
            ),
        ]
        imports = _get_schema_imports(ops)
        assert imports == ["Apple", "Mango", "Zebra"]

    def test_no_duplicates(self):
        ops = [
            Operation(operation_id="op1", path="/", method="get", response_type="User"),
            Operation(
                operation_id="op2", path="/", method="post", request_body_type="User"
            ),
        ]
        imports = _get_schema_imports(ops)
        assert imports.count("User") == 1


class TestGenerateService:
    def _generate_and_read(self, spec: ParsedSpec) -> str:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            output_path = Path(f.name)

        try:
            generate_service(spec, output_path)
            return output_path.read_text()
        finally:
            output_path.unlink()

    def test_empty_spec(self):
        spec = ParsedSpec(title="Empty API", version="1.0.0")
        content = self._generate_and_read(spec)

        assert "class WebService(ExternalService):" in content
        assert "from external_service import ExternalService, HTTPResponse" in content

    def test_simple_get_operation(self):
        spec = ParsedSpec(
            title="API",
            version="1.0.0",
            operations=[
                Operation(
                    operation_id="get_users",
                    path="/users/",
                    method="get",
                    summary="Get all users",
                    response_type="List[User]",
                )
            ],
        )
        content = self._generate_and_read(spec)

        assert "async def get_users(" in content
        assert '"""Get all users"""' in content
        assert 'await self.get("/users/"' in content

    def test_get_with_query_params(self):
        spec = ParsedSpec(
            title="API",
            version="1.0.0",
            operations=[
                Operation(
                    operation_id="search_users",
                    path="/users/",
                    method="get",
                    response_type="List[User]",
                    parameters=[
                        Parameter(
                            name="search", python_type="Optional[str]", in_="query"
                        ),
                        Parameter(
                            name="limit", python_type="Optional[int]", in_="query"
                        ),
                    ],
                )
            ],
        )
        content = self._generate_and_read(spec)

        assert "search: Optional[str] = None" in content
        assert "limit: Optional[int] = None" in content
        assert "_filter_params({" in content
        assert '"search": search' in content
        assert '"limit": limit' in content
        assert "params=params" in content

    def test_get_with_path_params(self):
        spec = ParsedSpec(
            title="API",
            version="1.0.0",
            operations=[
                Operation(
                    operation_id="get_user",
                    path="/users/{user_id}/",
                    method="get",
                    response_type="User",
                    parameters=[
                        Parameter(
                            name="user_id", python_type="int", required=True, in_="path"
                        ),
                    ],
                )
            ],
        )
        content = self._generate_and_read(spec)

        assert "user_id: int" in content
        assert 'f"/users/{user_id}/"' in content

    def test_post_with_body(self):
        spec = ParsedSpec(
            title="API",
            version="1.0.0",
            operations=[
                Operation(
                    operation_id="create_user",
                    path="/users/",
                    method="post",
                    request_body_type="UserCreate",
                    response_type="User",
                )
            ],
        )
        content = self._generate_and_read(spec)

        assert "body: UserCreate" in content
        assert 'await self.post("/users/"' in content
        assert 'json=body.model_dump(mode="json")' in content

    def test_put_with_body(self):
        spec = ParsedSpec(
            title="API",
            version="1.0.0",
            operations=[
                Operation(
                    operation_id="update_user",
                    path="/users/{user_id}/",
                    method="put",
                    request_body_type="UserUpdate",
                    response_type="User",
                    parameters=[
                        Parameter(
                            name="user_id", python_type="int", required=True, in_="path"
                        ),
                    ],
                )
            ],
        )
        content = self._generate_and_read(spec)

        assert "body: UserUpdate" in content
        assert 'await self.put(f"/users/{user_id}/"' in content
        assert "exclude_unset=True" in content

    def test_delete_operation(self):
        spec = ParsedSpec(
            title="API",
            version="1.0.0",
            operations=[
                Operation(
                    operation_id="delete_user",
                    path="/users/{user_id}/",
                    method="delete",
                    response_type="Any",
                    parameters=[
                        Parameter(
                            name="user_id", python_type="int", required=True, in_="path"
                        ),
                    ],
                )
            ],
        )
        content = self._generate_and_read(spec)

        assert "async def delete_user(" in content
        assert "await self.delete(" in content

    def test_patch_with_body(self):
        spec = ParsedSpec(
            title="API",
            version="1.0.0",
            operations=[
                Operation(
                    operation_id="patch_user",
                    path="/users/{user_id}/",
                    method="patch",
                    request_body_type="UserPatch",
                    response_type="User",
                    parameters=[
                        Parameter(
                            name="user_id", python_type="int", required=True, in_="path"
                        ),
                    ],
                )
            ],
        )
        content = self._generate_and_read(spec)

        assert "await self.patch(" in content
        assert "exclude_unset=True" in content

    def test_reserved_word_in_path_param(self):
        spec = ParsedSpec(
            title="API",
            version="1.0.0",
            operations=[
                Operation(
                    operation_id="get_item",
                    path="/items/{id}/",
                    method="get",
                    response_type="Item",
                    parameters=[
                        Parameter(
                            name="id", python_type="int", required=True, in_="path"
                        ),
                    ],
                )
            ],
        )
        content = self._generate_and_read(spec)

        assert "id_: int" in content
        assert 'f"/items/{id_}/"' in content

    def test_reserved_word_in_query_param(self):
        spec = ParsedSpec(
            title="API",
            version="1.0.0",
            operations=[
                Operation(
                    operation_id="get_items",
                    path="/items/",
                    method="get",
                    response_type="List[Item]",
                    parameters=[
                        Parameter(
                            name="type", python_type="Optional[str]", in_="query"
                        ),
                    ],
                )
            ],
        )
        content = self._generate_and_read(spec)

        assert "type_: Optional[str]" in content
        assert '"type": type_' in content

    def test_filter_params_method_included(self):
        spec = ParsedSpec(title="API", version="1.0.0")
        content = self._generate_and_read(spec)

        assert "@staticmethod" in content
        assert "def _filter_params(params: dict[str, Any])" in content
        assert "isinstance(v, bool)" in content
        assert "isinstance(v, Iterable)" in content
        assert "isinstance(v, datetime)" in content
        assert "isinstance(v, Enum)" in content

    def test_imports_generated(self):
        spec = ParsedSpec(
            title="API",
            version="1.0.0",
            operations=[
                Operation(
                    operation_id="get_user",
                    path="/users/{id}",
                    method="get",
                    response_type="User",
                    request_body_type="UserQuery",
                    parameters=[
                        Parameter(
                            name="id", python_type="int", required=True, in_="path"
                        ),
                    ],
                )
            ],
        )
        content = self._generate_and_read(spec)

        assert "from datetime import datetime" in content
        assert "from enum import Enum" in content
        assert "from typing import Any, Iterable, List, Optional" in content
        assert "from external_service import ExternalService, HTTPResponse" in content
        assert "from .schemas import (" in content
        assert "User," in content
        assert "UserQuery," in content

    def test_multiple_operations(self):
        spec = ParsedSpec(
            title="API",
            version="1.0.0",
            operations=[
                Operation(
                    operation_id="list_users",
                    path="/users/",
                    method="get",
                    response_type="List[User]",
                ),
                Operation(
                    operation_id="create_user",
                    path="/users/",
                    method="post",
                    request_body_type="UserCreate",
                    response_type="User",
                ),
                Operation(
                    operation_id="get_user",
                    path="/users/{id}",
                    method="get",
                    response_type="User",
                    parameters=[
                        Parameter(
                            name="id", python_type="int", required=True, in_="path"
                        )
                    ],
                ),
                Operation(
                    operation_id="delete_user",
                    path="/users/{id}",
                    method="delete",
                    response_type="Any",
                    parameters=[
                        Parameter(
                            name="id", python_type="int", required=True, in_="path"
                        )
                    ],
                ),
            ],
        )
        content = self._generate_and_read(spec)

        assert "async def list_users(" in content
        assert "async def create_user(" in content
        assert "async def get_user(" in content
        assert "async def delete_user(" in content

    def test_post_without_body(self):
        spec = ParsedSpec(
            title="API",
            version="1.0.0",
            operations=[
                Operation(
                    operation_id="trigger_action",
                    path="/actions/{id}/trigger/",
                    method="post",
                    response_type="Any",
                    parameters=[
                        Parameter(
                            name="id", python_type="int", required=True, in_="path"
                        ),
                    ],
                )
            ],
        )
        content = self._generate_and_read(spec)

        assert "async def trigger_action(" in content
        assert "await self.post(" in content
        assert "json=body" not in content
