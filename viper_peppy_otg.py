#!/usr/bin/env python3
import os, sys, subprocess

TARGET_IMAGE = os.path.expanduser('~/storage/shared/Download/peppy_recovery.bin')

def run_cmd(cmd):
    res = subprocess.run(cmd, shell=True, text=True, capture_output=True)
    return res.returncode, res.stdout.strip(), res.stderr.strip()

def execute_flash():
    print('[*] Initializing Peppy OTG Raw Write Sequence...')
    if not os.path.exists(TARGET_IMAGE):
        print(f'[!] Error: Recovery payload missing at {TARGET_IMAGE}')
        sys.exit(1)
        
    file_size_mb = os.path.getsize(TARGET_IMAGE) / (1024 * 1024)
    print(f'[*] Payload verified: {TARGET_IMAGE} ({file_size_mb:.2f} MB)')
    
    print('[*] Scanning connected storage blocks...')
    code, out, err = run_cmd('ls /dev/block/sd* /dev/block/mmcblk* 2>/dev/null')
    print('[+] Detected nodes:\n' + (out if out else 'None detected.'))
    
    target = input('[?] Enter target block node (e.g. /dev/block/sdb): ').strip()
    if not target.startswith('/dev/'):
        print('[!] Invalid block device node.')
        sys.exit(1)
        
    confirm = input(f'[!] WARNING: This will overwrite {target}. Type EXECUTE: ').strip()
    if confirm != 'EXECUTE':
        print('[!] Aborted.')
        sys.exit(0)
        
    print(f'[*] Streaming peppy_recovery.bin to {target}...')
    cmd = f'su -c "dd if={TARGET_IMAGE} of={target} bs=4M status=progress conv=fsync"'
    code, out, err = run_cmd(cmd)
    print('[+] Flash complete!' if code == 0 else f'[!] Failed: {err}')

if __name__ == '__main__':
    execute_flash()
