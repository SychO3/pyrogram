"""Check raw enums against the TL schema for missing constructors."""

from pathlib import Path
from compiler import parse_tl_schema, check_enums, open
import json

SCHEMA_PATH = Path("../api/source/main_api.tl")

if __name__ == "__main__":
    with open(Path("source/enums.json")) as f:
        enums = json.load(f)

    type_to_constructors = parse_tl_schema(SCHEMA_PATH)
    has_warnings = check_enums(enums, type_to_constructors)

    if not has_warnings:
        print("All raw enums are up to date with the TL schema.")
