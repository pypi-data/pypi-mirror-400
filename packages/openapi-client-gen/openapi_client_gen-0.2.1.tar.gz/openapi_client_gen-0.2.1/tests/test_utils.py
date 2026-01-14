import pytest

from openapi_client_gen.utils import (
    PYTHON_RESERVED,
    safe_enum_member,
    safe_function_name,
    safe_name,
)


class TestSafeName:
    def test_normal_name_unchanged(self):
        assert safe_name("user_id") == "user_id"
        assert safe_name("mission_status") == "mission_status"
        assert safe_name("get_users") == "get_users"

    def test_python_keywords_get_suffix(self):
        assert safe_name("class") == "class_"
        assert safe_name("def") == "def_"
        assert safe_name("return") == "return_"
        assert safe_name("import") == "import_"
        assert safe_name("from") == "from_"
        assert safe_name("for") == "for_"
        assert safe_name("while") == "while_"
        assert safe_name("if") == "if_"
        assert safe_name("else") == "else_"
        assert safe_name("try") == "try_"
        assert safe_name("except") == "except_"
        assert safe_name("finally") == "finally_"
        assert safe_name("with") == "with_"
        assert safe_name("as") == "as_"
        assert safe_name("pass") == "pass_"
        assert safe_name("break") == "break_"
        assert safe_name("continue") == "continue_"
        assert safe_name("lambda") == "lambda_"
        assert safe_name("yield") == "yield_"
        assert safe_name("raise") == "raise_"
        assert safe_name("global") == "global_"
        assert safe_name("nonlocal") == "nonlocal_"
        assert safe_name("assert") == "assert_"
        assert safe_name("del") == "del_"
        assert safe_name("in") == "in_"
        assert safe_name("is") == "is_"
        assert safe_name("not") == "not_"
        assert safe_name("and") == "and_"
        assert safe_name("or") == "or_"

    def test_builtin_shadows_get_suffix(self):
        assert safe_name("type") == "type_"
        assert safe_name("id") == "id_"
        assert safe_name("list") == "list_"
        assert safe_name("dict") == "dict_"
        assert safe_name("set") == "set_"
        assert safe_name("str") == "str_"
        assert safe_name("int") == "int_"
        assert safe_name("float") == "float_"
        assert safe_name("bool") == "bool_"

    def test_constants_get_suffix(self):
        assert safe_name("True") == "True_"
        assert safe_name("False") == "False_"
        assert safe_name("None") == "None_"

    def test_custom_suffix(self):
        assert safe_name("class", suffix="_field") == "class_field"
        assert safe_name("type", suffix="_param") == "type_param"


class TestSafeEnumMember:
    def test_lowercase_conversion(self):
        existing: set[str] = set()
        assert safe_enum_member("NEW", existing) == "new"
        assert safe_enum_member("IN_PROGRESS", existing) == "in_progress"
        assert safe_enum_member("DONE", existing) == "done"

    def test_special_chars_replaced(self):
        existing: set[str] = set()
        assert safe_enum_member("in-progress", existing) == "in_progress"
        assert safe_enum_member("user.status", existing) == "user_status"
        assert safe_enum_member("value@1", existing) == "value_1"
        assert safe_enum_member("test!name", existing) == "test_name"

    def test_numeric_prefix_handled(self):
        existing: set[str] = set()
        assert safe_enum_member("123", existing) == "value_123"
        assert safe_enum_member("1st", existing) == "value_1st"
        assert safe_enum_member("2nd_place", existing) == "value_2nd_place"

    def test_empty_value_handled(self):
        existing: set[str] = set()
        assert safe_enum_member("", existing) == "empty"
        assert safe_enum_member("   ", existing) == "___"

    def test_reserved_words_get_suffix(self):
        existing: set[str] = set()
        assert safe_enum_member("class", existing) == "class_"
        assert safe_enum_member("TYPE", existing) == "type_"
        assert safe_enum_member("None", existing) == "none"

    def test_collision_detection(self):
        existing: set[str] = set()

        result1 = safe_enum_member("NEW", existing)
        assert result1 == "new"
        assert "new" in existing

        result2 = safe_enum_member("new", existing)
        assert result2 == "new_1"
        assert "new_1" in existing

        result3 = safe_enum_member("New", existing)
        assert result3 == "new_2"
        assert "new_2" in existing

    def test_collision_with_reserved_word(self):
        existing: set[str] = set()

        result1 = safe_enum_member("class", existing)
        assert result1 == "class_"
        assert "class" in existing

        result2 = safe_enum_member("CLASS", existing)
        assert result2 == "class_1"

    def test_multiple_collisions(self):
        existing: set[str] = set()

        results = []
        for _ in range(5):
            results.append(safe_enum_member("STATUS", existing))

        assert results == ["status", "status_1", "status_2", "status_3", "status_4"]


class TestSafeFunctionName:
    def test_normal_name_unchanged(self):
        assert safe_function_name("get_users") == "get_users"
        assert safe_function_name("create_mission") == "create_mission"

    def test_invalid_chars_replaced(self):
        assert safe_function_name("get-users") == "get_users"
        assert safe_function_name("get.users") == "get_users"
        assert safe_function_name("get@users") == "get_users"

    def test_consecutive_underscores_collapsed(self):
        assert safe_function_name("get__users") == "get_users"
        assert safe_function_name("get___users") == "get_users"

    def test_leading_trailing_underscores_removed(self):
        assert safe_function_name("_get_users") == "get_users"
        assert safe_function_name("get_users_") == "get_users"
        assert safe_function_name("_get_users_") == "get_users"

    def test_uppercase_converted(self):
        assert safe_function_name("GetUsers") == "getusers"
        assert safe_function_name("GET_USERS") == "get_users"

    def test_reserved_words_get_suffix(self):
        assert safe_function_name("class") == "class_"
        assert safe_function_name("import") == "import_"

    def test_empty_becomes_operation(self):
        assert safe_function_name("") == "operation"
        assert safe_function_name("___") == "operation"

    def test_collision_detection(self):
        existing: set[str] = set()

        result1 = safe_function_name("get_users", existing)
        assert result1 == "get_users"

        result2 = safe_function_name("get_users", existing)
        assert result2 == "get_users_1"

        result3 = safe_function_name("get_users", existing)
        assert result3 == "get_users_2"

    def test_collision_with_similar_names(self):
        existing: set[str] = set()

        result1 = safe_function_name("get_user", existing)
        result2 = safe_function_name("get_users", existing)

        assert result1 == "get_user"
        assert result2 == "get_users"

    def test_no_collision_tracking_when_none(self):
        result1 = safe_function_name("get_users", None)
        result2 = safe_function_name("get_users", None)

        assert result1 == "get_users"
        assert result2 == "get_users"


class TestPythonReserved:
    def test_contains_all_keywords(self):
        import keyword

        for kw in keyword.kwlist:
            assert kw in PYTHON_RESERVED, f"Missing keyword: {kw}"

    def test_contains_common_builtins(self):
        builtins = ["type", "id", "list", "dict", "set", "str", "int", "float", "bool"]
        for b in builtins:
            assert b in PYTHON_RESERVED, f"Missing builtin: {b}"

    def test_contains_constants(self):
        assert "True" in PYTHON_RESERVED
        assert "False" in PYTHON_RESERVED
        assert "None" in PYTHON_RESERVED
