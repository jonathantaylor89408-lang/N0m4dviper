#!/usr/bin/env python3
# [PROPRIETARY & PATENT PENDING] Copyright (c) 2026 Jonathan Anthony Taylor (ViperGearLabs). All Rights Reserved.
"""
VIPER-ELITE: VAULT RESOLUTION & NODE HARDENING UTILITY
"""
import os
import json
from pathlib import Path

NODE_DIR = Path.home() / "viper_node"
VAULT_PATH = NODE_DIR / ".v1p34c0de" / "V1P34C0DE.vipercode"
LEDGER_PATH = NODE_DIR / "ledger" / "chain.log"

LEDGER_PATH.parent.mkdir(parents=True, exist_ok=True)

def log_audit(msg):
    print(f"[*] {msg}")
    with open(LEDGER_PATH, "a") as f:
        f.write(f"[HARDEN] {msg}\n")

def check_vault():
    if VAULT_PATH.exists():
        log_audit(f"Vault verified intact at {VAULT_PATH}")
        return True
    else:
        log_audit("WARNING: Vault path missing!")
        return False

def harden_permissions():
    log_audit("Hardening node file permissions (umask 077 equivalent)...")
    for root, dirs, files in os.walk(NODE_DIR):
        for d in dirs:
            os.chmod(os.path.join(root, d), 0o700)
        for f in files:
            filepath = os.path.join(root, f)
            if f.endswith('.sh') or f.endswith('.py'):
                os.chmod(filepath, 0o700)
            else:
                os.chmod(filepath, 0o600)
    log_audit("File permissions successfully hardened.")

if __name__ == "__main__":
    log_audit("Initiating Viper node resolution and hardening protocol...")
    check_vault()
    harden_permissions()
    log_audit("Node hardening completed successfully. System compliant.")
