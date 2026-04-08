import json
import os
import re
from collections import defaultdict
from pathlib import Path
from typing import Dict, List
import argparse

import requests


BASE_DIR = Path(__file__).resolve().parent
URLS_FILE = BASE_DIR / "data_urls.txt"
SOURCE_DIR = BASE_DIR / "errors" / "source"
API_SOURCE_DIR = BASE_DIR / "api"

METHOD_CATEGORIES = ["bot_only", "user_only", "business_supported", "unauthed_allowed"]


def default_code_mapping() -> Dict[str, str]:
    return {
        "303": "303_SEE_OTHER.tsv",
        "400": "400_BAD_REQUEST.tsv",
        "401": "401_UNAUTHORIZED.tsv",
        "403": "403_FORBIDDEN.tsv",
        "404": "404_NOT_FOUND.tsv",
        "406": "406_NOT_ACCEPTABLE.tsv",
        "420": "420_FLOOD.tsv",
        "500": "500_INTERNAL_SERVER_ERROR.tsv",
        "503": "503_SERVICE_UNAVAILABLE.tsv",
    }


def load_urls() -> List[str]:
    if not URLS_FILE.exists():
        raise FileNotFoundError(f"Missing {URLS_FILE}")
    with open(URLS_FILE, encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip() and not line.strip().startswith("#")]


def fetch_json(url: str) -> dict:
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    text = r.text.strip()
    # 容错：若结尾带有多余字符，截取最后一个闭合大括号
    if not text.endswith("}"):
        last = text.rfind("}")
        if last != -1:
            text = text[: last + 1]
    return json.loads(text)


def sanitize_code_name(http_code: str) -> str:
    # Map numeric or signed numeric codes to canonical filename header
    # Examples: "400" -> "400_BAD_REQUEST", "-503" -> "503_SERVICE_UNAVAILABLE"
    # We keep existing names if already present in source dir; otherwise, infer minimal names
    existing = {p.name for p in SOURCE_DIR.glob("*.tsv")}
    # Try to find a file whose prefix matches this code (ignoring minus sign)
    unsigned = re.sub(r"^-", "", str(http_code))
    for name in existing:
        if name.startswith(f"{unsigned}_"):
            return name
    # Fallbacks for common HTTP codes
    mapping = default_code_mapping()
    return mapping.get(unsigned, f"{unsigned}_UNKNOWN.tsv")


def read_existing(path: Path) -> Dict[str, str]:
    data: Dict[str, str] = {}
    if not path.exists():
        return data
    with open(path, encoding="utf-8") as f:
        for i, line in enumerate(f):
            line = line.rstrip("\n")
            if i == 0 and line.startswith("id\t"):
                continue
            if not line:
                continue
            try:
                k, v = line.split("\t", 1)
            except ValueError:
                continue
            if k and v:
                data[k] = v
    return data


def write_tsv(path: Path, rows: Dict[str, str]) -> None:
    # Sort by id lexicographically to match existing tooling
    keys = sorted(rows.keys())
    with open(path, "w", encoding="utf-8") as f:
        f.write("id\tmessage\n")
        for i, k in enumerate(keys, start=1):
            f.write(f"{k}\t{rows[k]}")
            if i != len(keys):
                f.write("\n")


def merge_descriptions(status_block: dict, descriptions: dict, skip_empty: bool) -> Dict[str, Dict[str, str]]:
    # Build per-code mapping of id -> message
    per_code: Dict[str, Dict[str, str]] = defaultdict(dict)

    for code, err_to_methods in status_block.items():
        # Normalize code to string
        code_str = str(code)
        filename = sanitize_code_name(code_str)
        # Ensure descriptions exist
        for error_id in err_to_methods.keys():
            # Normalize placeholders: id: %d -> X ; message: %d -> {value}
            normalized_id = error_id.replace('%d', 'X')
            msg = descriptions.get(error_id, "")
            # Fallbacks: remove placeholders like %d for normalization? Keep as-is.
            # Ensure no tabs/newlines in messages
            msg = re.sub(r"\s+", " ", msg).strip()
            if msg:
                msg = msg.replace('%d', '{value}')
            if skip_empty and not msg:
                # drop this entry entirely when skipping empties
                continue
            if not msg:
                msg = ""
            per_code[filename][normalized_id] = msg

    return per_code


def main() -> None:
    SOURCE_DIR.mkdir(parents=True, exist_ok=True)

    # 清空 source 目录下现有的 TSV 文件
    removed = 0
    for p in SOURCE_DIR.glob("*.tsv"):
        try:
            p.unlink()
            removed += 1
        except Exception:
            pass
    if removed:
        print(f"[OK] Cleared {removed} file(s) in source/")

    parser = argparse.ArgumentParser(description="Fetch error JSONs and write TSVs")
    parser.add_argument("--skip-empty", action="store_true", help="skip errors without descriptions")
    args = parser.parse_args()

    urls = load_urls()

    # 先根据默认映射创建空文件（随后会填充内容）
    for filename in sorted(default_code_mapping().values()):
        path = SOURCE_DIR / filename
        if not path.exists():
            write_tsv(path, {})
    # Accumulate merged data across multiple URLs
    aggregated: Dict[str, Dict[str, str]] = defaultdict(dict)
    method_cats: Dict[str, set] = {cat: set() for cat in METHOD_CATEGORIES}

    for url in urls:
        try:
            data = fetch_json(url)
        except Exception as e:
            print(f"[WARN] Failed to fetch {url}: {e}")
            continue

        # 支持两种结构：{"statuses": {...}} 或 {"errors": {...}}
        statuses = data.get("statuses") or data.get("errors") or {}
        descriptions = data.get("descriptions") or {}

        per_code = merge_descriptions(statuses, descriptions, skip_empty=args.skip_empty)

        for filename, rows in per_code.items():
            # Merge with previous aggregated data
            for k, v in rows.items():
                # Prefer non-empty message
                old = aggregated[filename].get(k)
                if not old or (not old.strip() and v.strip()):
                    aggregated[filename][k] = v
                else:
                    aggregated[filename].setdefault(k, v)

        # Collect method categories
        for cat in METHOD_CATEGORIES:
            items = data.get(cat)
            if isinstance(items, list):
                method_cats[cat].update(items)

    # 合并写回
    for filename, rows in aggregated.items():
        path = SOURCE_DIR / filename
        existing = read_existing(path)
        # Merge existing first, then overwrite with new non-empty
        merged = dict(existing)
        for k, v in rows.items():
            if k in merged and merged[k].strip():
                # Keep existing non-empty message unless new is different and non-empty
                if v.strip() and merged[k].strip() != v.strip():
                    merged[k] = v
            else:
                merged[k] = v

        write_tsv(path, merged)
        print(f"[OK] Wrote {path.relative_to(BASE_DIR / 'errors')} with {len(merged)} rows")

    # Write method category JSON files
    API_SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    for cat in METHOD_CATEGORIES:
        items = sorted(method_cats[cat])
        if not items:
            continue
        path = API_SOURCE_DIR / f"{cat}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(items, f, indent=2, ensure_ascii=False)
            f.write("\n")
        print(f"[OK] Wrote {path.relative_to(BASE_DIR)} with {len(items)} methods")


if __name__ == "__main__":
    main()


