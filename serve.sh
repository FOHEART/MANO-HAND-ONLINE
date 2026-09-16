#!/usr/bin/env sh
# ============================================================
#  One-click dev server for MANO HAND ONLINE (macOS / Linux).
#  Run:  ./serve.sh            (or: sh serve.sh --port 9000)
#  On macOS you can also double-click this file if it ends in
#  .command — see README.
# ============================================================
set -e
cd "$(dirname "$0")"

for py in python3 python py; do
    if command -v "$py" >/dev/null 2>&1; then
        exec "$py" serve.py "$@"
    fi
done

echo "Python 3 was not found on PATH." >&2
echo "Install it from https://www.python.org/downloads/ and try again." >&2
exit 1
