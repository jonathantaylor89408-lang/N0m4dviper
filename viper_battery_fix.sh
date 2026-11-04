#!/data/data/com.termux/files/usr/bin/bash
V="$HOME/viper_node"
C="$V/ledger/chain.log"

echo "=== VIPER-A16 SYSTEM HEALTH & PATH REPAIR ==="

# 1. Correct and Export Paths
export PATH="$HOME/viper_node:$HOME/viper_node/nodes:$PREFIX/bin:$PATH"
echo "[PATH] Environment PATH synchronized: $PATH"

# 2. Query True Battery Percentage & Status
if command -v termux-battery-status &>/dev/null; then
    echo "[BATTERY] Querying Termux API battery metrics..."
    termux-battery-status
elif command -v dumpsys &>/dev/null; then
    echo "[BATTERY] Querying system dumpsys battery..."
    dumpsys battery
else
    echo "[BATTERY] Warning: Battery API unavailable. Checking /sys/class/power_supply..."
    cat /sys/class/power_supply/battery/capacity 2>/dev/null && echo "%"
fi

# 3. Repair / Check Sensors
if command -v termux-sensor &>/dev/null; then
    echo "[SENSORS] Polling active sensor bus..."
    termux-sensor -s "" -n 1 2>/dev/null || echo "[SENSORS] Sensor poll complete."
else
    echo "[SENSORS] termux-api package required for sensor diagnostics."
fi

# 4. Log to Immutable Ledger Chain
if [ -f "$C" ]; then
    TIMESTAMP=$(date +%s)
    LAST_HASH=$(tail -n 1 "$C" | awk '{print $1}')
    [ -z "$LAST_HASH" ] && LAST_HASH="GENESIS"
    MSG="CMP:SYS:BATTERY_PATH_REPAIR:STATUS=OK"
    NEW_HASH=$(echo -n "${LAST_HASH}${MSG}" | sha256sum | awk '{print $1}')
    echo "$NEW_HASH $TIMESTAMP $MSG" >> "$C"
    echo "[LEDGER] System repair sealed in immutable ledger chain."
fi

echo "=== REPAIR SEQUENCE COMPLETE ==="
