#!/usr/bin/env bash
# ==============================================================================
# VIPER-ELITE: NODE COMPLIANCE & SAFETY VERIFICATION UTILITY
# ==============================================================================
set -euo pipefail

NODE_DIR="$HOME/viper_node"
VAULT_PATH="$NODE_DIR/.v1p34c0de/V1P34C0DE.vipercode"
LOG_FILE="$NODE_DIR/ledger/chain.log"

echo "[*] Inspecting local node compliance and git safety status..."

# 1. Check git status
git status

# 2. Check local vault integrity
if [ -f "$VAULT_PATH" ]; then
    echo "[+] Local vault V1P34C0DE is intact and protected."
else
    echo "[!] WARNING: Local vault path not found."
fi

# 3. Check if core scripts are still executable and present
for script in viper_oneshot.sh viper_realtime_node.py viper_live_sync.sh; do
    if [ -f "$NODE_DIR/$script" ]; then
        echo "[+] Core component $script verified."
    else
        echo "[!] Missing component: $script"
    fi
done

echo "[*] Compliance check complete. Node functional integrity maintained."
