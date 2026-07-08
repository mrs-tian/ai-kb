import paramiko

HOST = "59.110.10.135"
PORT = 22
USER = "root"
PASSWORD = "super@test001"

COMMANDS = [
    "uname -a",
    "ls -la /etc/nginx/sites-enabled/ 2>/dev/null || ls -la /etc/nginx/conf.d/",
    "grep -R 'easytransfer' -l /etc/nginx/ 2>/dev/null || true",
    "for f in /etc/nginx/sites-enabled/* /etc/nginx/conf.d/*; do [ -f \"$f\" ] && echo '---' $f '---' && cat \"$f\"; done",
    "nginx -t 2>&1",
    "systemctl list-units --type=service --state=running | head -40",
    "ls -la /opt/ /var/www/ 2>/dev/null || true",
    "python3 --version 2>&1; node --version 2>&1; npm --version 2>&1; git --version 2>&1",
    "df -h /",
    "free -h",
    "ss -tlnp | head -30",
]

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, port=PORT, username=USER, password=PASSWORD, timeout=20)

for cmd in COMMANDS:
    print(f"\n=== {cmd} ===")
    stdin, stdout, stderr = client.exec_command(cmd)
    out = stdout.read().decode("utf-8", errors="replace")
    err = stderr.read().decode("utf-8", errors="replace")
    if out:
        print(out.rstrip())
    if err:
        print("ERR:", err.rstrip())

client.close()
print("\nPROBE_OK")
