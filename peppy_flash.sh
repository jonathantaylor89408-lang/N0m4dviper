#!/data/data/com.termux/files/usr/bin/bash
# [PROPRIETARY & PATENT PENDING] Copyright (c) 2026 Jonathan Anthony Taylor (ViperGearLabs). All Rights Reserved.
set -e

WORKDIR="$HOME/storage/shared/Download"
BIN="$WORKDIR/peppy_recovery.bin"
ZIP="$WORKDIR/peppy_recovery.zip"
TARGET="${TARGET:-/dev/block/sdb}"

mkdir -p "$WORKDIR"
cd "$WORKDIR"

if [ ! -f "$BIN" ] || [ "$(stat -c%s "$BIN" 2>/dev/null || echo 0)" -lt 1000000000 ]; then
    echo "[*] Resolving live Peppy recovery URL..."
    URL=$(curl -sL "https://dl.google.com/dl/edgedl/chromeos/recovery/recovery.conf" | grep -E "url=.*_peppy_recovery" | head -n1 | cut -d= -f2- | tr -d '\r')
    if [ -z "$URL" ]; then
        URL="https://dl.google.com/dl/edgedl/chromeos/recovery/chromeos_12239.92.0_peppy_recovery_stable-channel_mp-v3.bin.zip"
    fi
    echo "[*] Fetching $URL"
    curl -fL -o "$ZIP" "$URL"
    echo "[*] Extracting payload to $BIN..."
    unzip -p "$ZIP" > "$BIN"
    rm -f "$ZIP"
else
    echo "[*] Found existing valid image: $BIN ($(du -h "$BIN" | cut -f1))"
fi

echo "[*] Verifying MBR (55aa) & GPT (EFI PART) signatures..."
python3 -c '
import sys
with open("'"$BIN"'", "rb") as f:
    f.seek(510); mbr = f.read(2).hex()
    f.seek(512); gpt = f.read(8)
print(f"    MBR: {mbr} | GPT: {gpt}")
if mbr != "55aa" or gpt != b"EFI PART":
    sys.exit("[!] Signature mismatch — aborting.")
'

if [ "$1" == "--write" ]; then
    if [ ! -b "$TARGET" ]; then
        echo "[!] Block device $TARGET not found. Check OTG connection or run lsblk."
        exit 1
    fi
    echo "[*] Writing $BIN -> $TARGET (bs=4M)..."
    dd if="$BIN" of="$TARGET" bs=4M status=progress conv=fsync
    sync
    echo "[+] Write complete. Verify with: dd if=$TARGET bs=512 count=2 2>/dev/null | xxd"
else
    echo "[*] Image staged and verified at $BIN. Pass --write to flash $TARGET."
fi
