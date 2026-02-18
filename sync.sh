#!/usr/bin/env bash
# Sync code changes to VPS and restart the service
# Usage: ./sync.sh

set -euo pipefail

REMOTE="rob@agenticedge.us"
APP_DIR="/opt/starlette_blog"

echo "==> Syncing files ..."
rsync -rlz --no-group --no-times --exclude='venv' --exclude='__pycache__' --exclude='.secret_key' \
    --exclude='data/' --exclude='uploads/' --exclude='.mypy_cache/' \
    -e ssh ./ "$REMOTE:$APP_DIR/"

echo "==> Fixing ownership, updating nginx, and restarting ..."
ssh -t "$REMOTE" "sudo chown -R www-data:www-data $APP_DIR && sudo cp $APP_DIR/deploy/agenticedge.us.nginx /etc/nginx/sites-available/agenticedge.us && sudo nginx -t && sudo systemctl reload nginx && sudo systemctl restart starlette_blog"

echo "==> Done!"
