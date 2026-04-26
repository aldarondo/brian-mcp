"""Prune memory snapshots, keeping daily and weekly retention.

Filenames must match memory-YYYY-MM-DD.tar.gz. Anything else in the
directory is ignored.
"""
from __future__ import annotations

import argparse
import re
import sys
from datetime import date, timedelta
from pathlib import Path

NAME_RE = re.compile(r"^memory-(\d{4})-(\d{2})-(\d{2})\.tar\.gz$")


def parse_backup_date(filename: str) -> date | None:
    m = NAME_RE.match(filename)
    if not m:
        return None
    try:
        return date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    except ValueError:
        return None


def select_to_keep(
    backups: list[tuple[date, Path]],
    today: date,
    daily: int,
    weekly: int,
) -> set[Path]:
    """Keep all snapshots within the last `daily` days, plus the newest
    snapshot in each of the `weekly` most recent ISO weeks beyond that.
    """
    keep: set[Path] = set()
    daily_cutoff = today - timedelta(days=daily)
    weekly_buckets: dict[tuple[int, int], tuple[date, Path]] = {}

    for d, path in backups:
        if d > today:
            continue
        if d > daily_cutoff:
            keep.add(path)
            continue
        iso = d.isocalendar()
        bucket = (iso.year, iso.week)
        cur = weekly_buckets.get(bucket)
        if cur is None or cur[0] < d:
            weekly_buckets[bucket] = (d, path)

    for bucket in sorted(weekly_buckets.keys(), reverse=True)[:weekly]:
        keep.add(weekly_buckets[bucket][1])

    return keep


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("backup_dir")
    p.add_argument("--daily", type=int, default=7)
    p.add_argument("--weekly", type=int, default=4)
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--today", help="YYYY-MM-DD; for testing")
    args = p.parse_args(argv)

    today = date.fromisoformat(args.today) if args.today else date.today()
    backup_dir = Path(args.backup_dir)
    if not backup_dir.is_dir():
        print(f"backup dir not found: {backup_dir}", file=sys.stderr)
        return 1

    backups: list[tuple[date, Path]] = []
    for path in backup_dir.iterdir():
        d = parse_backup_date(path.name)
        if d is not None:
            backups.append((d, path))

    keep = select_to_keep(backups, today, args.daily, args.weekly)
    deleted: list[str] = []
    for _, path in backups:
        if path not in keep:
            if not args.dry_run:
                path.unlink()
            deleted.append(path.name)

    action = "would delete" if args.dry_run else "deleted"
    print(f"kept {len(keep)} of {len(backups)}; {action} {len(deleted)}: {sorted(deleted)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
