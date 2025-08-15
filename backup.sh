#!/usr/bin/env bash
set -e
set -u
set -o pipefail

BACKUP_DIR="./backups"
TIME_BUFFER=7
TIMESTAMP="$(date +"%Y-%m-%d_%H-%M-%S")"

if [[ $# -lt 1 ]]; then
  echo "Use: $0 <dir_for_backup>"
  exit 1
fi

TARGET_DIR="$1"

if [[ ! -d "$TARGET_DIR" ]]; then
  echo "Error: The argument is not an existing folder: '$TARGET_DIR'"
  exit 2
fi

mkdir -p "$BACKUP_DIR"

LOG_FILE="$BACKUP_DIR/backup.log"
touch "$LOG_FILE" || { echo "Ошибка: не могу создать лог $LOG_FILE"; exit 3; }

exec > >(awk '{ print strftime("[%Y-%m-%d %H:%M:%S]"), $0 }' | tee -a "$LOG_FILE") 2>&1

echo "Backup start."
echo "Target: $TARGET_DIR"

SRC_PARENT="$(cd "$(dirname "$TARGET_DIR")" && pwd)"
SRC_BASE="$(basename "$TARGET_DIR")"
ARCHIVE_NAME="${SRC_BASE}_${TIMESTAMP}.tar.gz"
ARCHIVE_PATH="$BACKUP_DIR/$ARCHIVE_NAME"

tar -czf "$ARCHIVE_PATH" -C "$SRC_PARENT" "$SRC_BASE"
echo "Archive created: $ARCHIVE_PATH"

FOUND_OLD=0
while IFS= read -r f; do
  [[ -n "$f" ]] || continue
  FOUND_OLD=1
  echo "Deleting archive: $f"
  rm -f -- "$f"
done < <(find "$BACKUP_DIR" -maxdepth 1 -type f -name "${SRC_BASE}_*.tar.gz" -mtime +"$TIME_BUFFER" -print)

if [[ $FOUND_OLD -eq 0 ]]; then
  echo "No backups were found for deletion."
else
  echo "$FOUND_OLD archives deleted."
fi

echo "Backup completed."
