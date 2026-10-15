#!/bin/zsh
# One-time: store the Atlassian API token in the macOS Keychain.
# The token is typed at a hidden prompt, never passed on the command line,
# so it never lands in shell history, the vault, or git.
#
# Use a CLASSIC token ("Create API token", NOT "with scopes"): the sync uses
# Basic auth (email:token) against the site URL, which only classic tokens
# support. Get one at:
#   https://id.atlassian.com/manage-profile/security/api-tokens
# Re-run any time the token is rotated (it replaces the existing item).
#
# Why Python/keyring instead of `security add-generic-password -w`:
# the `security` CLI's hidden prompt silently truncates input at 128 chars,
# which mangles long Atlassian tokens. Python's getpass has no such cap,
# and keyring writes via the native Keychain API (no cap, no argv exposure).
#
# CONFIG: replace the placeholder below; it must equal KEYCHAIN_SERVICE in sync.py.
set -uo pipefail

ITEM="__KEYCHAIN_SERVICE__"

# Require an interactive terminal: getpass needs a real prompt to read the
# token securely.
if [[ ! -t 0 ]]; then
  echo "error: run this in an interactive Terminal, not via a pipe or a" >&2
  echo "       non-interactive shell." >&2
  exit 1
fi

if ! command -v uv >/dev/null 2>&1; then
  echo "error: 'uv' not found. Install it: https://docs.astral.sh/uv/" >&2
  exit 1
fi

# Remove any prior (possibly truncated) item so exactly one clean copy remains.
security delete-generic-password -a "$USER" -s "$ITEM" >/dev/null 2>&1 || true

# Read the token with Python getpass (no length cap) and store it via keyring's
# native Keychain API. sync.py reads it back through the same keyring library.
exec uv run --with keyring python3 - "$ITEM" "$USER" <<'PY'
import sys, getpass, keyring

item, user = sys.argv[1], sys.argv[2]
token = getpass.getpass("Paste the CLASSIC Atlassian API token (hidden), then Enter: ").strip()
if not token:
    raise SystemExit("error: empty token - nothing stored.")

keyring.set_password(item, user, token)

# Verify it reads back intact before claiming success.
back = keyring.get_password(item, user) or ""
if back != token:
    raise SystemExit("error: token did not read back intact - nothing usable stored.")

print(f"\nStored {len(token)} chars. Run: uv run scripts/optional/confluence/sync.py")
PY
