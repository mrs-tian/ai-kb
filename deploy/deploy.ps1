# 本地一键部署到生产（Windows PowerShell）
# 用法: powershell -ExecutionPolicy Bypass -File deploy/deploy.ps1
$ErrorActionPreference = "Stop"

$SERVER = "root@59.110.10.135"
$SSH_PORT = 22
$REMOTE = "/srv/ai-kb-demo"
$ROOT = Split-Path -Parent $PSScriptRoot

Write-Host "==> 构建前端..."
Push-Location "$ROOT\admin-web"
npm run build | Out-Host
Pop-Location

Write-Host "==> 打包..."
$STAGE = Join-Path $env:TEMP "ai-kb-demo-deploy"
if (Test-Path $STAGE) { Remove-Item $STAGE -Recurse -Force }
New-Item -ItemType Directory -Path "$STAGE\backend" -Force | Out-Null
New-Item -ItemType Directory -Path "$STAGE\deploy" -Force | Out-Null
New-Item -ItemType Directory -Path "$STAGE\www" -Force | Out-Null

Copy-Item "$ROOT\backend\app" "$STAGE\backend\app" -Recurse
Copy-Item "$ROOT\backend\alembic" "$STAGE\backend\alembic" -Recurse
Copy-Item "$ROOT\backend\scripts" "$STAGE\backend\scripts" -Recurse
Copy-Item "$ROOT\backend\alembic.ini" "$STAGE\backend\"
Copy-Item "$ROOT\backend\requirements.txt" "$STAGE\backend\"
Copy-Item "$ROOT\deploy\*" "$STAGE\deploy\" -Recurse
Copy-Item "$ROOT\admin-web\dist\*" "$STAGE\www\" -Recurse

$TAR = Join-Path $env:TEMP "ai-kb-demo.tgz"
if (Test-Path $TAR) { Remove-Item $TAR -Force }
tar -czf $TAR -C $STAGE .

Write-Host "==> 上传..."
ssh -p $SSH_PORT $SERVER "mkdir -p $REMOTE"
scp -P $SSH_PORT $TAR "${SERVER}:/tmp/ai-kb-demo.tgz"

Write-Host "==> 服务器安装..."
ssh -p $SSH_PORT $SERVER "set -e; mkdir -p $REMOTE; tar -xzf /tmp/ai-kb-demo.tgz -C $REMOTE; chmod +x $REMOTE/deploy/setup_server.sh; SEED_DEMO=1 bash $REMOTE/deploy/setup_server.sh"

Write-Host "==> 验证..."
ssh -p $SSH_PORT $SERVER "curl -sf http://127.0.0.1:8001/health; echo; systemctl is-active ai-kb-api"

Write-Host ""
Write-Host "部署完成: https://un.easytransfer.top"
Write-Host "H5: https://www.easytransfer.top"
Write-Host "SSH 免密: ssh -p 22 root@59.110.10.135"
