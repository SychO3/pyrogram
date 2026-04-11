#!/usr/bin/env python3
#  Pyrogram - Telegram MTProto API Client Library for Python
#  Copyright (C) 2017-present Dan <https://github.com/delivrance>
#
#  This file is part of Pyrogram.
#
#  Pyrogram is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published
#  by the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Pyrogram is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with Pyrogram.  If not, see <http://www.gnu.org/licenses/>.

"""CLI tool to migrate per-bot .session SQLite files into a unified database.

Usage::

    python -m pyrogram.tools.migrate_sessions \\
        --db bots.db \\
        --sessions /path/to/sessions/ \\
        [--pattern "*.session"] \\
        [--dry-run]

Each .session file is a per-bot SQLite database created by the original
Pyrogram Client. This tool imports all of them into a single
MultiSQLiteStorage database used by Runtime.
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import os
import re
import sys
from pathlib import Path
from typing import List, Optional

log = logging.getLogger(__name__)


def discover_session_files(
    directory: str,
    pattern: str = "*.session",
) -> List[Path]:
    """Find session files in the given directory."""
    base = Path(directory)
    if not base.is_dir():
        raise FileNotFoundError(f"Directory not found: {directory}")

    files = sorted(base.glob(pattern))
    return [f for f in files if f.is_file()]


def extract_bot_id(session_file: Path) -> Optional[int]:
    """Try to extract bot_id from filename or session content.

    Convention: filenames like ``123456789.session`` or ``bot_123456789.session``.
    Falls back to reading user_id from the session SQLite.
    """
    stem = session_file.stem

    # Try numeric filename
    if stem.isdigit():
        return int(stem)

    # Try bot_NNNN pattern
    match = re.match(r"bot[_-]?(\d+)", stem)
    if match:
        return int(match.group(1))

    # Fall back: read from SQLite
    try:
        import sqlite3
        conn = sqlite3.connect(str(session_file))
        cursor = conn.cursor()

        # Try user_id from sessions table
        try:
            cursor.execute("SELECT user_id FROM sessions LIMIT 1")
            row = cursor.fetchone()
            if row and row[0]:
                return int(row[0])
        except sqlite3.OperationalError:
            pass

        conn.close()
    except Exception:
        pass

    return None


async def migrate_sessions(
    db_path: str,
    session_files: List[Path],
    dry_run: bool = False,
    backend: str = "sqlite",
    redis_uri: str = "redis://localhost:6379/0",
) -> dict:
    """Migrate session files into the unified storage.

    Returns a dict with counts: migrated, skipped, failed.
    """
    results = {"migrated": 0, "skipped": 0, "failed": 0, "details": []}

    if backend == "redis":
        from pyrogram.storage.redis_storage import RedisStorage
        storage = RedisStorage(redis_uri)
    else:
        from pyrogram.storage import MultiSQLiteStorage
        storage = MultiSQLiteStorage(db_path)

    if not dry_run:
        await storage.open()

    try:
        for session_file in session_files:
            bot_id = extract_bot_id(session_file)
            if bot_id is None:
                log.warning("Cannot determine bot_id for %s, skipping", session_file)
                results["skipped"] += 1
                results["details"].append(
                    {"file": str(session_file), "status": "skipped", "reason": "no bot_id"}
                )
                continue

            if dry_run:
                log.info("[DRY RUN] Would migrate %s (bot_id=%d)", session_file, bot_id)
                results["migrated"] += 1
                results["details"].append(
                    {"file": str(session_file), "status": "would_migrate", "bot_id": bot_id}
                )
                continue

            try:
                data = await storage.migrate_from_file(str(session_file), bot_id)
                if data is None:
                    log.warning("Empty or invalid session: %s", session_file)
                    results["skipped"] += 1
                    results["details"].append(
                        {"file": str(session_file), "status": "skipped", "reason": "empty"}
                    )
                else:
                    log.info(
                        "Migrated %s -> bot_id=%d, dc=%d, user=%s",
                        session_file.name, bot_id, data.dc_id, data.user_id,
                    )
                    results["migrated"] += 1
                    results["details"].append(
                        {"file": str(session_file), "status": "migrated", "bot_id": bot_id}
                    )
            except Exception as e:
                log.error("Failed to migrate %s: %s", session_file, e)
                results["failed"] += 1
                results["details"].append(
                    {"file": str(session_file), "status": "failed", "error": str(e)}
                )
    finally:
        if not dry_run:
            await storage.close()

    return results


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Migrate per-bot .session files into a unified database",
        prog="python -m pyrogram.tools.migrate_sessions",
    )
    parser.add_argument(
        "--db", default="bots.db",
        help="Path to the unified SQLite database (default: bots.db)",
    )
    parser.add_argument(
        "--sessions", required=True,
        help="Directory containing .session files",
    )
    parser.add_argument(
        "--pattern", default="*.session",
        help="Glob pattern for session files (default: *.session)",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Show what would be migrated without making changes",
    )
    parser.add_argument(
        "--backend", choices=["sqlite", "redis"], default="sqlite",
        help="Storage backend to migrate into (default: sqlite)",
    )
    parser.add_argument(
        "--redis-uri", default="redis://localhost:6379/0",
        help="Redis URI (only used with --backend redis)",
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true",
        help="Enable verbose logging",
    )

    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    try:
        files = discover_session_files(args.sessions, args.pattern)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    if not files:
        print(f"No session files found in {args.sessions} matching {args.pattern}")
        return 0

    print(f"Found {len(files)} session file(s)")

    results = asyncio.run(
        migrate_sessions(
            db_path=args.db,
            session_files=files,
            dry_run=args.dry_run,
            backend=args.backend,
            redis_uri=args.redis_uri,
        )
    )

    print(f"\nResults: {results['migrated']} migrated, "
          f"{results['skipped']} skipped, {results['failed']} failed")

    return 0 if results["failed"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
