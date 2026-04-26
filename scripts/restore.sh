#!/bin/sh
# Restore a memory snapshot. Existing data is moved aside (not deleted)
# so the restore is reversible.
#
# Usage: restore.sh <tarball> [target-memory-dir]

set -eu

if [ $# -lt 1 ]; then
    echo "Usage: $0 <tarball> [target-memory-dir]" >&2
    exit 1
fi

TARBALL="$1"
SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
PROJECT_DIR=$(dirname "$SCRIPT_DIR")
TARGET="${2:-$PROJECT_DIR/memory}"

if [ ! -f "$TARBALL" ]; then
    echo "tarball not found: $TARBALL" >&2
    exit 1
fi

cd "$PROJECT_DIR"
echo "[restore] stopping mcp-memory…"
docker compose stop mcp-memory

ARCHIVED=""
if [ -e "$TARGET" ]; then
    ARCHIVED="$TARGET.before-restore-$(date +%Y%m%d-%H%M%S)"
    echo "[restore] moving existing $TARGET → $ARCHIVED"
    mv "$TARGET" "$ARCHIVED"
fi

echo "[restore] extracting $TARBALL → $(dirname "$TARGET")"
tar xzf "$TARBALL" -C "$(dirname "$TARGET")"

echo "[restore] starting mcp-memory…"
docker compose start mcp-memory

if [ -n "$ARCHIVED" ]; then
    echo "[restore] done. Previous data archived at $ARCHIVED — delete once you've verified the restore."
else
    echo "[restore] done."
fi
