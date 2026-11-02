#!/usr/bin/env python3
import os, sys, subprocess
TARGET_IMAGE = os.path.expanduser('~/storage/shared/Download/peppy_recovery.bin')
def run_cmd(cmd):
    res = subprocess.run(cmd, shell=True, text=True, capture_output=True)
    return res.returncode, res.stdout.strip(), res.stderr.strip()
def execute_write():
    print('[*] Initializing Peppy Raw Write Sequence...')
    if not os.path.exists(TARGET_IMAGE):
        print(f'[!] Error: Recovery payload missing at {TARGET_IMAGE}')
        sys.exit(1)
    print('[*] Scanning available block storage nodes...')
    code, out, err = run_cmd('ls /dev/block/sd* /dev/block/mmcblk* 2>/dev/null')
    print(f'[+] Detected nodes:
{out if out else "None detected."}')
    target_block = input('[?] Enter target block node (e.g. /dev/block/sdb): ').strip()
    if not target_block.startswith('/dev/'):
        print('[!] Invalid block node.')
        sys.exit(1)
    if input(f'[!] Overwrite {target_block}? Type EXECUTE: ').strip() != 'EXECUTE':
        sys.exit(0)
    print(f'[*] Writing payload to {target_block}...')
    code, out, err = run_cmd(f'su -c "dd if={TARGET_IMAGE} of={target_block} bs=4M status=progress conv=fsync"')
    print('[+] Success!' if code == 0 else f'[!] Failed: {err}')
if __name__ == '__main__':
    execute_write()
