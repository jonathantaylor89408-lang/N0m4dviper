#!/usr/bin/env python3
import os, sys, json, hashlib

VAULT_PATH = os.path.expanduser("~/viper_node/.v1p34c0de/V1P34C0DE.vipercode")
CACHE_DIR = os.path.expanduser("~/viper_node/cache")
os.makedirs(CACHE_DIR, exist_ok=True)

def load_local_source(source_path):
    print(f"[*] Loading local source vector: {source_path}")
    try:
        with open(source_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"[!] Critical Error reading source file: {e}", file=sys.stderr)
        sys.exit(1)

def verify_and_compare(source_data, local_input):
    print("[*] Normalizing data vectors and calculating cryptographic hashes...")
    source_hash = hashlib.sha256(source_data.encode('utf-8')).hexdigest()
    
    local_normalized = json.dumps(local_input, sort_keys=True)
    local_hash = hashlib.sha256(local_normalized.encode('utf-8')).hexdigest()
    
    print(f"[+] Source Data SHA256  : {source_hash[:16]}...")
    print(f"[+] Local Vault SHA256  : {local_hash[:16]}...")
    
    match_status = source_hash == local_hash
    report = {
        "status": "VERIFIED" if match_status else "DISCREPANCY_DETECTED",
        "source_hash": source_hash,
        "local_hash": local_hash,
        "match": match_status
    }
    
    report_path = os.path.join(CACHE_DIR, "sync_audit_report.json")
    with open(report_path, "w") as f:
        json.dump(report, f, indent=4)
            
    if match_status:
        print("[+] SUCCESS: Data vectors match local node vault identically.")
    else:
        print("[!] WARNING: Variance detected between source and local node inputs.")

if __name__ == "__main__":
    target_file = VAULT_PATH if os.path.exists(VAULT_PATH) else "README.md"
    if len(sys.argv) > 1:
        target_file = sys.argv[1]
        
    raw_data = load_local_source(target_file)
    local_input_data = input("Local Data Input > ")
    verify_and_compare(raw_data, local_input_data)
