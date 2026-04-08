#!/usr/bin/env python3
"""TL Schema diff tool.

Parses .tl schema files, compares against a previous snapshot,
and outputs a JSON report of added/removed/modified constructors and functions.
"""

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

HOME_PATH = Path(__file__).parent
SOURCE_PATH = HOME_PATH / "source"
SNAPSHOT_PATH = HOME_PATH / "schema_snapshot.json"
DIFF_OUTPUT_PATH = HOME_PATH / "schema_changes.json"

SECTION_RE = re.compile(r"---(\w+)---")
LAYER_RE = re.compile(r"//\sLAYER\s(\d+)")
COMBINATOR_RE = re.compile(
    r"^([\w.]+)#([0-9a-f]+)\s(?:.*)=\s([\w<>.]+);$", re.MULTILINE
)
ARGS_RE = re.compile(r"[^{](\w+):([\w?!.<>#]+)")
FLAGS_RE = re.compile(r"flags\d?:#")


def parse_schema(paths: list[Path]) -> dict[str, Any]:
    """Parse .tl files and return a dict of all combinators keyed by qualname."""
    combinators: dict[str, dict[str, Any]] = {}
    section = "types"
    layer = 0

    for path in paths:
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()

                s = SECTION_RE.match(line)
                if s:
                    section = s.group(1)
                    continue

                l = LAYER_RE.match(line)
                if l:
                    layer = int(l.group(1))
                    continue

                m = COMBINATOR_RE.match(line)
                if m:
                    qualname, cid, qualtype = m.groups()

                    # Extract args, skip flags:# fields
                    args = [
                        {"name": name, "type": typ}
                        for name, typ in ARGS_RE.findall(line)
                        if not FLAGS_RE.match(f"{name}:{typ}")
                    ]

                    namespace = ""
                    name = qualname
                    if "." in qualname:
                        namespace, name = qualname.split(".", 1)

                    combinators[qualname] = {
                        "section": section,
                        "id": cid,
                        "namespace": namespace,
                        "name": name,
                        "qualtype": qualtype,
                        "args": args,
                    }

    return {"layer": layer, "combinators": combinators}


def diff_schemas(
    old: dict[str, Any], new: dict[str, Any]
) -> dict[str, Any]:
    """Compare two parsed schemas and return structured diff."""
    old_c = old.get("combinators", {})
    new_c = new.get("combinators", {})

    old_keys = set(old_c.keys())
    new_keys = set(new_c.keys())

    added_keys = sorted(new_keys - old_keys)
    removed_keys = sorted(old_keys - new_keys)
    common_keys = sorted(old_keys & new_keys)

    result: dict[str, Any] = {
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "old_layer": old.get("layer", 0),
        "new_layer": new.get("layer", 0),
        "types": {"added": [], "removed": [], "modified": []},
        "functions": {"added": [], "removed": [], "modified": []},
    }

    for key in added_keys:
        entry = new_c[key]
        section = entry["section"]
        target = "types" if section == "types" else "functions"
        result[target]["added"].append({
            "qualname": key,
            "id": entry["id"],
            "qualtype": entry["qualtype"],
            "args": entry["args"],
        })

    for key in removed_keys:
        entry = old_c[key]
        section = entry["section"]
        target = "types" if section == "types" else "functions"
        result[target]["removed"].append({
            "qualname": key,
            "id": entry["id"],
            "qualtype": entry["qualtype"],
        })

    for key in common_keys:
        o, n = old_c[key], new_c[key]
        changes: dict[str, Any] = {}

        if o["id"] != n["id"]:
            changes["id"] = {"old": o["id"], "new": n["id"]}

        if o["qualtype"] != n["qualtype"]:
            changes["qualtype"] = {"old": o["qualtype"], "new": n["qualtype"]}

        old_args = {a["name"]: a["type"] for a in o["args"]}
        new_args = {a["name"]: a["type"] for a in n["args"]}

        args_added = [
            {"name": k, "type": new_args[k]}
            for k in sorted(set(new_args) - set(old_args))
        ]
        args_removed = [
            {"name": k, "type": old_args[k]}
            for k in sorted(set(old_args) - set(new_args))
        ]
        args_type_changed = [
            {"name": k, "old_type": old_args[k], "new_type": new_args[k]}
            for k in sorted(set(old_args) & set(new_args))
            if old_args[k] != new_args[k]
        ]

        if args_added:
            changes["args_added"] = args_added
        if args_removed:
            changes["args_removed"] = args_removed
        if args_type_changed:
            changes["args_type_changed"] = args_type_changed

        if changes:
            section = n["section"]
            target = "types" if section == "types" else "functions"
            result[target]["modified"].append({
                "qualname": key,
                "changes": changes,
            })

    return result


def main():
    tl_files = sorted(SOURCE_PATH.glob("*.tl"))
    current = parse_schema(tl_files)

    if SNAPSHOT_PATH.exists():
        with open(SNAPSHOT_PATH, encoding="utf-8") as f:
            previous = json.load(f)

        changes = diff_schemas(previous, current)

        with open(DIFF_OUTPUT_PATH, "w", encoding="utf-8") as f:
            json.dump(changes, f, indent=2, ensure_ascii=False)

        added_t = len(changes["types"]["added"])
        removed_t = len(changes["types"]["removed"])
        modified_t = len(changes["types"]["modified"])
        added_f = len(changes["functions"]["added"])
        removed_f = len(changes["functions"]["removed"])
        modified_f = len(changes["functions"]["modified"])

        total = added_t + removed_t + modified_t + added_f + removed_f + modified_f

        if total == 0:
            print("No changes detected.")
        else:
            print(f"Layer: {changes['old_layer']} -> {changes['new_layer']}")
            print(f"Types:     +{added_t}  -{removed_t}  ~{modified_t}")
            print(f"Functions: +{added_f}  -{removed_f}  ~{modified_f}")
            print(f"Written to {DIFF_OUTPUT_PATH}")
    else:
        print("No previous snapshot found. Saving current schema as baseline.")

    # Save current as snapshot for next run
    with open(SNAPSHOT_PATH, "w", encoding="utf-8") as f:
        json.dump(current, f, indent=2, ensure_ascii=False)

    print(f"Snapshot saved to {SNAPSHOT_PATH}")


if __name__ == "__main__":
    main()
