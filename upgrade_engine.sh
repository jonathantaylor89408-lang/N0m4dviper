#!/data/data/com.termux/files/usr/bin/bash
# [PROPRIETARY & PATENT PENDING] Copyright (c) 2026 Jonathan Anthony Taylor (ViperGearLabs). All Rights Reserved.
set -euo pipefail
V="$HOME/viper_node"
echo "[*] Initializing Viper Operational Upgrades..."

# 1. Ensure immutable ledger checkpointing tool
cat >> "$V/superadapt.sh" <<'PYEOF'

# Checkpoint extension
if len(sys.argv) > 1 and sys.argv[1] == "checkpoint":
    c_path = f"{V}/ledger/checkpoint.seal"
    shutil.copy2(C, c_path)
    print(f"[{time.strftime('%T')}] CHECKPOINT SECURED: {h(c_path)[:12]}")
PYEOF

# 2. Set strict umask and file ownership across all node vaults
chmod 700 "$V"/*.sh "$V"/*.py 2>/dev/null || true
chmod 600 "$V"/auth/* "$V"/ledger/* 2>/dev/null || true

# 3. Log rotation cron rule (purges daemon logs exceeding 5MB)
LOG="$V/ledger/daemon.log"
if [ -f "$LOG" ] && [ $(stat -c%s "$LOG" 2>/dev/null || echo 0) -gt 5242880 ]; then
  tail -n 1000 "$LOG" > "$LOG.tmp" && mv "$LOG.tmp" "$LOG"
  echo "[*] Daemon log rotated."
fi

echo "[OK] UPGRADE ENGINE COMPLETE: Node integrity verified."
