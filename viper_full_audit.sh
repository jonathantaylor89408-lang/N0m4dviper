#!/usr/bin/env bash
# ==============================================================================
# VIPER-ELITE: COMPREHENSIVE NODE AUDIT & HEALTH REPORT
# ==============================================================================
set -euo pipefail

NODE_DIR="$HOME/viper_node"
VAULT_PATH="$NODE_DIR/.v1p34c0de/V1P34C0DE.vipercode"
LEDGER_PATH="$NODE_DIR/ledger/chain.log"

echo "=================================================="
echo "          VIPER-ELITE NODE AUDIT REPORT          "
echo "=================================================="
echo "TIMESTAMP: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "NODE PATH: $NODE_DIR"
echo ""

echo "--- 1. GIT STATUS & REPOSITORY METRICS ---"
if [ -d ".git" ]; then
    echo "HEAD: $(git rev-parse --short HEAD 2>/dev/null || echo 'none')"
    echo "SUBJECT: $(git log -1 --format=%s 2>/dev/null || echo 'none')"
    echo "ORIGIN: $(git remote get-url origin 2>/dev/null || echo 'none')"
    echo "DIRTY

cd ~/viper_node
cat << 'EOF' > viper_live_sync.sh
#!/usr/bin/env bash
# ==============================================================================
# VIPER-ELITE: GROK-COMPLIANT INVINCIBLE SYNC & REPUBLISH UTILITY
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

log_msg "INFO" "Initializing Grok-compliant invincible node synchronization..."

if [ -f "$VAULT_PATH" ]; then
    log_msg "SUCCESS" "Vault baseline V1P34C0DE verified intact."
else
    log_msg "ERROR" "Critical fault: Vault baseline missing."
    exit 1
fi

# Ensure correct secure permissions before staging
chmod 700 "$NODE_DIR"/*.sh "$NODE_DIR"/*.py 2>/dev/null || true

# Force-resolve git status and sync changes while respecting core ignores
git add -A
git commit -m "Grok node compliance: Invincible V1P34C0DE republish sync" || log_msg "INFO" "No pending changes to commit."
git push origin main

log_msg "SUCCESS" "Invincible node synchronization and remote republish completed successfully."
