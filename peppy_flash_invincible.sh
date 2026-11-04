#!/data/data/com.termux/files/usr/bin/bash
# [PROPRIETARY & PATENT PENDING] Copyright (c) 2026 Jonathan Anthony Taylor (ViperGearLabs). All Rights Reserved.
# VIPER :: INVINCIBLE RECOVERY WRITER :: ROOTLESS :: SELF-TARGETING
set -euo pipefail

BOARD="peppy"; PLATFORM="12239.92.0"
WORK="$HOME/viper_node/peppy"
ZIP="$WORK/peppy_recovery.zip"
EXPECTED_BYTES=1526751232
URL="https://dl.google.com/dl/edgedl/chromeos/recovery/chromeos_12105.100.1_peppy_recovery_stable-channel_mp-v3.bin.zip"

log(){ printf '[%s] %s\n' "$(date +%H:%M:%S)" "$*"; }
die(){ log "[!] $*"; exit 1; }

mkdir -p "$WORK"; cd "$WORK"

# ---------- 1. FETCH (retry x3, clean each time) ----------
fetch(){
  for i in 1 2 3; do
    log "Fetch attempt $i"
    rm -f "$ZIP"
    if curl -L --fail --retry 2 -o "$ZIP" "$URL"; then return 0; fi
    log "Attempt $i failed"; sleep 3
  done
  die "Fetch failed after 3 attempts — platform string may be stale"
}
[ -s "$ZIP" ] && log "Zip present, skipping fetch" || fetch

# ---------- 2. EXTRACT ----------
log "Extracting"
unzip -o "$ZIP" -d "$WORK" >/dev/null
BIN=$(find "$WORK" -maxdepth 1 -name '*.bin' -print -quit)
[ -n "$BIN" ] || die "No .bin inside zip"

# ---------- 3. VERIFY (size + magic, hard gate) ----------
SIZE=$(stat -c '%s' "$BIN")
log "Size: $SIZE / expected $EXPECTED_BYTES"
[ "$SIZE" -eq "$EXPECTED_BYTES" ] || die "Size mismatch — refusing to write"
MAGIC=$(head -c 4 "$BIN" | xxd -p)
log "Magic: $MAGIC"
[ "$MAGIC" = "33c0fa8e" ] || die "Bad MBR magic ($MAGIC) — not a recovery image"
log "SHA-256: $(sha256sum "$BIN" | cut -d' ' -f1)"

# ---------- 4. SELF-TARGET (find USB, exclude internal) ----------
find_target(){
  local cands
  cands=$(ls /dev/block/sd* 2>/dev/null | grep -vE 'sd[a-z][0-9]+$' || true)
  [ -n "$cands" ] || die "No USB block device. Attach OTG + grant USB in Termux:API"
  local n; n=$(echo "$cands" | wc -l)
  [ "$n" -eq 1 ] || die "Multiple targets: $(echo $cands) — set TARGET="
  echo "$cands"
}
TARGET="${TARGET:-$(find_target)}"
[ -b "$TARGET" ] || die "$TARGET not a block device"
log "Target: $TARGET"
log "Target size: $(blockdev --getsize64 "$TARGET" 2>/dev/null || echo '?') bytes"

# ---------- 5. WRITE (aligned, flushed, verified) ----------
log "Writing — DO NOT UNPLUG"
dd if="$BIN" of="$TARGET" bs=4M conv=fsync status=progress
sync

# ---------- 6. READBACK VERIFY ----------
log "Readback check (first 1 MiB)"
SRC=$(head -c 1048576 "$BIN" | sha256sum | cut -d' ' -f1)
DST=$(dd if="$TARGET" bs=1M count=1 2>/dev/null | sha256sum | cut -d' ' -f1)
[ "$SRC" = "$DST" ] && log "[+] Readback MATCH — stick is good" || die "Readback MISMATCH — rewrite"

log "[+] COMPLETE. Boot: Esc+Refresh, tap Power, Ctrl+D."
