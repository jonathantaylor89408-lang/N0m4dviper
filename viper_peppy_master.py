#!/usr/bin/env python3
import os
import sys
import subprocess

TARGET_IMAGE = os.path.expanduser("~/storage/shared/Download/peppy_recovery.bin")
EXPECTED_BYTES = 1526727680

def run_cmd(cmd):
    res = subprocess.run(cmd, shell=True, text=True, capture_output=True)
    return res.returncode, res.stdout.strip(), res.stderr.strip()

def verify_payload():
    print("[*] Phase 1: Validating Peppy Recovery Payload...")
    if not os.path.exists(TARGET_IMAGE):
        print(f"[!] Error: Recovery payload missing at {TARGET_IMAGE}")
        print("[*] Self-Healing: Locating recovery.bin in shared storage...")
        alt = subprocess.run("find ~/storage/shared -name 'peppy_recovery.bin' 2>/dev/null", shell=True, text=True, capture_output=True)
        if alt.stdout.strip():
            found = alt.stdout.strip().splitlines()[0]
            print(f"[+] Found payload at: {found}")
            return found
        else:
            print("[!] Critical: peppy_recovery.bin not found in shared storage.")
            sys.exit(1)
    return TARGET_IMAGE

def scan_storage():
    print("
[*] Phase 2: Scanning Connected Storage Nodes...")
    code, out, err = run_cmd("ls /dev/block/sd* /dev/block/mmcblk* 2>/dev/null")
    if out:
        print(f"[+] Detected block storage nodes:
{out}")
    else:
        print("[-] Warning: No standard block nodes found. Checking USB host paths...")
        alt_nodes = run_cmd("ls /dev/sdb /dev/sdc /dev/mmcblk1 2>/dev/null")
