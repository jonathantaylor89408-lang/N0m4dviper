#!/data/data/com.termux/files/usr/bin/python3
# [PROPRIETARY & PATENT PENDING] Copyright (c) 2026 Jonathan Anthony Taylor (ViperGearLabs). All Rights Reserved.
import os, sys, time, shutil, hashlib
V = os.path.expanduser("~/viper_node")
for d in ["auth","ledger","nodes","stage","nfc"]: os.makedirs(f"{V}/{d}", exist_ok=True)
T,K,C,Z,OPS,SEG = f"{V}/auth/trust.db",f"{V}/auth/node.key",f"{V}/ledger/chain.log",f"{V}/ledger/anchor.seal",f"{V}/ledger/ops.log",f"{V}/ledger/segments.seal"
for f in [T,C,OPS,SEG]: open(f,"a").close()
if not os.path.exists(K) or not os.path.getsize(K): open(K,"wb").write(os.urandom(64))
h  = lambda p: hashlib.sha256(open(p,"rb").read()).hexdigest()
hs = lambda s: hashlib.sha256(s.encode()).hexdigest()
ID = h(K)[:12]; MAXCHAIN = 20000; VERBOSE = "-v" in sys.argv
def log(m):
    open(OPS,"a").write(f"[{time.strftime('%H:%M:%S')}] {m}\n")
    if VERBOSE: print(m)
def rotate():
    L = open(C).read().splitlines()
    if len(L) < MAXCHAIN: return
    seg = f"{V}/ledger/chain.{int(time.time())}.log"
    shutil.move(C, seg); open(C,"a").close()
    open(SEG,"a").write(f"{h(seg)} {seg}\n"); log(f"ROTATED -> {os.path.basename(seg)}")
def led(m):
    rotate(); L = open(C).read().splitlines(); p = L[-1].split()[0] if L else "GENESIS"
    open(C,"a").write(f"{hs(p+m)} {int(time.time())} {m}\n")
def trusted(p): return h(p) in open(T).read().splitlines()
a = [x for x in sys.argv[1:] if x != "-v"]
if os.path.basename(sys.argv[0]) == "comply": a = ["comply"] + a
c = a[0] if a else "status"
if c == "cert": open(T,"a").write(h(a[1])+"\n"); log(f"CERT {a[1]} {h(a[1])[:12]}")
elif c == "auth": ok = trusted(a[1]); log(f"{'ALLOW' if ok else 'DENY'} {a[1]}"); sys.exit(0 if ok else 1)
elif c == "apply":
    if not trusted(a[1]): sys.exit("DENY uncertified")
    src,dst = a[1],a[2]; tmp = f"{V}/stage/{os.path.basename(dst)}.tmp"
    shutil.copy2(src,tmp)
    if h(tmp) != h(src): os.remove(tmp); sys.exit("stage verify fail")
    bak = f"{V}/stage/{os.path.basename(dst)}.bak"
    if os.path.exists(dst): shutil.copy2(dst,bak)
    try:
        os.replace(tmp,dst)
        if h(dst) != h(src): raise OSError("post-swap verify fail")
        led(f"TX:{dst}:{h(dst)[:12]}"); log(f"COMMIT {dst}")
    except Exception as e:
        if os.path.exists(bak): shutil.copy2(bak,dst)
        led(f"ROLLBACK:{dst}"); sys.exit(f"ROLLBACK {e}")
elif c == "rollback":
    bak = f"{V}/stage/{os.path.basename(a[1])}.bak"
    if not os.path.exists(bak): sys.exit("no backup")
    shutil.copy2(bak,a[1]); led(f"RB:{a[1]}"); log(f"ROLLED {a[1]}")
elif c == "comply": led(f"CMP:{':'.join(a[1:])}:{ID}"); log(f"COMPLY {' '.join(a[1:])}")
elif c == "seal": open(Z,"w").write(h(C)); log(f"SEALED {h(C)[:12]}")
elif c == "verify":
    ok = os.path.exists(Z) and open(Z).read().strip() == h(C)
    for line in open(SEG):
        sh,txt = line.split(); ok = ok and os.path.exists(txt) and h(txt) == sh
    log(f"{'OK' if ok else 'DRIFT'} ({len(open(C).read().splitlines())} tx)"); sys.exit(0 if ok else 1)
else:
    sl = "OK" if (os.path.exists(Z) and open(Z).read().strip() == h(C)) else "NO"
    log(f"NODE:{ID} TX:{len(open(C).read().splitlines())} TRUST:{len(open(T).read().splitlines())} SEAL:{sl}")
    if VERBOSE: print(f"NODE:{ID} TX:{len(open(C).read().splitlines())} TRUST:{len(open(T).read().splitlines())} SEAL:{sl}")

# Checkpoint extension
if len(sys.argv) > 1 and sys.argv[1] == "checkpoint":
    c_path = f"{V}/ledger/checkpoint.seal"
    shutil.copy2(C, c_path)
    print(f"[{time.strftime('%T')}] CHECKPOINT SECURED: {h(c_path)[:12]}")
