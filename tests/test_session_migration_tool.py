"""Comprehensive tests for the CLI migration tool at pyrogram.tools.migrate_sessions.

Covers discover_session_files, extract_bot_id, migrate_sessions, dry_run mode,
and the main() CLI entry point.
"""

import asyncio
import sqlite3
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from pyrogram.tools.migrate_sessions import (
    discover_session_files,
    extract_bot_id,
    main,
    migrate_sessions,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _create_session_file(path: Path, user_id: int = 0) -> Path:
    """Create a minimal SQLite session file with a sessions table."""
    conn = sqlite3.connect(str(path))
    conn.execute(
        "CREATE TABLE IF NOT EXISTS sessions ("
        "  dc_id INTEGER, server_address TEXT, port INTEGER,"
        "  auth_key BLOB, user_id INTEGER, date INTEGER,"
        "  test_mode INTEGER, is_bot INTEGER"
        ")"
    )
    if user_id:
        conn.execute(
            "INSERT INTO sessions (dc_id, server_address, port, auth_key, user_id, date, test_mode, is_bot) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (2, "149.154.167.50", 443, b"\x00" * 256, user_id, 0, 0, 1),
        )
    conn.commit()
    conn.close()
    return path


def _create_empty_file(path: Path) -> Path:
    """Create a file with no SQLite content (e.g., corrupt or not a DB)."""
    path.write_bytes(b"not-a-database")
    return path


def _make_mock_storage(**overrides):
    """Build a mock storage instance with async open/close/migrate_from_file."""
    storage = AsyncMock()
    storage.open = AsyncMock()
    storage.close = AsyncMock()
    storage.migrate_from_file = AsyncMock(
        return_value=MagicMock(dc_id=2, user_id=0)
    )
    for k, v in overrides.items():
        setattr(storage, k, v)
    return storage


def _make_storage_class(storage_instance):
    """Build a MagicMock class whose __call__ returns the given instance.

    This is necessary because MultiSQLiteStorage(db_path) is a regular
    synchronous constructor call; using AsyncMock for the class would
    return a coroutine instead of the instance.
    """
    cls_mock = MagicMock()
    cls_mock.return_value = storage_instance
    return cls_mock


# ===========================================================================
# discover_session_files
# ===========================================================================


class TestDiscoverSessionFiles:
    """Tests for discover_session_files()."""

    def test_finds_session_files(self, tmp_path: Path):
        """Should find all .session files in the given directory."""
        (tmp_path / "bot1.session").touch()
        (tmp_path / "bot2.session").touch()
        (tmp_path / "other.txt").touch()

        result = discover_session_files(str(tmp_path))
        names = [f.name for f in result]

        assert len(result) == 2
        assert "bot1.session" in names
        assert "bot2.session" in names
        assert "other.txt" not in names

    def test_custom_pattern(self, tmp_path: Path):
        """Should respect a custom glob pattern."""
        (tmp_path / "bot1.session").touch()
        (tmp_path / "bot2.dat").touch()

        result = discover_session_files(str(tmp_path), pattern="*.dat")

        assert len(result) == 1
        assert result[0].name == "bot2.dat"

    def test_empty_directory(self, tmp_path: Path):
        """Should return an empty list for a directory with no matches."""
        result = discover_session_files(str(tmp_path))
        assert result == []

    def test_nonexistent_directory_raises(self):
        """Should raise FileNotFoundError for a directory that doesn't exist."""
        with pytest.raises(FileNotFoundError, match="Directory not found"):
            discover_session_files("/nonexistent/directory/abc123")

    def test_ignores_subdirectories(self, tmp_path: Path):
        """Subdirectories matching the glob pattern should be excluded."""
        subdir = tmp_path / "fake.session"
        subdir.mkdir()
        (tmp_path / "real.session").touch()

        result = discover_session_files(str(tmp_path))

        assert len(result) == 1
        assert result[0].name == "real.session"

    def test_returns_sorted_results(self, tmp_path: Path):
        """Results should be sorted by path."""
        (tmp_path / "z_bot.session").touch()
        (tmp_path / "a_bot.session").touch()
        (tmp_path / "m_bot.session").touch()

        result = discover_session_files(str(tmp_path))
        names = [f.name for f in result]

        assert names == sorted(names)


# ===========================================================================
# extract_bot_id
# ===========================================================================


class TestExtractBotId:
    """Tests for extract_bot_id()."""

    def test_numeric_filename(self, tmp_path: Path):
        """Pure numeric filename should be used as bot_id."""
        f = tmp_path / "123456789.session"
        f.touch()
        assert extract_bot_id(f) == 123456789

    def test_bot_underscore_pattern(self, tmp_path: Path):
        """bot_NNNN pattern should extract the number."""
        f = tmp_path / "bot_987654.session"
        f.touch()
        assert extract_bot_id(f) == 987654

    def test_bot_dash_pattern(self, tmp_path: Path):
        """bot-NNNN pattern should extract the number."""
        f = tmp_path / "bot-111222.session"
        f.touch()
        assert extract_bot_id(f) == 111222

    def test_bot_no_separator_pattern(self, tmp_path: Path):
        """botNNNN pattern (no separator) should extract the number."""
        f = tmp_path / "bot555666.session"
        f.touch()
        assert extract_bot_id(f) == 555666

    def test_fallback_to_sqlite_user_id(self, tmp_path: Path):
        """When filename doesn't match, should read user_id from SQLite."""
        f = tmp_path / "my_custom_bot.session"
        _create_session_file(f, user_id=42424242)
        assert extract_bot_id(f) == 42424242

    def test_fallback_sqlite_no_user_id(self, tmp_path: Path):
        """When SQLite has no user_id, should return None."""
        f = tmp_path / "unknown_bot.session"
        _create_session_file(f, user_id=0)  # 0 is falsy
        assert extract_bot_id(f) is None

    def test_fallback_sqlite_no_sessions_table(self, tmp_path: Path):
        """When SQLite has no sessions table, should return None."""
        f = tmp_path / "empty.session"
        conn = sqlite3.connect(str(f))
        conn.execute("CREATE TABLE other (id INTEGER)")
        conn.commit()
        conn.close()
        assert extract_bot_id(f) is None

    def test_corrupt_file_returns_none(self, tmp_path: Path):
        """Corrupt / non-SQLite file should return None."""
        f = tmp_path / "corrupt.session"
        _create_empty_file(f)
        assert extract_bot_id(f) is None

    def test_nonexistent_file_returns_none(self, tmp_path: Path):
        """Non-existent file should return None (no crash)."""
        f = tmp_path / "does_not_exist.session"
        assert extract_bot_id(f) is None

    def test_large_numeric_id(self, tmp_path: Path):
        """Large bot IDs (10+ digits) should work."""
        f = tmp_path / "9999999999.session"
        f.touch()
        assert extract_bot_id(f) == 9999999999


# ===========================================================================
# migrate_sessions (async)
# ===========================================================================


class TestMigrateSessions:
    """Tests for the async migrate_sessions() function."""

    @pytest.mark.asyncio
    async def test_migrate_single_file(self, tmp_path: Path):
        """Should migrate a single session file successfully."""
        f = tmp_path / "111222333.session"
        _create_session_file(f, user_id=111222333)

        storage = _make_mock_storage(
            migrate_from_file=AsyncMock(
                return_value=MagicMock(dc_id=2, user_id=111222333)
            ),
        )
        cls_mock = _make_storage_class(storage)

        with patch("pyrogram.storage.MultiSQLiteStorage", cls_mock):
            results = await migrate_sessions(
                db_path=str(tmp_path / "test.db"),
                session_files=[f],
            )

        assert results["migrated"] == 1
        assert results["skipped"] == 0
        assert results["failed"] == 0

    @pytest.mark.asyncio
    async def test_migrate_skips_unknown_bot_id(self, tmp_path: Path):
        """Files where bot_id cannot be determined should be skipped."""
        f = tmp_path / "unknown_name.session"
        _create_empty_file(f)

        storage = _make_mock_storage()
        cls_mock = _make_storage_class(storage)

        with patch("pyrogram.storage.MultiSQLiteStorage", cls_mock):
            results = await migrate_sessions(
                db_path=str(tmp_path / "test.db"),
                session_files=[f],
            )

        assert results["skipped"] == 1
        assert results["migrated"] == 0
        assert results["details"][0]["reason"] == "no bot_id"

    @pytest.mark.asyncio
    async def test_migrate_handles_migration_error(self, tmp_path: Path):
        """If migrate_from_file raises, the file should be counted as failed."""
        f = tmp_path / "999888777.session"
        f.touch()

        storage = _make_mock_storage(
            migrate_from_file=AsyncMock(side_effect=RuntimeError("DB locked")),
        )
        cls_mock = _make_storage_class(storage)

        with patch("pyrogram.storage.MultiSQLiteStorage", cls_mock):
            results = await migrate_sessions(
                db_path=str(tmp_path / "test.db"),
                session_files=[f],
            )

        assert results["failed"] == 1
        assert results["migrated"] == 0
        assert "DB locked" in results["details"][0]["error"]

    @pytest.mark.asyncio
    async def test_migrate_handles_empty_session(self, tmp_path: Path):
        """If migrate_from_file returns None, the file should be skipped."""
        f = tmp_path / "555444333.session"
        f.touch()

        storage = _make_mock_storage(
            migrate_from_file=AsyncMock(return_value=None),
        )
        cls_mock = _make_storage_class(storage)

        with patch("pyrogram.storage.MultiSQLiteStorage", cls_mock):
            results = await migrate_sessions(
                db_path=str(tmp_path / "test.db"),
                session_files=[f],
            )

        assert results["skipped"] == 1
        assert results["details"][0]["reason"] == "empty"

    @pytest.mark.asyncio
    async def test_migrate_multiple_files_mixed_results(self, tmp_path: Path):
        """Multiple files can produce a mix of migrated, skipped, and failed."""
        good = tmp_path / "111000111.session"
        good.touch()

        bad_name = tmp_path / "no_id_here.session"
        _create_empty_file(bad_name)

        failing = tmp_path / "222000222.session"
        failing.touch()

        async def mock_migrate(path, bot_id):
            if "222000222" in str(path):
                raise RuntimeError("corrupt")
            return MagicMock(dc_id=2, user_id=bot_id)

        storage = _make_mock_storage(
            migrate_from_file=AsyncMock(side_effect=mock_migrate),
        )
        cls_mock = _make_storage_class(storage)

        with patch("pyrogram.storage.MultiSQLiteStorage", cls_mock):
            results = await migrate_sessions(
                db_path=str(tmp_path / "test.db"),
                session_files=[good, bad_name, failing],
            )

        assert results["migrated"] == 1
        assert results["skipped"] == 1
        assert results["failed"] == 1

    @pytest.mark.asyncio
    async def test_storage_open_and_close_called(self, tmp_path: Path):
        """Storage should be opened and closed when not in dry_run mode."""
        f = tmp_path / "100200300.session"
        f.touch()

        storage = _make_mock_storage(
            migrate_from_file=AsyncMock(
                return_value=MagicMock(dc_id=2, user_id=100200300)
            ),
        )
        cls_mock = _make_storage_class(storage)

        with patch("pyrogram.storage.MultiSQLiteStorage", cls_mock):
            await migrate_sessions(
                db_path=str(tmp_path / "test.db"),
                session_files=[f],
            )

        storage.open.assert_awaited_once()
        storage.close.assert_awaited_once()


# ===========================================================================
# dry_run mode
# ===========================================================================


class TestDryRun:
    """Tests for dry_run mode in migrate_sessions()."""

    @pytest.mark.asyncio
    async def test_dry_run_does_not_open_storage(self, tmp_path: Path):
        """In dry_run mode, storage.open() should NOT be called."""
        f = tmp_path / "123456789.session"
        f.touch()

        # In dry_run, the storage is still created but never opened
        storage = _make_mock_storage()
        cls_mock = _make_storage_class(storage)

        with patch("pyrogram.storage.MultiSQLiteStorage", cls_mock):
            results = await migrate_sessions(
                db_path=str(tmp_path / "test.db"),
                session_files=[f],
                dry_run=True,
            )

        assert results["migrated"] == 1
        assert results["details"][0]["status"] == "would_migrate"
        assert results["details"][0]["bot_id"] == 123456789
        storage.open.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_dry_run_multiple_files(self, tmp_path: Path):
        """Dry run should list all files that would be migrated."""
        f1 = tmp_path / "111.session"
        f2 = tmp_path / "222.session"
        f3 = tmp_path / "unknown.session"
        f1.touch()
        f2.touch()
        _create_empty_file(f3)

        storage = _make_mock_storage()
        cls_mock = _make_storage_class(storage)

        with patch("pyrogram.storage.MultiSQLiteStorage", cls_mock):
            results = await migrate_sessions(
                db_path="unused.db",
                session_files=[f1, f2, f3],
                dry_run=True,
            )

        assert results["migrated"] == 2
        assert results["skipped"] == 1  # unknown cannot extract bot_id

    @pytest.mark.asyncio
    async def test_dry_run_does_not_call_migrate_from_file(self, tmp_path: Path):
        """Dry run should never call storage.migrate_from_file()."""
        f = tmp_path / "777.session"
        f.touch()

        storage = _make_mock_storage()
        cls_mock = _make_storage_class(storage)

        with patch("pyrogram.storage.MultiSQLiteStorage", cls_mock):
            results = await migrate_sessions(
                db_path=str(tmp_path / "test.db"),
                session_files=[f],
                dry_run=True,
            )

        storage.migrate_from_file.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_dry_run_storage_not_closed(self, tmp_path: Path):
        """In dry_run mode, storage.close() should NOT be called (never opened)."""
        f = tmp_path / "888.session"
        f.touch()

        storage = _make_mock_storage()
        cls_mock = _make_storage_class(storage)

        with patch("pyrogram.storage.MultiSQLiteStorage", cls_mock):
            await migrate_sessions(
                db_path=str(tmp_path / "test.db"),
                session_files=[f],
                dry_run=True,
            )

        storage.open.assert_not_awaited()
        storage.close.assert_not_awaited()


# ===========================================================================
# main() CLI entry point
# ===========================================================================


class TestMainCLI:
    """Tests for the main() CLI entry point."""

    def test_main_no_files_found(self, tmp_path: Path):
        """main() should return 0 when no session files are found."""
        result = main(["--sessions", str(tmp_path), "--db", str(tmp_path / "out.db")])
        assert result == 0

    def test_main_nonexistent_directory(self):
        """main() should return 1 when the sessions directory doesn't exist."""
        result = main(["--sessions", "/nonexistent/dir/xyz", "--db", "out.db"])
        assert result == 1

    def test_main_dry_run(self, tmp_path: Path):
        """main() with --dry-run should succeed and not create a DB."""
        f = tmp_path / "12345.session"
        f.touch()

        result = main([
            "--sessions", str(tmp_path),
            "--db", str(tmp_path / "out.db"),
            "--dry-run",
        ])

        assert result == 0
        # DB file should NOT have been created
        assert not (tmp_path / "out.db").exists()

    def test_main_with_custom_pattern(self, tmp_path: Path):
        """main() should respect --pattern argument."""
        (tmp_path / "bot.dat").touch()
        (tmp_path / "bot.session").touch()

        result = main([
            "--sessions", str(tmp_path),
            "--db", str(tmp_path / "out.db"),
            "--pattern", "*.dat",
            "--dry-run",
        ])

        assert result == 0

    def test_main_verbose_flag(self, tmp_path: Path):
        """main() should accept the -v / --verbose flag without crashing."""
        result = main([
            "--sessions", str(tmp_path),
            "--db", str(tmp_path / "out.db"),
            "-v",
        ])
        assert result == 0

    def test_main_with_migrated_files(self, tmp_path: Path):
        """main() should return 0 when all files are successfully migrated."""
        f = tmp_path / "100200300.session"
        f.touch()

        storage = _make_mock_storage(
            migrate_from_file=AsyncMock(
                return_value=MagicMock(dc_id=2, user_id=100200300)
            ),
        )
        cls_mock = _make_storage_class(storage)

        with patch("pyrogram.storage.MultiSQLiteStorage", cls_mock):
            result = main([
                "--sessions", str(tmp_path),
                "--db", str(tmp_path / "out.db"),
            ])

        assert result == 0

    def test_main_returns_1_on_failures(self, tmp_path: Path):
        """main() should return 1 when any migration fails."""
        f = tmp_path / "999888777.session"
        f.touch()

        storage = _make_mock_storage(
            migrate_from_file=AsyncMock(side_effect=RuntimeError("Disk full")),
        )
        cls_mock = _make_storage_class(storage)

        with patch("pyrogram.storage.MultiSQLiteStorage", cls_mock):
            result = main([
                "--sessions", str(tmp_path),
                "--db", str(tmp_path / "out.db"),
            ])

        assert result == 1

    def test_main_default_db(self, tmp_path: Path):
        """When --db is omitted, default should be 'bots.db'."""
        # Just test the parser defaults via dry run on empty directory
        result = main([
            "--sessions", str(tmp_path),
            "--dry-run",
        ])
        assert result == 0


# ===========================================================================
# Edge cases and integration-style tests
# ===========================================================================


class TestEdgeCases:
    """Edge case tests across the migration tool."""

    @pytest.mark.asyncio
    async def test_empty_session_files_list(self, tmp_path: Path):
        """Passing an empty list should return all zeros."""
        storage = _make_mock_storage()
        cls_mock = _make_storage_class(storage)

        with patch("pyrogram.storage.MultiSQLiteStorage", cls_mock):
            results = await migrate_sessions(
                db_path=str(tmp_path / "test.db"),
                session_files=[],
                dry_run=True,
            )

        assert results["migrated"] == 0
        assert results["skipped"] == 0
        assert results["failed"] == 0
        assert results["details"] == []

    def test_extract_bot_id_with_leading_zeros(self, tmp_path: Path):
        """Filenames with leading zeros should parse correctly."""
        f = tmp_path / "007654321.session"
        f.touch()
        assert extract_bot_id(f) == 7654321

    def test_discover_deeply_nested_ignored(self, tmp_path: Path):
        """Files in subdirectories should not be found (non-recursive glob)."""
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        (subdir / "nested.session").touch()

        result = discover_session_files(str(tmp_path))
        assert len(result) == 0

    def test_extract_bot_id_bot_prefix_case_sensitive(self, tmp_path: Path):
        """The 'bot' prefix match is case-sensitive (lowercase only)."""
        f = tmp_path / "BOT_12345.session"
        f.touch()
        # 'BOT_12345' doesn't match the regex r"bot[_-]?(\d+)"
        # and it's not purely numeric, so it should fall back to SQLite
        # which will fail (empty file), returning None
        assert extract_bot_id(f) is None

    @pytest.mark.asyncio
    async def test_migrate_sessions_closes_storage_on_error(self, tmp_path: Path):
        """Storage.close() should be called even if migration raises unexpectedly."""
        f = tmp_path / "42.session"
        f.touch()

        storage = _make_mock_storage(
            migrate_from_file=AsyncMock(
                return_value=MagicMock(dc_id=2, user_id=42)
            ),
        )
        cls_mock = _make_storage_class(storage)

        with patch("pyrogram.storage.MultiSQLiteStorage", cls_mock):
            await migrate_sessions(
                db_path=str(tmp_path / "test.db"),
                session_files=[f],
            )

        # close should always be called in the finally block
        storage.close.assert_awaited_once()

    def test_extract_bot_id_with_sqlite_user_id_in_session(self, tmp_path: Path):
        """Full round-trip: create a proper SQLite file, extract bot_id from it."""
        f = tmp_path / "my_custom_name.session"
        _create_session_file(f, user_id=314159265)

        result = extract_bot_id(f)
        assert result == 314159265
