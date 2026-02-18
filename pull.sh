#!/usr/bin/env bash
# Pull posts, users, and uploads from remote server to local
# Usage: ./pull.sh

set -euo pipefail

REMOTE="rob@agenticedge.us"
APP_DIR="/opt/starlette_blog"

echo "==> Pulling data and uploads from $REMOTE ..."
rsync -rlz --no-group --no-times --delete \
    -e ssh "$REMOTE:$APP_DIR/data/" ./data/
rsync -rlz --no-group --no-times --delete \
    -e ssh "$REMOTE:$APP_DIR/uploads/" ./uploads/

echo "==> Done! Local data and uploads synced from remote."
