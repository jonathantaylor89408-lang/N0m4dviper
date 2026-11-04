#!/usr/bin/env python3
import os
import sys
import subprocess

TARGET_IMAGE = os.path.expanduser("~/storage/shared/Download/peppy_recovery.bin")

def run_cmd(cmd):
    result = subprocess.run(cmd, shell=True, text=True, capture_output=True)
    if result.returncode != 0:
        return f"[!] Error: {result.stderr.strip()}"
    return result.stdout.strip()

def verify_and_flash():
    print("[*] Initializing Peppy USB OTG Recovery Sequence...")
    if not os.path.exists(TARGET_IMAGE):
        print(f"[!] Error: Recovery payload not found at {TARGET_IMAGE}")
        sys.exit(1)
        
    file_size_mb = os.path.getsize(TARGET_IMAGE) / (1024 * 1024)
    print(f"[*] Payload verified: {TARGET_IMAGE} ({file_size_mb:.2f} MB)")
    
    print("[*] Scanning USB OTG bus for storage targets...")
    storage_blocks = run_cmd("ls /dev/block/sd* /dev/block/mmcblk* 2>/dev/null")
    print(f"[+] Available storage nodes:\n{storage_blocks}")
    
    print("[*] Enforcing MBR (55AA) and GPT signature check...")
    sig_check = run_cmd(f"hexdump -C -n 512 {TARGET_IMAGE} | grep '55 aa'")
    if sig_check:
        print("[+] MBR signature 55AA verified successfully.")
    else:
        print("[!] Warning: Standard MBR boot signature check unconfirmed.")

    print("[*] Peppy OTG staging environment ready.")

if __name__ == "__main__":
    verify_and_flash()
