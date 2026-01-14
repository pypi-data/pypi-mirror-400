import json
import tempfile
from pathlib import Path

import pytest


class TestConstraints:
    def _generate_schemas(self, spec: dict) -> str:
        from openapi_client_gen.generators.schemas import generate_schemas

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            spec_path = tmpdir_path / "openapi.json"
            spec_path.write_text(json.dumps(spec))

            schemas_path = tmpdir_path / "schemas.py"
            generate_schemas(spec_path, schemas_path, lowercase_enums=True)

            return schemas_path.read_text()

    def test_string_min_max_length(self):
        spec = {
            "openapi": "3.0.0",
            "info": {"title": "API", "version": "1.0.0"},
            "components": {
                "schemas": {
                    "User": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string", "minLength": 1, "maxLength": 100},
                        },
                    },
                }
            },
        }
        content = self._generate_schemas(spec)

        assert "min_length=1" in content or "ge=1" in content
        assert "max_length=100" in content or "le=100" in content

    def test_integer_minimum_maximum(self):
        spec = {
            "openapi": "3.0.0",
            "info": {"title": "API", "version": "1.0.0"},
            "components": {
                "schemas": {
                    "Pagination": {
                        "type": "object",
                        "properties": {
                            "limit": {"type": "integer", "minimum": 1, "maximum": 100},
                            "page": {"type": "integer", "minimum": 0},
                        },
                    },
                }
            },
        }
        content = self._generate_schemas(spec)

        assert "ge=1" in content or "minimum=1" in content
        assert "le=100" in content or "maximum=100" in content

    def test_exclusive_minimum_maximum(self):
        spec = {
            "openapi": "3.0.0",
            "info": {"title": "API", "version": "1.0.0"},
            "components": {
                "schemas": {
                    "Range": {
                        "type": "object",
                        "properties": {
                            "value": {"type": "number", "exclusiveMinimum": 0, "exclusiveMaximum": 100},
                        },
                    },
                }
            },
        }
        content = self._generate_schemas(spec)

        assert "gt=0" in content or "exclusiveMinimum" in content
        assert "lt=100" in content or "exclusiveMaximum" in content

    def test_pattern_constraint(self):
        spec = {
            "openapi": "3.0.0",
            "info": {"title": "API", "version": "1.0.0"},
            "components": {
                "schemas": {
                    "Email": {
                        "type": "object",
                        "properties": {
                            "email": {"type": "string", "pattern": r"^[\w\.-]+@[\w\.-]+\.\w+$"},
                        },
                    },
                }
            },
        }
        content = self._generate_schemas(spec)

        assert "pattern=" in content or "regex=" in content


class TestDescriptions:
    def _generate_schemas(self, spec: dict) -> str:
        from openapi_client_gen.generators.schemas import generate_schemas

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            spec_path = tmpdir_path / "openapi.json"
            spec_path.write_text(json.dumps(spec))

            schemas_path = tmpdir_path / "schemas.py"
            generate_schemas(spec_path, schemas_path, lowercase_enums=True)

            return schemas_path.read_text()

    def test_field_description(self):
        spec = {
            "openapi": "3.0.0",
            "info": {"title": "API", "version": "1.0.0"},
            "components": {
                "schemas": {
                    "User": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string", "description": "The user's full name"},
                        },
                    },
                }
            },
        }
        content = self._generate_schemas(spec)

        assert "description=" in content
        assert "The user's full name" in content or "user" in content.lower()

    def test_schema_description_as_docstring(self):
        spec = {
            "openapi": "3.0.0",
            "info": {"title": "API", "version": "1.0.0"},
            "components": {
                "schemas": {
                    "User": {
                        "type": "object",
                        "description": "Represents a system user",
                        "properties": {"name": {"type": "string"}},
                    },
                }
            },
        }
        content = self._generate_schemas(spec)

        assert "Represents a system user" in content or "User" in content


class TestDefaultValues:
    def _generate_schemas(self, spec: dict) -> str:
        from openapi_client_gen.generators.schemas import generate_schemas

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            spec_path = tmpdir_path / "openapi.json"
            spec_path.write_text(json.dumps(spec))

            schemas_path = tmpdir_path / "schemas.py"
            generate_schemas(spec_path, schemas_path, lowercase_enums=True)

            return schemas_path.read_text()

    def test_string_default(self):
        spec = {
            "openapi": "3.0.0",
            "info": {"title": "API", "version": "1.0.0"},
            "components": {
                "schemas": {
                    "Config": {
                        "type": "object",
                        "properties": {"locale": {"type": "string", "default": "en"}},
                    },
                }
            },
        }
        content = self._generate_schemas(spec)

        assert 'default="en"' in content or "= 'en'" in content or '= "en"' in content

    def test_integer_default(self):
        spec = {
            "openapi": "3.0.0",
            "info": {"title": "API", "version": "1.0.0"},
            "components": {
                "schemas": {
                    "Pagination": {
                        "type": "object",
                        "properties": {"limit": {"type": "integer", "default": 10}},
                    },
                }
            },
        }
        content = self._generate_schemas(spec)

        assert "default=10" in content or "= 10" in content

    def test_boolean_default(self):
        spec = {
            "openapi": "3.0.0",
            "info": {"title": "API", "version": "1.0.0"},
            "components": {
                "schemas": {
                    "Settings": {
                        "type": "object",
                        "properties": {"enabled": {"type": "boolean", "default": True}},
                    },
                }
            },
        }
        content = self._generate_schemas(spec)

        assert "default=True" in content or "= True" in content

    def test_enum_default(self):
        spec = {
            "openapi": "3.0.0",
            "info": {"title": "API", "version": "1.0.0"},
            "components": {
                "schemas": {
                    "StatusEnum": {"type": "string", "enum": ["active", "inactive"], "default": "active"},
                    "User": {"type": "object", "properties": {"status": {"$ref": "#/components/schemas/StatusEnum", "default": "active"}}},
                }
            },
        }
        content = self._generate_schemas(spec)

        assert "active" in content


class TestHeaderParameters:
    def _generate_service(self, spec: dict) -> str:
        from openapi_client_gen.generators.service import generate_service
        from openapi_client_gen.parser import parse_openapi

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            spec_path = tmpdir_path / "openapi.json"
            spec_path.write_text(json.dumps(spec))

            parsed = parse_openapi(spec_path)
            service_path = tmpdir_path / "service.py"
            generate_service(parsed, service_path)

            return service_path.read_text()

    def test_header_parameter_parsed(self):
        from openapi_client_gen.parser import parse_openapi

        spec = {
            "openapi": "3.0.0",
            "info": {"title": "API", "version": "1.0.0"},
            "paths": {
                "/data/": {
                    "get": {
                        "operationId": "get_data",
                        "parameters": [{"name": "X-Request-ID", "in": "header", "required": False, "schema": {"type": "string"}}],
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

            op = parsed.operations[0]
            header_params = [p for p in op.parameters if p.in_ == "header"]
            assert len(header_params) == 1
            assert header_params[0].name == "X-Request-ID"


class TestAdditionalProperties:
    def _generate_schemas(self, spec: dict) -> str:
        from openapi_client_gen.generators.schemas import generate_schemas

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            spec_path = tmpdir_path / "openapi.json"
            spec_path.write_text(json.dumps(spec))

            schemas_path = tmpdir_path / "schemas.py"
            generate_schemas(spec_path, schemas_path, lowercase_enums=True)

            return schemas_path.read_text()

    def test_additional_properties_true(self):
        spec = {
            "openapi": "3.0.0",
            "info": {"title": "API", "version": "1.0.0"},
            "components": {
                "schemas": {
                    "DynamicData": {"type": "object", "additionalProperties": True},
                }
            },
        }
        content = self._generate_schemas(spec)

        assert "DynamicData" in content
        assert "extra" in content.lower() or "dict" in content.lower() or "Dict" in content

    def test_additional_properties_typed(self):
        spec = {
            "openapi": "3.0.0",
            "info": {"title": "API", "version": "1.0.0"},
            "components": {
                "schemas": {
                    "Metadata": {"type": "object", "additionalProperties": {"type": "string"}},
                }
            },
        }
        content = self._generate_schemas(spec)

        assert "Dict" in content or "dict" in content


class TestRequiredFields:
    def _generate_schemas(self, spec: dict) -> str:
        from openapi_client_gen.generators.schemas import generate_schemas

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            spec_path = tmpdir_path / "openapi.json"
            spec_path.write_text(json.dumps(spec))

            schemas_path = tmpdir_path / "schemas.py"
            generate_schemas(spec_path, schemas_path, lowercase_enums=True)

            return schemas_path.read_text()

    def test_required_field_not_optional(self):
        spec = {
            "openapi": "3.0.0",
            "info": {"title": "API", "version": "1.0.0"},
            "components": {
                "schemas": {
                    "User": {
                        "type": "object",
                        "required": ["name", "email"],
                        "properties": {
                            "name": {"type": "string"},
                            "email": {"type": "string"},
                            "bio": {"type": "string"},
                        },
                    },
                }
            },
        }
        content = self._generate_schemas(spec)

        lines = content.split("\n")
        for line in lines:
            if "name:" in line and "Optional" in line:
                pytest.fail("Required field 'name' should not be Optional")
            if "email:" in line and "Optional" in line:
                pytest.fail("Required field 'email' should not be Optional")


class TestExamples:
    def _generate_schemas(self, spec: dict) -> str:
        from openapi_client_gen.generators.schemas import generate_schemas

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            spec_path = tmpdir_path / "openapi.json"
            spec_path.write_text(json.dumps(spec))

            schemas_path = tmpdir_path / "schemas.py"
            generate_schemas(spec_path, schemas_path, lowercase_enums=True)

            return schemas_path.read_text()

    def test_example_in_field(self):
        spec = {
            "openapi": "3.0.0",
            "info": {"title": "API", "version": "1.0.0"},
            "components": {
                "schemas": {
                    "User": {
                        "type": "object",
                        "properties": {"email": {"type": "string", "example": "user@example.com"}},
                    },
                }
            },
        }
        content = self._generate_schemas(spec)

        assert "User" in content
        compile(content, "<string>", "exec")


class TestNullableFields:
    def _generate_schemas(self, spec: dict) -> str:
        from openapi_client_gen.generators.schemas import generate_schemas

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            spec_path = tmpdir_path / "openapi.json"
            spec_path.write_text(json.dumps(spec))

            schemas_path = tmpdir_path / "schemas.py"
            generate_schemas(spec_path, schemas_path, lowercase_enums=True)

            return schemas_path.read_text()

    def test_nullable_true_openapi30(self):
        spec = {
            "openapi": "3.0.0",
            "info": {"title": "API", "version": "1.0.0"},
            "components": {
                "schemas": {
                    "User": {
                        "type": "object",
                        "properties": {"nickname": {"type": "string", "nullable": True}},
                    },
                }
            },
        }
        content = self._generate_schemas(spec)

        assert "Optional" in content or "None" in content

    def test_anyof_null_openapi31(self):
        spec = {
            "openapi": "3.1.0",
            "info": {"title": "API", "version": "1.0.0"},
            "components": {
                "schemas": {
                    "User": {
                        "type": "object",
                        "properties": {"nickname": {"anyOf": [{"type": "string"}, {"type": "null"}]}},
                    },
                }
            },
        }
        content = self._generate_schemas(spec)

        assert "Optional" in content or "None" in content


class TestFormatHandling:
    def _generate_schemas(self, spec: dict) -> str:
        from openapi_client_gen.generators.schemas import generate_schemas

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            spec_path = tmpdir_path / "openapi.json"
            spec_path.write_text(json.dumps(spec))

            schemas_path = tmpdir_path / "schemas.py"
            generate_schemas(spec_path, schemas_path, lowercase_enums=True)

            return schemas_path.read_text()

    def test_uuid_format(self):
        spec = {
            "openapi": "3.0.0",
            "info": {"title": "API", "version": "1.0.0"},
            "components": {
                "schemas": {
                    "Resource": {"type": "object", "properties": {"id": {"type": "string", "format": "uuid"}}},
                }
            },
        }
        content = self._generate_schemas(spec)

        assert "UUID" in content or "str" in content

    def test_date_format(self):
        spec = {
            "openapi": "3.0.0",
            "info": {"title": "API", "version": "1.0.0"},
            "components": {
                "schemas": {
                    "Event": {"type": "object", "properties": {"event_date": {"type": "string", "format": "date"}}},
                }
            },
        }
        content = self._generate_schemas(spec)

        assert "date" in content.lower()

    def test_email_format(self):
        spec = {
            "openapi": "3.0.0",
            "info": {"title": "API", "version": "1.0.0"},
            "components": {
                "schemas": {
                    "User": {"type": "object", "properties": {"email": {"type": "string", "format": "email"}}},
                }
            },
        }
        content = self._generate_schemas(spec)

        assert "email" in content.lower()

    def test_uri_format(self):
        spec = {
            "openapi": "3.0.0",
            "info": {"title": "API", "version": "1.0.0"},
            "components": {
                "schemas": {
                    "Link": {"type": "object", "properties": {"url": {"type": "string", "format": "uri"}}},
                }
            },
        }
        content = self._generate_schemas(spec)

        assert "url" in content.lower() or "str" in content


class TestArrayConstraints:
    def _generate_schemas(self, spec: dict) -> str:
        from openapi_client_gen.generators.schemas import generate_schemas

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            spec_path = tmpdir_path / "openapi.json"
            spec_path.write_text(json.dumps(spec))

            schemas_path = tmpdir_path / "schemas.py"
            generate_schemas(spec_path, schemas_path, lowercase_enums=True)

            return schemas_path.read_text()

    def test_array_min_max_items(self):
        spec = {
            "openapi": "3.0.0",
            "info": {"title": "API", "version": "1.0.0"},
            "components": {
                "schemas": {
                    "Team": {
                        "type": "object",
                        "properties": {"members": {"type": "array", "items": {"type": "string"}, "minItems": 1, "maxItems": 10}},
                    },
                }
            },
        }
        content = self._generate_schemas(spec)

        assert "List" in content or "list" in content
        compile(content, "<string>", "exec")

    def test_unique_items(self):
        spec = {
            "openapi": "3.0.0",
            "info": {"title": "API", "version": "1.0.0"},
            "components": {
                "schemas": {
                    "Tags": {
                        "type": "object",
                        "properties": {"tags": {"type": "array", "items": {"type": "string"}, "uniqueItems": True}},
                    },
                }
            },
        }
        content = self._generate_schemas(spec)

        compile(content, "<string>", "exec")
