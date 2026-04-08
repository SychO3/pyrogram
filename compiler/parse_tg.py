"""Parse types and methods from the Telegram Bot API HTML page (tg.html).

Outputs two JSON files under compiler/api/:
  - bot_api_types.json   — all Bot API types
  - bot_api_methods.json — all Bot API methods
"""

import json
import re
from html import unescape
from html.parser import HTMLParser
from pathlib import Path

BASE_DIR = Path(__file__).parent
HTML_PATH = BASE_DIR / "tg.html"
API_DIR = BASE_DIR / "api"

# ---------- HTML table extractor ----------

class TableParser(HTMLParser):
    """Extract all <table class="table"> blocks from the HTML."""

    def __init__(self):
        super().__init__()
        self._in_table = False
        self._depth = 0
        self._in_td = False
        self._in_th = False
        self._current_row = []
        self._current_cell = ""
        self._rows = []
        self.tables = []  # list of (offset, rows)
        self._table_start = 0

    def handle_starttag(self, tag, attrs):
        if tag == "table" and ("class", "table") in attrs:
            self._in_table = True
            self._depth = 1
            self._rows = []
            self._table_start = self.getpos()[0]
            return
        if self._in_table:
            if tag == "table":
                self._depth += 1
            elif tag in ("td", "th"):
                self._in_td = tag == "td"
                self._in_th = tag == "th"
                self._current_cell = ""
            elif tag == "tr":
                self._current_row = []
            elif tag == "a" and self._in_td:
                for k, v in attrs:
                    if k == "href" and v.startswith("#"):
                        pass  # link text will be captured via handle_data
            elif tag == "em" and self._in_td:
                pass

    def handle_endtag(self, tag):
        if not self._in_table:
            return
        if tag == "table":
            self._depth -= 1
            if self._depth == 0:
                self._in_table = False
                self.tables.append((self._table_start, self._rows))
                return
        if tag in ("td", "th"):
            self._current_row.append(self._current_cell.strip())
            self._in_td = False
            self._in_th = False
        elif tag == "tr":
            if self._current_row:
                self._rows.append(self._current_row)

    def handle_data(self, data):
        if self._in_table and (self._in_td or self._in_th):
            self._current_cell += data


# ---------- h4 heading extractor ----------

_H4_RE = re.compile(
    r'<h4><a class="anchor" name="([^"]+)" href="[^"]*">'
    r'<i class="anchor-icon"></i></a>(.+?)</h4>',
)


def _extract_headings(html: str) -> list[tuple[int, str, str]]:
    """Return [(line_number, anchor_name, display_text), ...]."""
    results = []
    for i, line in enumerate(html.splitlines(), 1):
        m = _H4_RE.search(line)
        if m:
            results.append((i, m.group(1), m.group(2)))
    return results


# ---------- description / return type extractor ----------

_STRIP_HTML = re.compile(r"<[^>]+>")
_RETURN_PATTERNS = [
    # "Returns ... on success"
    re.compile(r"[Rr]eturns\s+(.+?)\s+on\s+success", re.DOTALL),
    # "On success, ... is returned"
    re.compile(r"[Oo]n\s+success,\s+(.+?)\s+is\s+returned", re.DOTALL),
    # "On success, ... are returned"
    re.compile(r"[Oo]n\s+success,\s+(.+?)\s+are\s+returned", re.DOTALL),
    # "On success, returns a/an X"
    re.compile(r"[Oo]n\s+success,\s+returns\s+(.+?)\."),
    # "Returns ... as a X object"
    re.compile(r"[Rr]eturns\s+.+?\s+as\s+(?:an?\s+)?(.+?)\s+objects?\."),
    # "Returns an Array of X objects."
    re.compile(r"[Rr]eturns\s+(an?\s+[Aa]rray\s+of\s+.+?)\s+objects?\."),
    # "Returns a X object."
    re.compile(r"[Rr]eturns\s+(an?\s+.+?)\s+objects?\."),
    # "in form of a X object"
    re.compile(r"in\s+form\s+of\s+(an?\s+.+?)\s+objects?\."),
    # "Will return ... in a game"
    re.compile(r"[Ww]ill\s+return\s+(.+?)\."),
    # Generic fallback: "Returns a X."
    re.compile(r"[Rr]eturns\s+(an?\s+.+?)\."),
]

_HREF_RE = re.compile(r'<a[^>]*href="#([^"]*)"[^>]*>([^<]+)</a>')


def _extract_description_block(lines: list[str], start: int) -> str:
    """Collect raw HTML from the line after *start* until the next h3/h4 or table."""
    parts = []
    for line in lines[start:]:  # start is 1-based line_no, lines[start] is the line after h4
        if "<h4>" in line or "<h3>" in line or '<table class="table">' in line:
            break
        parts.append(line)
    return "\n".join(parts)


def _html_to_text(html: str) -> str:
    return unescape(_STRIP_HTML.sub("", html)).strip()


def _extract_return_type(desc_html: str) -> str | None:
    for pat in _RETURN_PATTERNS:
        m = pat.search(desc_html)
        if m:
            raw = m.group(1).strip()
            # Prefer linked type names
            href = _HREF_RE.search(raw)
            if href:
                type_name = href.group(2)
                if "Array of" in raw or "array of" in raw:
                    return f"Array of {type_name}"
                return type_name
            clean = _html_to_text(raw)
            return clean
    return None


# ---------- subtypes (union) extractor ----------

def _extract_subtypes(lines: list[str], start: int) -> list[str]:
    """For union/abstract types, extract the list of subtypes from <ul>."""
    subtypes = []
    in_ul = False
    for line in lines[start:]:
        if "<h4>" in line or "<h3>" in line or '<table class="table">' in line:
            break
        if "<ul>" in line:
            in_ul = True
        if in_ul:
            for m in _HREF_RE.finditer(line):
                subtypes.append(m.group(2))
        if "</ul>" in line and in_ul:
            break
    return subtypes


# ---------- h3 section extractor ----------

_H3_RE = re.compile(
    r'<h3><a class="anchor" name="([^"]+)" href="[^"]*">'
    r'<i class="anchor-icon"></i></a>(.+?)</h3>',
)

# Sections before actual type/method definitions — skip these
_SKIP_SECTIONS = {
    "recent-changes",
    "authorizing-your-bot",
    "making-requests",
    "making-requests-when-getting-updates",
    "using-a-local-bot-api-server",
    "do-i-need-a-local-bot-api-server",
}


def _extract_h3_sections(html: str) -> list[tuple[int, str, str]]:
    """Return [(line_number, anchor_name, display_text), ...]."""
    results = []
    for i, line in enumerate(html.splitlines(), 1):
        m = _H3_RE.search(line)
        if m and m.group(1) not in _SKIP_SECTIONS:
            results.append((i, m.group(1), m.group(2)))
    return results


# ---------- main parser ----------

def _is_method_name(name: str) -> bool:
    """Methods start with a lowercase letter."""
    return name[0].islower()


def parse(html: str) -> tuple[list[dict], list[dict]]:
    """Parse tg.html and return (types, methods)."""
    lines = html.splitlines()

    # 1. Extract all h4 headings
    headings = _extract_headings(html)

    # 2. Extract all h3 sections for category grouping
    h3_sections = _extract_h3_sections(html)

    # 3. Parse tables
    parser = TableParser()
    parser.feed(html)
    # Build line_number -> table rows mapping
    table_map: dict[int, list[list[str]]] = {}
    for line_no, rows in parser.tables:
        table_map[line_no] = rows

    # 4. For each heading, find its nearest table (if any)
    def _find_table(heading_line: int, next_heading_line: int):
        for tl in sorted(table_map):
            if heading_line < tl < next_heading_line:
                return table_map[tl]
        return None

    # 5. Determine current h3 section for each heading
    def _get_section(heading_line: int) -> str:
        current = ""
        for sl, _, sname in h3_sections:
            if sl < heading_line:
                current = sname
            else:
                break
        return current

    types = []
    methods = []

    for idx, (line_no, anchor, name) in enumerate(headings):
        # Skip non-API headings (dates, version numbers, etc.)
        if re.match(r"\w+\s+\d+,?\s+\d{4}", name):  # "April 3, 2026"
            continue
        if name.startswith("Bot API"):
            continue

        next_line = headings[idx + 1][0] if idx + 1 < len(headings) else len(lines) + 1
        table = _find_table(line_no, next_line)
        desc_html = _extract_description_block(lines, line_no)  # line_no is 1-based, lines is 0-based
        description = _html_to_text(desc_html)
        section = _get_section(line_no)

        if _is_method_name(name):
            # --- Method ---
            method = {
                "name": name,
                "anchor": anchor,
                "section": section,
                "description": description,
                "returns": _extract_return_type(desc_html),
                "parameters": [],
            }
            if table and len(table) > 1:
                for row in table[1:]:
                    if len(row) < 4:
                        continue
                    method["parameters"].append({
                        "name": row[0],
                        "type": row[1],
                        "required": row[2].strip().lower() == "yes",
                        "description": row[3],
                    })
            methods.append(method)
        else:
            # --- Type ---
            typ = {
                "name": name,
                "anchor": anchor,
                "section": section,
                "description": description,
                "fields": [],
                "subtypes": [],
            }
            subtypes = _extract_subtypes(lines, line_no)
            if subtypes:
                typ["subtypes"] = subtypes
            elif table and len(table) > 1:
                for row in table[1:]:
                    if len(row) < 3:
                        continue
                    typ["fields"].append({
                        "name": row[0],
                        "type": row[1],
                        "description": row[2],
                    })
            types.append(typ)

    return types, methods


def main():
    html = HTML_PATH.read_text(encoding="utf-8")
    types, methods = parse(html)

    API_DIR.mkdir(parents=True, exist_ok=True)

    types_path = API_DIR / "bot_api_types.json"
    methods_path = API_DIR / "bot_api_methods.json"

    types_path.write_text(
        json.dumps(types, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    methods_path.write_text(
        json.dumps(methods, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print(f"Parsed {len(types)} types -> {types_path}")
    print(f"Parsed {len(methods)} methods -> {methods_path}")


if __name__ == "__main__":
    main()
