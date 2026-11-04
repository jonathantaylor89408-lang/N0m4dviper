import os, sys, time, subprocess, hashlib

V = os.path.expanduser("~/viper_node")
LOG = f"{V}/ledger/daemon.log"
os.makedirs(os.path.dirname(LOG), exist_ok=True)

def log(msg):
    with open(LOG, "a") as f:
        f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}] {msg}\n")

log("VIPER DAEMON INIT: Entering hidden background mesh loop.")

while True:
    try:
        # 1. Ensure superadapt binary/links are intact
        sa = f"{V}/superadapt.sh"
        if os.path.exists(sa):
            subprocess.run([sa, "verify"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # 2. Keep local cache integration warm
        time.sleep(30)
    except Exception as e:
        log(f"CRITICAL EXCEPTION: {e}")
        time.sleep(10)
