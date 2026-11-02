#!/data/data/com.termux/files/usr/bin/bash

echo "=================================================="
echo "   VIPER NODE // OTG RECOVERY FLASH PIPELINE      "
echo "=================================================="

# 1. Locate staged Peppy recovery payload
IMG=""
for path in "/sdcard/Download/peppy_recovery.bin" \
            "/sdcard/Download/recovery.bin" \
            "$HOME/storage/shared/Download/peppy_recovery.bin" \
            "$HOME/storage/shared/Download/recovery.bin"; do
    if [ -f "$path" ]; then
        IMG="$path"
        break
    fi
done

if [ -z "$IMG" ]; then
    echo "[!] ERROR: Recovery payload not found in /sdcard/Download/"
    exit 1
fi

SIZE_MB=$(du -m "$IMG" | cut -f1)
echo "[+] Payload Locked : $IMG (${SIZE_MB} MB)"

# 2. Verify MBR (55AA) Boot Signature
MAGIC=$(xxd -p -l 2 -s 510 "$IMG" 2>/dev/null)
if [ "$MAGIC" = "55aa" ]; then
    echo "[+] MBR Signature  : VALID (0x55AA)"
else
    echo "[*] MBR Check      : $MAGIC (Proceeding with raw image)"
fi

# 3. Enumerate JCD324 USB-C Hub & MicroSD Reader
echo "--------------------------------------------------"
echo "[*] Scanning USB OTG Bus..."
if command -v termux-usb >/dev/null 2>&1; then
    USB_LIST=$(termux-usb -l)
    echo "[+] Active USB Nodes: $USB_LIST"
fi

# 4. Check for raw block access (Root / Direct Block Mode)
TARGET_DEV=$(ls /dev/block/sd* 2>/dev/null | grep -E '^/dev/block/sd[a-z]$' | tail -n 1)

if [ -n "$TARGET_DEV" ] && [ -w "$TARGET_DEV" ]; then
    echo "[+] Direct Block Device Detected: $TARGET_DEV"
    echo "[*] Flashing recovery image via dd (bs=4M)..."
    dd if="$IMG" of="$TARGET_DEV" bs=4M status=progress conv=fsync
    sync
    echo "[+] FLASH COMPLETE. Safe to unplug OTG hub."
else
    echo "[!] Standard Android unrooted lock active on /dev/block/sd*."
    echo "[*] Routing payload to OTG hardware bridge..."
    
    # Trigger Android USB permission dialog if USB node is visible
    USB_NODE=$(termux-usb -l 2>/dev/null | tr -d '[]"' | cut -d',' -f1)
    if [ -n "$USB_NODE" ]; then
        echo "[*] Requesting USB hardware descriptor grant on $USB_NODE..."
        termux-usb -r "$USB_NODE"
    fi

    echo ""
    echo "[+] ACTION REQUIRED TO COMPLETE RAW WRITE:"
    echo "    1. Your JCD324 hub + microSD reader is active."
    echo "    2. If using EtchDroid for unrooted raw USB-C block bypass:"
    echo "       Select 'Write raw image' -> Pick:"
    echo "       $IMG"
    echo "    3. Select the USB Mass Storage device and flash."
fi
echo "=================================================="
