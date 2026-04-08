import json
import os
import re
from functools import partial
from pathlib import Path

HOME_PATH = Path("compiler/enums")
DESTINATION_PATH = Path("pyrogram/enums")
SCHEMA_PATH = Path("compiler/api/source/main_api.tl")
NOTICE_PATH = "NOTICE"

COMBINATOR_RE = re.compile(r"^([\w.]+)#([0-9a-f]+)\s(?:.*)=\s([\w<>.]+);$", re.MULTILINE)

WARNING = """
# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #
""".strip()

KEEP_FILES = {"auto_name.py", "__pycache__"}

# noinspection PyShadowingBuiltins
open = partial(open, encoding="utf-8")


def snake(s: str) -> str:
    s = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", s)
    return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s).lower()


def camel(s: str) -> str:
    return "".join([i[0].upper() + i[1:] for i in s.split("_")])


def parse_tl_schema(schema_path: Path = None) -> dict[str, list[str]]:
    """Parse TL schema and return a map of result type -> list of constructor names."""
    with open(schema_path or SCHEMA_PATH) as f:
        schema = f.read()

    type_to_constructors: dict[str, list[str]] = {}

    for m in COMBINATOR_RE.finditer(schema):
        qualname = m.group(1)
        qualtype = m.group(3)

        ns, name = qualname.split(".") if "." in qualname else ("", qualname)
        name = camel(name)
        qualname = f"{ns}.{name}" if ns else name

        tns, tname = qualtype.split(".") if "." in qualtype else ("", qualtype)
        tname = camel(tname)
        qualtype = f"{tns}.{tname}" if tns else tname

        if qualtype not in type_to_constructors:
            type_to_constructors[qualtype] = []
        type_to_constructors[qualtype].append(qualname)

    return type_to_constructors


def check_enums(enums: list[dict], type_to_constructors: dict[str, list[str]]) -> bool:
    """Check raw enums against TL schema. Returns True if warnings were emitted."""
    has_warnings = False

    for enum_def in enums:
        if enum_def["type"] != "raw":
            continue

        tl_type = enum_def.get("tl_type")
        if not tl_type:
            continue

        schema_constructors = set(type_to_constructors.get(tl_type, []))
        existing = {m["raw"] for m in enum_def["members"]}
        excluded = set(enum_def.get("exclude", []))

        missing = schema_constructors - existing - excluded
        if missing:
            has_warnings = True
            print(f"  WARNING: {enum_def['name']} is missing constructors from {tl_type}:")
            for c in sorted(missing):
                print(f"    - {c}")

    return has_warnings


def format_doc(doc: str, indent: str = "    ") -> str:
    """Format a doc string for an enum member."""
    if "\n" in doc:
        lines = doc.split("\n")
        result = f'{indent}"""{lines[0]}'
        for line in lines[1:]:
            if line:
                result += f"\n{indent}{line}"
            else:
                result += f"\n"
        result += f'\n{indent}"""'
        return result
    return f'{indent}"{doc}"'


def format_member(member: dict, enum_type: str) -> str:
    """Format a single enum member as Python source lines."""
    name = member["name"]

    if enum_type == "auto":
        assignment = f"    {name} = auto()"
    elif enum_type == "raw":
        assignment = f"    {name} = raw.types.{member['raw']}"
    else:  # value
        value = member.get("value")
        if value is None:
            assignment = f"    {name} = None"
        else:
            assignment = f"    {name} = {value}"

    doc = member.get("doc", "")
    if doc:
        return f"{assignment}\n{format_doc(doc)}"
    return assignment


def start():
    # Clean generated files
    for f in os.listdir(DESTINATION_PATH):
        if f in KEEP_FILES:
            continue
        path = DESTINATION_PATH / f
        if path.is_file():
            path.unlink()

    # Read notice
    with open(NOTICE_PATH) as f:
        notice = "\n".join(f"#  {line}".rstrip() for line in f.read().splitlines())

    # Read templates
    with open(HOME_PATH / "template/auto_enum.txt") as f:
        auto_tmpl = f.read()
    with open(HOME_PATH / "template/raw_enum.txt") as f:
        raw_tmpl = f.read()
    with open(HOME_PATH / "template/value_enum.txt") as f:
        value_tmpl = f.read()

    templates = {
        "auto": auto_tmpl,
        "raw": raw_tmpl,
        "value": value_tmpl,
    }

    # Read enum definitions
    with open(HOME_PATH / "source/enums.json") as f:
        enums = json.load(f)

    # Check raw enums against TL schema
    type_to_constructors = parse_tl_schema()
    check_enums(enums, type_to_constructors)

    enum_classes = []

    for enum_def in enums:
        name = enum_def["name"]
        enum_type = enum_def["type"]
        docstring = enum_def["docstring"]
        members = enum_def["members"]

        tmpl = templates[enum_type]

        members_str = "\n\n".join(format_member(m, enum_type) for m in members)

        source = tmpl.format(
            notice=notice,
            warning=WARNING,
            name=name,
            docstring=docstring,
            members=members_str,
        )

        module_name = snake(name)
        with open(DESTINATION_PATH / f"{module_name}.py", "w") as f:
            f.write(source)

        enum_classes.append((module_name, name))

    # Generate __init__.py
    with open(DESTINATION_PATH / "__init__.py", "w") as f:
        f.write(f"{notice}\n\n")

        for module_name, class_name in enum_classes:
            f.write(f"from .{module_name} import {class_name}\n")

        f.write(f"\n__all__ = [\n")
        for _, class_name in enum_classes:
            f.write(f"    '{class_name}',\n")
        f.write(f"]\n")


if "__main__" == __name__:
    HOME_PATH = Path(".")
    DESTINATION_PATH = Path("../../pyrogram/enums")
    SCHEMA_PATH = Path("../api/source/main_api.tl")
    NOTICE_PATH = Path("../../NOTICE")

    start()
