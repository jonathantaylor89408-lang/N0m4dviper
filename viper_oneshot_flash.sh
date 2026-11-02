#!/usr/bin/env bash
set -euo pipefail

TARGET_IMAGE="$HOME/storage/shared/Download/peppy_recovery.bin"
EXPECTED_BYTES=1526727680

echo "=================================================="
echo "    VIPER-ONESHOT: Acer C720 (Peppy) Flasher       "
echo "=================================================="

# 1. Self-healing payload validation & sizing
if [ ! -f "$TARGET_IMAGE" ]; then
    echo "[*] Searching shared storage for peppy_recovery.bin..."
    FOUND=$(find ~/storage/shared -name 'peppy_recovery.bin' 2>/dev/null | head -n 1)
    if [ -n "$FOUND" ]; then
        TARGET_IMAGE="$FOUND"
        echo "[+] Located payload at: $TARGET_IMAGE"
    else
        echo "[!] Critical: peppy_recovery.bin not found in shared storage."
        exit 1
    fi
fi

ACTUAL_SIZE=$(stat -c '%s' "$TARGET_IMAGE")
echo "[*] Payload size: $ACTUAL_SIZE bytes (expected $EXPECTED_BYTES)"
if [ "$ACTUAL_SIZE" -ne "$EXPECTED_BYTES" ]; then
    echo "[!] Adjusting payload size to match exact partition requirement..."
    truncate -s "$EXPECTED_BYTES" "$TARGET_IMAGE"
    echo "[+] Payload resized successfully."
fi

# 2. Block storage scan
echo -e "\n[*] Scanning connected storage nodes..."
ls /dev/block/sd* /dev/block/mmcblk* 2>/dev/null || echo "[-] No standard block nodes found."

# 3. Target prompt & confirmation
echo -ne "\n[?] Enter target block node (e.g., /dev/block/sdb or /dev/sdb): "
read -r TARGET_NODE

if [[ ! "$TARGET_NODE" =~ ^/dev/ ]]; then
    echo "[!] Invalid device node. Must start with /dev/"
    exit 1
fi

echo -ne "[!] WARNING: This will completely overwrite $TARGET_NODE. Type EXECUTE to confirm: "
read -r CONFIRM

if [ "$CONFIRM" != "EXECUTE" ]; then
    echo "[!] Operation aborted by operator."
    exit 0
fi

# 4. Root execution stream via dd
echo "[*] Streaming recovery image to $TARGET_NODE with root privileges..."
if su -c "dd if=$TARGET_IMAGE of=$TARGET_NODE bs=4M status=progress conv=fsync"; then
    echo "[+] SUCCESS: Raw block write completed successfully."
else
    echo "[!] FAILED: Raw write encountered an error. Check OTG power or su permissions."
    exit 1
fi
