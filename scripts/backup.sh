#!/bin/sh
# Daily snapshot of the ChromaDB memory store.
# Stops mcp-memory briefly, tars the data dir, restarts, then prunes old
# snapshots. Designed to run from Synology Task Scheduler at 03:00.

set -eu

SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
PROJECT_DIR=$(dirname "$SCRIPT_DIR")
BACKUP_DIR="$PROJECT_DIR/backups"
MEMORY_DIR="$PROJECT_DIR/memory"
LOG="$BACKUP_DIR/backup.log"

mkdir -p "$BACKUP_DIR"

log() {
    printf '[%s] %s\n' "$(date -Iseconds)" "$1" | tee -a "$LOG"
}

DATE=$(date +%F)
SNAPSHOT="$BACKUP_DIR/memory-$DATE.tar.gz"

if [ -f "$SNAPSHOT" ]; then
    log "snapshot for $DATE already exists at $SNAPSHOT; aborting"
    exit 0
fi

log "starting backup → $SNAPSHOT"

cd "$PROJECT_DIR"
docker compose stop mcp-memory
# Bring the container back up no matter how we exit from here.
trap 'docker compose start mcp-memory >/dev/null 2>&1 || true' EXIT INT TERM

tar czf "$SNAPSHOT.tmp" -C "$PROJECT_DIR" memory
mv "$SNAPSHOT.tmp" "$SNAPSHOT"

docker compose start mcp-memory
trap - EXIT INT TERM

SIZE=$(du -h "$SNAPSHOT" | cut -f1)
log "snapshot complete: $SNAPSHOT ($SIZE)"

python3 "$SCRIPT_DIR/prune_backups.py" "$BACKUP_DIR" --daily 7 --weekly 4 2>&1 | tee -a "$LOG"
log "backup done"
