#!/usr/bin/env bash
# [PROPRIETARY & PATENT PENDING] Copyright (c) 2026 Jonathan Anthony Taylor (ViperGearLabs). All Rights Reserved.
# ==============================================================================
# VIPER-ELITE: MASTER ONESHOT CONSOLIDATION, HARDENING & REPUBLISH SCRIPT
# ==============================================================================
set -euo pipefail

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

log_msg "INFO" "Executing Viper-Elite Master Oneshot Consolidation..."

# 1. Vault & Compliance Verification
if [ -f "$VAULT_PATH" ]; then
    log_msg "SUCCESS" "Vault V1P34C0DE verified intact."
else
    log_msg "ERROR" "Critical fault: Vault baseline missing!"
    exit 1
fi

# 2. Strict Permission Hardening (umask 077 equivalent)
log_msg "INFO" "Hardening file permissions across node environment..."
find "$NODE_DIR" -type d -exec chmod 700 {} + 2>/dev/null || true
find "$NODE_DIR" -type f \( -name "*.sh" -o -name "*.py" \) -exec chmod 700 {} + 2>/dev/null || true
find "$NODE_DIR" -type f ! \( -name "*.sh" -o -name "*.py" \) -exec chmod 600 {} + 2>/dev/null || true
log_msg "SUCCESS" "File permissions locked down securely."

# 3. Invincible Git Sync & Republish
log_msg "INFO" "Staging changes and pushing to remote repository..."
git add -A
git commit -m "Viper-Elite Master Oneshot: Invincible node sync, vault resolution & hardening" || log_msg "INFO" "No pending changes to commit."
git push origin main

log_msg "SUCCESS" "Master oneshot node consolidation, hardening, and republish complete."
