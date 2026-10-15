#!/bin/zsh
# Generate today's daily brief headless, then let your git plugin commit it.
# Scheduled by a LaunchAgent (see daily-brief.plist; weekdays 08:30).
# Run manually any time:  zsh scripts/optional/daily-brief.sh
set -uo pipefail

VAULT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:$PATH"
CLAUDE="$(command -v claude || echo "$HOME/.local/bin/claude")"
LOG="$VAULT_DIR/daily/.brief.log"

cd "$VAULT_DIR" || exit 1
{
  echo "=== $(date '+%Y-%m-%d %H:%M:%S') daily-brief start ==="
  "$CLAUDE" -p "/daily" --permission-mode acceptEdits
  rc=$?
  echo "=== $(date '+%Y-%m-%d %H:%M:%S') daily-brief done (exit $rc) ==="
  echo
} >> "$LOG" 2>&1
