from openapi_client_gen.models import Operation, Parameter, ParsedSpec


class TestParameter:
    def test_basic_parameter(self):
        param = Parameter(name="user_id", python_type="int", required=True)

        assert param.name == "user_id"
        assert param.python_type == "int"
        assert param.required is True
        assert param.in_ == "query"
        assert param.description is None

    def test_parameter_with_all_fields(self):
        param = Parameter(
            name="mission_id",
            python_type="int",
            required=True,
            in_="path",
            description="Mission identifier",
        )

        assert param.name == "mission_id"
        assert param.in_ == "path"
        assert param.description == "Mission identifier"

    def test_safe_name_normal(self):
        param = Parameter(name="user_id", python_type="int")
        assert param.safe_name == "user_id"

    def test_safe_name_reserved_word(self):
        param = Parameter(name="id", python_type="int")
        assert param.safe_name == "id_"

        param2 = Parameter(name="type", python_type="str")
        assert param2.safe_name == "type_"

        param3 = Parameter(name="class", python_type="str")
        assert param3.safe_name == "class_"

    def test_signature_required(self):
        param = Parameter(name="user_id", python_type="int", required=True)
        assert param.signature == "user_id: int"

    def test_signature_optional(self):
        param = Parameter(name="user_id", python_type="Optional[int]", required=False)
        assert param.signature == "user_id: Optional[int] = None"

    def test_signature_with_reserved_name(self):
        param = Parameter(name="id", python_type="int", required=True)
        assert param.signature == "id_: int"

        param2 = Parameter(name="type", python_type="Optional[str]", required=False)
        assert param2.signature == "type_: Optional[str] = None"


class TestOperation:
    def test_basic_operation(self):
        op = Operation(
            operation_id="get_users_api_v1_users__get",
            path="/api/v1/users/",
            method="get",
        )

        assert op.operation_id == "get_users_api_v1_users__get"
        assert op.path == "/api/v1/users/"
        assert op.method == "get"
        assert op.summary is None
        assert op.parameters == []
        assert op.request_body_type is None
        assert op.response_type == "Any"

    def test_function_name_removes_api_suffix(self):
        op = Operation(
            operation_id="get_users_api_v1_users__get",
            path="/api/v1/users/",
            method="get",
        )
        assert op.function_name == "get_users"

    def test_function_name_removes_method_suffix(self):
        test_cases = [
            ("create_user__post", "create_user"),
            ("update_user__put", "update_user"),
            ("delete_user__delete", "delete_user"),
            ("patch_user__patch", "patch_user"),
        ]

        for operation_id, expected in test_cases:
            op = Operation(operation_id=operation_id, path="/", method="post")
            assert op.function_name == expected, f"Failed for {operation_id}"

    def test_function_name_override(self):
        op = Operation(
            operation_id="get_users_api_v1_users__get",
            path="/api/v1/users/",
            method="get",
            function_name_override="list_all_users",
        )
        assert op.function_name == "list_all_users"

    def test_path_params(self):
        op = Operation(
            operation_id="get_user",
            path="/users/{user_id}",
            method="get",
            parameters=[
                Parameter(name="user_id", python_type="int", in_="path"),
                Parameter(name="include_deleted", python_type="bool", in_="query"),
            ],
        )

        path_params = op.path_params
        assert len(path_params) == 1
        assert path_params[0].name == "user_id"

    def test_query_params(self):
        op = Operation(
            operation_id="get_users",
            path="/users/",
            method="get",
            parameters=[
                Parameter(name="user_id", python_type="int", in_="path"),
                Parameter(name="search", python_type="str", in_="query"),
                Parameter(name="limit", python_type="int", in_="query"),
            ],
        )

        query_params = op.query_params
        assert len(query_params) == 2
        names = {p.name for p in query_params}
        assert names == {"search", "limit"}

    def test_has_query_params(self):
        op_with = Operation(
            operation_id="get_users",
            path="/users/",
            method="get",
            parameters=[Parameter(name="search", python_type="str", in_="query")],
        )
        assert op_with.has_query_params is True

        op_without = Operation(
            operation_id="get_user",
            path="/users/{id}",
            method="get",
            parameters=[Parameter(name="id", python_type="int", in_="path")],
        )
        assert op_without.has_query_params is False

    def test_has_body(self):
        op_with = Operation(
            operation_id="create_user",
            path="/users/",
            method="post",
            request_body_type="UserCreate",
        )
        assert op_with.has_body is True

        op_without = Operation(
            operation_id="delete_user",
            path="/users/{id}",
            method="delete",
        )
        assert op_without.has_body is False

    def test_formatted_path_no_params(self):
        op = Operation(
            operation_id="get_users",
            path="/api/v1/users/",
            method="get",
        )
        assert op.formatted_path == '"/api/v1/users/"'

    def test_formatted_path_with_params(self):
        op = Operation(
            operation_id="get_user",
            path="/api/v1/users/{user_id}/",
            method="get",
            parameters=[Parameter(name="user_id", python_type="int", in_="path")],
        )
        assert op.formatted_path == 'f"/api/v1/users/{user_id}/"'

    def test_formatted_path_multiple_params(self):
        op = Operation(
            operation_id="get_user_post",
            path="/users/{user_id}/posts/{post_id}",
            method="get",
            parameters=[
                Parameter(name="user_id", python_type="int", in_="path"),
                Parameter(name="post_id", python_type="int", in_="path"),
            ],
        )
        assert op.formatted_path == 'f"/users/{user_id}/posts/{post_id}"'

    def test_formatted_path_with_reserved_name(self):
        op = Operation(
            operation_id="get_item",
            path="/items/{id}",
            method="get",
            parameters=[Parameter(name="id", python_type="int", in_="path")],
        )
        assert op.formatted_path == 'f"/items/{id_}"'


class TestParsedSpec:
    def test_basic_spec(self):
        spec = ParsedSpec(title="My API", version="1.0.0")

        assert spec.title == "My API"
        assert spec.version == "1.0.0"
        assert spec.operations == []
        assert spec.schema_names == []

    def test_spec_with_operations(self):
        ops = [
            Operation(operation_id="get_users", path="/users", method="get"),
            Operation(operation_id="create_user", path="/users", method="post"),
        ]

        spec = ParsedSpec(
            title="User API",
            version="2.0.0",
            operations=ops,
            schema_names=["User", "UserCreate"],
        )

        assert len(spec.operations) == 2
        assert len(spec.schema_names) == 2
        assert "User" in spec.schema_names
