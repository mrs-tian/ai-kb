#!/usr/bin/env bash
# 在服务器上执行：初始化 / 更新智问 AI 知识库
set -euo pipefail

APP_ROOT="/srv/ai-kb-demo"
BACKEND="$APP_ROOT/backend"
PYTHON="/opt/miniconda3/bin/python3.11"

echo "[1/8] 准备目录..."
mkdir -p "$APP_ROOT/www" "$BACKEND/data" "$BACKEND/uploads" /var/www/certbot

echo "[2/8] Python 虚拟环境..."
if [ ! -d "$BACKEND/.venv" ]; then
  "$PYTHON" -m venv "$BACKEND/.venv"
fi
# shellcheck disable=SC1091
source "$BACKEND/.venv/bin/activate"
pip install -U pip -q
pip install greenlet --only-binary=:all: -q
pip install -r "$BACKEND/requirements.txt" -q

if [ ! -f "$BACKEND/.env" ]; then
  cp "$APP_ROOT/deploy/env.production.example" "$BACKEND/.env"
fi
if grep -q "CHANGE_ME_ON_DEPLOY" "$BACKEND/.env"; then
  SECRET=$(openssl rand -hex 32)
  sed -i "s/CHANGE_ME_ON_DEPLOY/${SECRET}/" "$BACKEND/.env"
fi

echo "[3/8] 数据库迁移..."
cd "$BACKEND"
alembic upgrade head

echo "[4/8] 初始化管理员（若不存在）..."
python -c "from app.db.init_db import init_db; init_db()"

if [ "${SEED_DEMO:-0}" = "1" ]; then
  echo "[4b] 填充 Demo 数据..."
  python scripts/seed_demo_data.py || true
fi

echo "[5/8] systemd..."
cp "$APP_ROOT/deploy/ai-kb-api.service" /etc/systemd/system/ai-kb-api.service
systemctl daemon-reload
systemctl enable ai-kb-api
systemctl restart ai-kb-api
sleep 2

echo "[6/8] SSL 证书..."
if [ ! -f "/etc/letsencrypt/live/un.easytransfer.top/fullchain.pem" ]; then
  cat >/etc/nginx/conf.d/ai-kb-demo-temp.conf <<'EOF'
server {
    listen 80;
    listen [::]:80;
    server_name un.easytransfer.top;
    location /.well-known/acme-challenge/ { root /var/www/certbot; }
    location / { return 200 'ok'; add_header Content-Type text/plain; }
}
EOF
  nginx -t && systemctl reload nginx
  certbot certonly --webroot -w /var/www/certbot -d un.easytransfer.top \
    --non-interactive --agree-tos --register-unsafely-without-email
  rm -f /etc/nginx/conf.d/ai-kb-demo-temp.conf
fi

echo "[7/8] Nginx..."
cp "$APP_ROOT/deploy/nginx-un.easytransfer.conf" /etc/nginx/conf.d/ai-kb-demo.conf
nginx -t
systemctl reload nginx

echo "[8/8] 健康检查..."
curl -sf http://127.0.0.1:8001/health
echo
curl -sfI https://un.easytransfer.top/health | head -5 || curl -sfI http://127.0.0.1/health -H 'Host: un.easytransfer.top' | head -5

echo "部署完成: https://un.easytransfer.top"
