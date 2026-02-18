#!/usr/bin/env bash
# Compare local code files against what's on the server
# Usage: ./diff.sh

set -euo pipefail

REMOTE="rob@agenticedge.us"
APP_DIR="/opt/starlette_blog"
TMPDIR=$(mktemp -d)

echo "==> Fetching server files to $TMPDIR ..."
rsync -rlz --no-group --no-times \
    --exclude='venv' --exclude='__pycache__' --exclude='.secret_key' \
    --exclude='data/' --exclude='uploads/' --exclude='.mypy_cache/' \
    -e ssh "$REMOTE:$APP_DIR/" "$TMPDIR/"

echo ""
echo "==> Diffing local vs server ..."
echo ""
diff -rq --exclude='venv' --exclude='__pycache__' --exclude='.secret_key' \
    --exclude='data' --exclude='uploads' --exclude='.mypy_cache' \
    . "$TMPDIR" || true

echo ""
echo "==> Detailed diffs:"
echo ""
diff -ru --exclude='venv' --exclude='__pycache__' --exclude='.secret_key' \
    --exclude='data' --exclude='uploads' --exclude='.mypy_cache' \
    . "$TMPDIR" || true

rm -rf "$TMPDIR"
echo ""
echo "==> Done."
