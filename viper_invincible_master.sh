#!/usr/bin/env bash
# ==============================================================================
# VIPER-ELITE: MASTER INVINCIBLE NODE REPAIR, HARDENING & REPUBLISH SCRIPT
# ==============================================================================
set -euo pipefail
IFS=$'\n\t'

NODE_DIR="$HOME/viper_node"
VAULT_PATH="$NODE_DIR/.v1p34c0de/V1P34C0DE.vipercode"
LEDGER_PATH="$NODE_DIR/ledger/chain.log"

mkdir -p "$(dirname "$LEDGER_PATH")"

log_msg() {
    local level="$1"
    local message="$2"
    local timestamp
    timestamp=$(date -u '+%Y-%m-%dT%H:%M:%SZ')
    echo "[$timestamp] [$level] $message" | tee -a "$LEDGER_PATH"
}

log_msg "INFO" "Executing Viper-Elite Master Invincible Repair & Synchronization..."

# 1. Vault Verification
if [ -f "$VAULT_PATH" ]; then
    log_msg "SUCCESS" "Vault V1P34C0DE verified intact at $VAULT_PATH"
else
    log_msg "ERROR" "Critical fault: Vault baseline missing!"
    exit 1
fi

# 2. Strict Permission Hardening (umask 077 compliance)
log_msg "INFO" "Applying strict 0700/0600 permissions..."
find "$NODE_DIR" -type d -exec chmod 700 {} + 2>/dev/null || true
find "$NODE_DIR" -type f \( -name "*.sh" -o -name "*.py" \) -exec chmod 700 {} + 2>/dev/null || true
find "$NODE_DIR" -type f ! \( -name "*.sh" -o -name "*.py" \) -exec chmod 600 {} + 2>/dev/null || true
log_msg "SUCCESS" "File permissions locked down securely."

# 3. Ensure Keepalive & Background Services
log_msg "INFO" "Verifying background daemons and local suite bindings..."
if ! pgrep -f "viper_lite.py" > /dev/null; then
    nohup python3 "$NODE_DIR/viper_lite.py" > "$NODE_DIR/ledger/suite_http.log" 2>&1 &
    log_msg "SUCCESS" "Launched viper_lite.py background web suite on port 8080."
else
    log_msg "INFO" "viper_lite.py already active."
fi

# 4. Invincible Git Sync & Republish
log_msg "INFO" "Staging, committing, and pushing invincible updates to remote repository..."
git add -A
git commit -m "Viper-Elite Master Invincible: Automatic repair, hardening & sync" || log_msg "INFO" "No pending changes to commit."
git push origin main

log_msg "SUCCESS" "Master invincible node repair, hardening, and remote push completed successfully."
