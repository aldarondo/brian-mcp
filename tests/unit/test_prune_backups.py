"""Unit tests for scripts/prune_backups.py."""
from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from scripts.prune_backups import main, parse_backup_date, select_to_keep  # noqa: E402


def _fake(d: date) -> tuple[date, Path]:
    return d, Path(f"memory-{d}.tar.gz")


class TestParseBackupDate:
    def test_valid(self):
        assert parse_backup_date("memory-2026-04-26.tar.gz") == date(2026, 4, 26)

    def test_wrong_prefix(self):
        assert parse_backup_date("backup-2026-04-26.tar.gz") is None

    def test_wrong_extension(self):
        assert parse_backup_date("memory-2026-04-26.tar") is None

    def test_garbage(self):
        assert parse_backup_date("memory-bad.tar.gz") is None

    def test_invalid_date(self):
        assert parse_backup_date("memory-2026-13-40.tar.gz") is None


class TestSelectToKeep:
    def test_keeps_all_within_daily_window(self):
        today = date(2026, 4, 26)
        backups = [_fake(date(2026, 4, 26 - i)) for i in range(7)]
        keep = select_to_keep(backups, today, daily=7, weekly=4)
        assert len(keep) == 7
        assert {p.name for _, p in backups} == {p.name for p in keep}

    def test_drops_files_outside_both_windows(self):
        today = date(2026, 4, 26)
        backups = [
            _fake(date(2026, 4, 26)),
            _fake(date(2025, 1, 1)),
        ]
        keep = select_to_keep(backups, today, daily=7, weekly=0)
        names = {p.name for p in keep}
        assert names == {"memory-2026-04-26.tar.gz"}

    def test_weekly_keeps_newest_within_a_week(self):
        today = date(2026, 4, 26)
        # Both 4/13 (Mon) and 4/12 (Sun) are >7 days out; ISO weeks differ
        # for these two dates so use two same-week dates instead.
        backups = [
            _fake(date(2026, 4, 13)),  # Mon — ISO 2026-W16
            _fake(date(2026, 4, 17)),  # Fri — ISO 2026-W16, but only 9d old
        ]
        keep = select_to_keep(backups, today, daily=7, weekly=4)
        names = {p.name for p in keep}
        assert names == {"memory-2026-04-17.tar.gz"}

    def test_weekly_caps_at_limit(self):
        today = date(2026, 4, 26)
        backups = [
            _fake(date(2026, 4, 12)),
            _fake(date(2026, 4, 5)),
            _fake(date(2026, 3, 29)),
            _fake(date(2026, 3, 22)),
            _fake(date(2026, 3, 15)),
            _fake(date(2026, 3, 8)),
        ]
        keep = select_to_keep(backups, today, daily=7, weekly=4)
        names = sorted(p.name for p in keep)
        assert names == [
            "memory-2026-03-22.tar.gz",
            "memory-2026-03-29.tar.gz",
            "memory-2026-04-05.tar.gz",
            "memory-2026-04-12.tar.gz",
        ]

    def test_ignores_future_dates(self):
        today = date(2026, 4, 26)
        backups = [
            _fake(date(2026, 4, 26)),
            _fake(date(2099, 1, 1)),
        ]
        keep = select_to_keep(backups, today, daily=7, weekly=4)
        names = {p.name for p in keep}
        assert names == {"memory-2026-04-26.tar.gz"}

    def test_empty_input(self):
        assert select_to_keep([], date(2026, 4, 26), 7, 4) == set()

    def test_combined_daily_plus_weekly(self):
        today = date(2026, 4, 26)
        backups = [_fake(date(2026, 4, 26 - i)) for i in range(7)]
        backups += [
            _fake(date(2026, 4, 12)),
            _fake(date(2026, 4, 5)),
            _fake(date(2026, 3, 29)),
            _fake(date(2026, 3, 22)),
            _fake(date(2026, 3, 1)),  # would be 5th weekly slot, dropped
        ]
        keep = select_to_keep(backups, today, daily=7, weekly=4)
        assert len(keep) == 11
        assert Path("memory-2026-03-01.tar.gz") not in keep


class TestMainCli:
    def _seed(self, tmp_path: Path, dates: list[date]) -> list[Path]:
        paths = []
        for d in dates:
            p = tmp_path / f"memory-{d}.tar.gz"
            p.write_bytes(b"x")
            paths.append(p)
        return paths

    def test_deletes_expired_files(self, tmp_path: Path, capsys):
        self._seed(tmp_path, [date(2026, 4, 26), date(2025, 1, 1)])
        rc = main([str(tmp_path), "--daily", "7", "--weekly", "0", "--today", "2026-04-26"])
        assert rc == 0
        remaining = sorted(p.name for p in tmp_path.iterdir())
        assert remaining == ["memory-2026-04-26.tar.gz"]

    def test_dry_run_keeps_files(self, tmp_path: Path):
        self._seed(tmp_path, [date(2026, 4, 26), date(2025, 1, 1)])
        rc = main([str(tmp_path), "--daily", "7", "--weekly", "0", "--today", "2026-04-26", "--dry-run"])
        assert rc == 0
        assert len(list(tmp_path.iterdir())) == 2

    def test_ignores_unrelated_files(self, tmp_path: Path):
        (tmp_path / "memory-2026-04-26.tar.gz").write_bytes(b"x")
        (tmp_path / "backup.log").write_text("log")
        (tmp_path / "memory-bad.tar.gz").write_bytes(b"x")
        rc = main([str(tmp_path), "--today", "2026-04-26"])
        assert rc == 0
        names = sorted(p.name for p in tmp_path.iterdir())
        assert "backup.log" in names
        assert "memory-bad.tar.gz" in names

    def test_missing_dir_returns_nonzero(self, tmp_path: Path):
        rc = main([str(tmp_path / "nope")])
        assert rc != 0
