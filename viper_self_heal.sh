#!/data/data/com.termux/files/usr/bin/bash
# ==============================================================================
# VIPER-A16 // Local Self-Heal, Change Detection & V1P34C0DE Override Updater
# Directives: Local execution only. No remote pushes. Silent ledger logging.
# ==============================================================================

V="$HOME/viper_node"
VAULT_DIR="$V/.v1p34c0de"
ARCHIVE="$VAULT_DIR/V1P34C0DE.vipercode"
MANIFEST="$VAULT_DIR/manifest.sha256"
LEDGER="$V/ledger/chain.log"

cd "$V" || exit 1
mkdir -p "$VAULT_DIR" "$V/ledger"

TARGETS=("viper_daemon.py" "net_harden.sh" "viper_battery_fix.sh" "rush" "Makefile")

log_event() {
    local MSG="$1"
    if [ -f "$LEDGER" ]; then
        local TIMESTAMP=$(date +%s)
        local LAST_HASH=$(tail -n 1 "$LEDGER" | awk '{print $1}')
        [ -z "$LAST_HASH" ] && LAST_HASH="GENESIS"
        local NEW_HASH=$(echo -n "${LAST_HASH}${MSG}" | sha256sum | awk '{print $1}')
        echo "$NEW_HASH $TIMESTAMP $MSG" >> "$LEDGER"
    fi
}

build_vipercode() {
    local EXISTING=()
    for f in "${TARGETS[@]}"; do
        [ -f "$V/$f" ] && EXISTING+=("$f")
    done
    if [ ${#EXISTING[@]} -gt 0 ]; then
        sha256sum "${EXISTING[@]}" > "$MANIFEST" 2>/dev/null
        tar -czf - "${EXISTING[@]}" 2>/dev/null | base64 > "$ARCHIVE"
        chmod 600 "$MANIFEST" "$ARCHIVE"
        log_event "CMP:V1P34C0DE:ARCHIVE_SEALED:STATUS=OK"
    fi
}

restore_from_vipercode() {
    if [ -f "$ARCHIVE" ]; then
        base64 -d "$ARCHIVE" | tar -xzf - -C "$V" 2>/dev/null
        chmod 700 "$V"/*.sh "$V"/*.py 2>/dev/null
        log_event "CMP:V1P34C0DE:OVERRIDE_RESTORE:STATUS=RECOVERED"
    fi
}

# 1. Handle Explicit Override / Reseal Flags
if [ "$1" == "--seal" ] || [ ! -f "$ARCHIVE" ]; then
    build_vipercode
    exit 0
elif [ "$1" == "--override" ]; then
    restore_from_vipercode
    exit 0
fi

# 2. Silent Change Detection & Self-Heal Loop
if [ -f "$MANIFEST" ]; then
    if ! sha256sum -c "$MANIFEST" --status 2>/dev/null; then
        restore_from_vipercode
    fi
fi

# 3. Verify Background Daemon Continuity
if ! pgrep -f "viper_daemon.py" >/dev/null 2>&1; then
    if [ -f "$V/viper_daemon.py" ]; then
        nohup python3 "$V/viper_daemon.py" >/dev/null 2>&1 &
        log_event "CMP:SELF_HEAL:DAEMON_RESTART:STATUS=OK"
    fi
fi
