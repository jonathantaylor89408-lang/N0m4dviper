#!/usr/bin/env bash
# VIPER FLASH GATE // Peppy Recovery Raw Block Flasher
# Usage: bash viper_flash_gate.sh /dev/block/sdb

TARGET_ARG="${1:-}"
IMAGE_NAME="chromeos_12239.92.0_peppy_recovery_stable-channel_mp-v3.bin"
EXPECTED_SIZE=1526751232

echo "=================================================="
echo "    VIPER-NODE: Peppy OTG Raw Write Controller    "
echo "=================================================="

# 1. Locate image in shared storage or home workspace
IMG=$(find ~/storage/shared "$HOME" -name "$IMAGE_NAME" 2>/dev/null | head -1)
if [ -z "$IMG" ]; then
    IMG=$(find ~/storage/shared "$HOME" -name '*.bin' -size +1000M 2>/dev/null | head -1)
fi

if [ -z "$IMG" ]; then
    echo "[!] ERROR: Recovery image not found. Ensure peppy_recovery.bin is in ~/storage/shared/Download/"
    exit 1
fi
echo "[+] Target image located at: $IMG"

# 2. Verify file size and SHA256 checksum
SIZE=$(stat -c '%s' "$IMG" 2>/dev/null)
echo "[*] Verifying payload dimensions ($SIZE bytes)..."
if [ "$SIZE" != "$EXPECTED_SIZE" ]; then
    echo "[!] WARNING: File size mismatch ($SIZE bytes, expected $EXPECTED_SIZE)."
fi

echo "[*] Verifying cryptographic hash against Google release..."
if sha256sum "$IMG" | grep -q "c88019bdeceefd476a22a6535b8b71c3adc682b60f56ad0127eea3f7a70985bd"; then
    echo "[+] HASH VERIFIED: Official Google bytes confirmed."
else
    echo "[!] WARNING: Hash mismatch detected. Proceed with caution."
fi

# 3. Scan available block storage nodes
echo -e "\n[*] Scanning connected block devices:"
ls /dev/block/sd* /dev/block/mmcblk* 2>/dev/null || echo "[-] No standard block nodes exposed."

# 4. Execute root-level raw write stream
if ! command -v su >/dev/null 2>&1 || ! su -c true 2>/dev/null; then
    echo "[!] ERROR: Root (su) privileges required for raw block writes."
    exit 1
fi

if [ -z "$TARGET_ARG" ]; then
    echo -e "\n[?] No target node provided as argument."
    echo "    Run again with your target node: bash viper_flash_gate.sh /dev/block/sdb"
    exit 0
fi

case "$TARGET_ARG" in
    /dev/block/*|/dev/sd*)
        echo -e "\n[!] WARNING: This will completely overwrite $TARGET_ARG."
        echo "[*] Streaming image via dd with 4M blocks and fsync..."
        if su -c "dd if='$IMG' of='$TARGET_ARG' bs=4M conv=fsync status=progress"; then
            echo "[+] SUCCESS: Raw block write completed successfully."
        else
            echo "[!] FAILED: Raw block write encountered an error."
            exit 1
        fi
        ;;
    *)
        echo "[!] ERROR: Invalid target device node ($TARGET_ARG). Must be /dev/block/sdX or /dev/sdX."
        exit 1
        ;;
esac
