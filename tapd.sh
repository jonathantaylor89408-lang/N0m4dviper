#!/data/data/com.termux/files/usr/bin/python3
# [PROPRIETARY & PATENT PENDING] Copyright (c) 2026 Jonathan Anthony Taylor (ViperGearLabs). All Rights Reserved.
import os, sys, time, json, subprocess, hashlib, signal
V = os.path.expanduser("~/viper_node")
NFC,OPS,C,HOOK = f"{V}/nfc",f"{V}/ledger/ops.log",f"{V}/ledger/chain.log",f"{V}/nfc/hook.py"
os.makedirs(NFC, exist_ok=True)
h = lambda p: hashlib.sha256(open(p,"rb").read()).hexdigest()
hs = lambda s: hashlib.sha256(s.encode()).hexdigest()
def log(m): open(OPS,"a").write(f"[{time.strftime('%H:%M:%S')}] TAPD {m}\n")
def led(m):
    L = open(C).read().splitlines(); p = L[-1].split()[0] if L else "GENESIS"
    open(C,"a").write(f"{hs(p+m)} {int(time.time())} {m}\n")
def _to(s,f): raise TimeoutError
while True:
    try:
        out = subprocess.run(["termux-nfc","-t","3600"], capture_output=True, text=True, timeout=3700)
        if out.returncode != 0 or not out.stdout.strip(): time.sleep(1); continue
        rec = json.loads(out.stdout)
        if os.path.exists(HOOK):
            signal.signal(signal.SIGALRM,_to); signal.alarm(3)
            try: ns = {}; exec(open(HOOK).read(), ns); rec = ns.get("hook", lambda r: r)(rec)
            except Exception as e: log(f"hook fail {e}")
            finally: signal.alarm(0)
        uid,tech,ats = rec.get("uid",""),rec.get("tech",""),rec.get("ats","")
        if not uid: log("bad handshake"); continue
        open(f"{NFC}/{int(time.time())}_{uid[:12]}.json","w").write(json.dumps(rec, indent=2))
        ok = tech in ("NfcA","NfcB","IsoDep")
        led(f"NFC:{uid[:12]}:{tech}:{'PASS' if ok else 'WARN'}")
        log(f"uid={uid[:12]} tech={tech} ats={ats or 'none'} {'PASS' if ok else 'WARN'}")
    except Exception as e: log(f"err {e}"); time.sleep(2)
