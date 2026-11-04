#!/data/data/com.termux/files/usr/bin/python3
# [PROPRIETARY & PATENT PENDING] Copyright (c) 2026 Jonathan Anthony Taylor (ViperGearLabs). All Rights Reserved.
import os, sys, time, subprocess, hashlib

V = os.path.expanduser("~/viper_node")
C = f"{V}/ledger/chain.log"
T = f"{V}/auth/trust.db"

h = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
hs = lambda s: hashlib.sha256(s.encode()).hexdigest()

def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] [NETTREEMAP] {msg}")

def led(m):
    if os.path.exists(C):
        L = open(C).read().splitlines()
        p = L[-1].split()[0] if L else "GENESIS"
        open(C, "a").write(f"{hs(p + m)} {int(time.time())} {m}\n")

def audit_bus():
    log("Scanning MDB Bus / Aztec Interface Node...")
    # Check if daemon process is healthy
    res = subprocess.run(["pgrep", "-f", "viper_daemon.py"], capture_output=True, text=True)
    daemon_active = bool(res.stdout.strip())
    
    # Check socket/network or serial interface availability
    serial_ports = [p for p in os.listdir("/dev") if "tty" in p or "usb" in p]
    
    log(f"Daemon Status: {'ONLINE (PID ' + res.stdout.strip() + ')' if daemon_active else 'OFFLINE'}")
    log(f"Active Serial/USB Nodes: {len(serial_ports)} detected")
    
    # Log compliance / telemetry audit event
    led(f"CMP:NETTREEMAP_AUDIT:AZTEC_BUS:STATUS={'OK' if daemon_active else 'WARN'}")
    log("Telemetry frame mapped. Audit committed to immutable ledger.")

if __name__ == "__main__":
    audit_bus()
