#!/usr/bin/env python3
# [PROPRIETARY & PATENT PENDING] Copyright (c) 2026 Jonathan Anthony Taylor (ViperGearLabs). All Rights Reserved.
import os, sys, subprocess

TARGET_IMAGE = os.path.expanduser("~/storage/shared/Download/peppy_recovery.bin")
EXPECTED_BYTES = 1526727680

def run_cmd(cmd):
    res = subprocess.run(cmd, shell=True, text=True, capture_output=True)
    return res.returncode, res.stdout.strip(), res.stderr.strip()

def verify_payload():
    print("[*] Phase 1: Validating recovery payload...")
    if not os.path.exists(TARGET_IMAGE):
        print(f"[!] Error: payload missing at {TARGET_IMAGE}")
        print("[*] Self-healing: searching shared storage...")
        rc, out, err = run_cmd("find ~/storage/shared -name 'peppy_recovery.bin' 2>/dev/null")
        if out:
            print(f"[+] Found: {out}")
            return out.splitlines()[0]
        print("[-] Not found. Abort.")
        return None
    size = os.path.getsize(TARGET_IMAGE)
    print(f"[*] Payload size: {size} bytes (expected {EXPECTED_BYTES})")
    if size != EXPECTED_BYTES:
        print("[!] Size mismatch — payload may be truncated.")
    else:
        print("[+] Size OK.")
    return TARGET_IMAGE

def scan_devices():
    print("[*] Phase 2: Scanning block devices...")
    rc, out, err = run_cmd("ls /dev/block/sd* /dev/block/mmcblk* 2>/dev/null")
    for line in out.splitlines():
        print(f"    {line}")
    return out.splitlines()

if __name__ == "__main__":
    img = verify_payload()
    if not img:
        sys.exit(1)
    scan_devices()
    print("[+] Harness complete.")
