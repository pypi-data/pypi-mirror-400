import keyword
import re

PYTHON_RESERVED = set(keyword.kwlist) | {
    "True",
    "False",
    "None",
    "type",
    "id",
    "list",
    "dict",
    "set",
    "str",
    "int",
    "float",
    "bool",
    "object",
    "property",
    "classmethod",
    "staticmethod",
}


def safe_name(name: str, suffix: str = "_") -> str:
    if name in PYTHON_RESERVED:
        return f"{name}{suffix}"
    return name


def safe_enum_member(value: str, existing: set[str] | None = None) -> str:
    name = value.lower()
    name = re.sub(r"[^a-z0-9_]", "_", name)

    if name and name[0].isdigit():
        name = f"value_{name}"

    if not name:
        name = "empty"

    if existing is not None:
        original = name
        counter = 1
        while name in existing:
            name = f"{original}_{counter}"
            counter += 1
        existing.add(name)

    return safe_name(name)


def safe_function_name(name: str, existing: set[str] | None = None) -> str:
    clean = re.sub(r"[^a-z0-9_]", "_", name.lower())
    clean = re.sub(r"_+", "_", clean)
    clean = clean.strip("_")

    if not clean:
        clean = "operation"

    clean = safe_name(clean)

    if existing is not None:
        original = clean
        counter = 1
        while clean in existing:
            clean = f"{original}_{counter}"
            counter += 1
        existing.add(clean)

    return clean
