#!/usr/bin/env bash
# Deploy AgenticEdge blog to VPS
# Usage: ./deploy.sh rob@your-vps-ip

set -euo pipefail

REMOTE="${1:?Usage: ./deploy.sh rob@your-vps-ip}"
APP_DIR="/opt/starlette_blog"

echo "==> Creating app directory on remote ..."
ssh -t "$REMOTE" "sudo mkdir -p $APP_DIR && sudo chown \$(whoami):\$(whoami) $APP_DIR"

echo "==> Syncing files to $REMOTE:$APP_DIR ..."
rsync -avz --exclude='venv' --exclude='__pycache__' --exclude='.secret_key' \
    -e ssh ./ "$REMOTE:$APP_DIR/"

echo "==> Setting up on remote ..."
ssh -t "$REMOTE" bash -s "$APP_DIR" << 'REMOTE_SCRIPT'
APP_DIR="$1"
set -euo pipefail

# Create venv + install deps if needed
if [ ! -d "$APP_DIR/venv" ]; then
    echo "  Creating virtualenv ..."
    python3 -m venv "$APP_DIR/venv"
fi
echo "  Installing dependencies ..."
"$APP_DIR/venv/bin/pip" install -q -r "$APP_DIR/requirements.txt"

# Generate sample data if posts.json is missing
if [ ! -f "$APP_DIR/data/posts.json" ]; then
    echo "  Generating sample data ..."
    cd "$APP_DIR" && "$APP_DIR/venv/bin/python" generate_samples.py
fi

# Fix ownership
sudo chown -R www-data:www-data "$APP_DIR"

# Install systemd service
sudo cp "$APP_DIR/deploy/starlette_blog.service" /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable starlette_blog
sudo systemctl restart starlette_blog
echo "  Service restarted."

# Install nginx config
sudo cp "$APP_DIR/deploy/agenticedge.us.nginx" /etc/nginx/sites-available/agenticedge.us
sudo ln -sf /etc/nginx/sites-available/agenticedge.us /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
echo "  Nginx reloaded."

echo "==> Done! Site is live at https://agenticedge.us"
REMOTE_SCRIPT
