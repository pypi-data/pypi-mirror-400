import json
import tempfile
from pathlib import Path

import pytest
from openapi_client_gen.generators.schemas import (
    _clean_schema_name,
    _generate_basic_schemas,
    _safe_enum_member,
    generate_schemas,
)


class TestSafeEnumMember:
    def test_basic_conversion(self):
        existing: set[str] = set()
        assert _safe_enum_member("NEW", existing) == "new"
        assert _safe_enum_member("IN_PROGRESS", existing) == "in_progress"

    def test_collision_handling(self):
        existing: set[str] = set()
        assert _safe_enum_member("STATUS", existing) == "status"
        assert _safe_enum_member("status", existing) == "status_1"
        assert _safe_enum_member("Status", existing) == "status_2"

    def test_reserved_word(self):
        existing: set[str] = set()
        assert _safe_enum_member("class", existing) == "class_"
        assert _safe_enum_member("type", existing) == "type_"

    def test_numeric_start(self):
        existing: set[str] = set()
        assert _safe_enum_member("1st", existing) == "value_1st"


class TestCleanSchemaName:
    def test_simple_name(self):
        assert _clean_schema_name("User") == "User"

    def test_generic_with_underscores(self):
        assert _clean_schema_name("ResponseList_User_") == "ResponseListUser"
        assert _clean_schema_name("Page_Item_") == "PageItem"

    def test_hyphenated_names(self):
        assert _clean_schema_name("Schema-Input") == "SchemaInput"
        assert (
            _clean_schema_name("RouteScheduleSchema-Input")
            == "RouteScheduleSchemaInput"
        )
        assert (
            _clean_schema_name("RouteScheduleSchema-Output")
            == "RouteScheduleSchemaOutput"
        )

    def test_combined_hyphen_and_underscore(self):
        assert _clean_schema_name("Response_List-Item_") == "ResponseListItem"


class TestGenerateBasicSchemas:
    @pytest.fixture
    def simple_spec(self):
        return {
            "components": {
                "schemas": {
                    "StatusEnum": {
                        "type": "string",
                        "enum": ["NEW", "IN_PROGRESS", "DONE"],
                    },
                    "User": {
                        "type": "object",
                        "required": ["name"],
                        "properties": {
                            "name": {"type": "string", "description": "User name"},
                            "age": {"type": "integer"},
                        },
                    },
                }
            }
        }

    @pytest.fixture
    def spec_with_colliding_enums(self):
        return {
            "components": {
                "schemas": {
                    "StatusEnum": {
                        "type": "string",
                        "enum": ["NEW", "new", "New"],
                    },
                }
            }
        }

    @pytest.fixture
    def spec_with_reserved_enum(self):
        return {
            "components": {
                "schemas": {
                    "KeywordEnum": {
                        "type": "string",
                        "enum": ["class", "type", "import"],
                    },
                }
            }
        }

    @pytest.fixture
    def spec_with_datetime(self):
        return {
            "components": {
                "schemas": {
                    "Event": {
                        "type": "object",
                        "properties": {
                            "created_at": {"type": "string", "format": "date-time"},
                        },
                    },
                }
            }
        }

    @pytest.fixture
    def spec_with_ref(self):
        return {
            "components": {
                "schemas": {
                    "StatusEnum": {
                        "type": "string",
                        "enum": ["active", "inactive"],
                    },
                    "User": {
                        "type": "object",
                        "properties": {
                            "status": {"$ref": "#/components/schemas/StatusEnum"},
                        },
                    },
                }
            }
        }

    @pytest.fixture
    def spec_with_anyof(self):
        return {
            "components": {
                "schemas": {
                    "User": {
                        "type": "object",
                        "properties": {
                            "nickname": {
                                "anyOf": [{"type": "string"}, {"type": "null"}]
                            },
                        },
                    },
                }
            }
        }

    @pytest.fixture
    def spec_with_array(self):
        return {
            "components": {
                "schemas": {
                    "Team": {
                        "type": "object",
                        "properties": {
                            "members": {
                                "type": "array",
                                "items": {"type": "string"},
                            },
                        },
                    },
                }
            }
        }

    def _write_and_generate(self, spec: dict) -> str:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(spec, f)
            spec_path = Path(f.name)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            output_path = Path(f.name)

        try:
            _generate_basic_schemas(spec_path, output_path)
            return output_path.read_text()
        finally:
            spec_path.unlink()
            output_path.unlink()

    def test_enum_generation(self, simple_spec):
        content = self._write_and_generate(simple_spec)

        assert "class StatusEnum(Enum):" in content
        assert 'new = "new"' in content
        assert 'in_progress = "in_progress"' in content
        assert 'done = "done"' in content

    def test_model_generation(self, simple_spec):
        content = self._write_and_generate(simple_spec)

        assert "class User(BaseModel):" in content
        assert "name: str" in content
        assert 'description="User name"' in content

    def test_enum_collision_handling(self, spec_with_colliding_enums):
        content = self._write_and_generate(spec_with_colliding_enums)

        assert "class StatusEnum(Enum):" in content
        assert 'new = "new"' in content
        assert 'new_1 = "new"' in content
        assert 'new_2 = "new"' in content

    def test_reserved_word_in_enum(self, spec_with_reserved_enum):
        content = self._write_and_generate(spec_with_reserved_enum)

        assert "class KeywordEnum(Enum):" in content
        assert 'class_ = "class"' in content
        assert 'type_ = "type"' in content
        assert 'import_ = "import"' in content

    def test_datetime_field(self, spec_with_datetime):
        content = self._write_and_generate(spec_with_datetime)

        assert "from datetime import datetime" in content
        assert "created_at:" in content
        assert "datetime" in content

    def test_ref_field(self, spec_with_ref):
        content = self._write_and_generate(spec_with_ref)

        assert "status: StatusEnum" in content

    def test_anyof_nullable_field(self, spec_with_anyof):
        content = self._write_and_generate(spec_with_anyof)

        assert "nickname: Optional[str]" in content

    def test_array_field(self, spec_with_array):
        content = self._write_and_generate(spec_with_array)

        assert "List" in content
        assert "members: List[str]" in content

    def test_imports_present(self, simple_spec):
        content = self._write_and_generate(simple_spec)

        assert "from datetime import datetime" in content
        assert "from enum import Enum" in content
        assert "from typing import" in content
        assert "from pydantic import BaseModel, Field" in content

    def test_empty_model(self):
        spec = {
            "components": {
                "schemas": {
                    "Empty": {"type": "object", "properties": {}},
                }
            }
        }
        content = self._write_and_generate(spec)

        assert "class Empty(BaseModel):" in content
        assert "pass" in content


class TestGenerateSchemas:
    @pytest.fixture
    def simple_spec(self):
        return {
            "openapi": "3.0.0",
            "info": {"title": "API", "version": "1.0.0"},
            "components": {
                "schemas": {
                    "StatusEnum": {
                        "type": "string",
                        "enum": ["ACTIVE", "INACTIVE"],
                    },
                }
            },
        }

    def test_generate_with_fallback(self, simple_spec):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(simple_spec, f)
            spec_path = Path(f.name)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            output_path = Path(f.name)

        try:
            generate_schemas(spec_path, output_path, lowercase_enums=True)

            content = output_path.read_text()
            assert "class StatusEnum" in content
            assert "Enum" in content
        finally:
            spec_path.unlink()
            output_path.unlink()
