#!/usr/bin/env python3
# [PROPRIETARY & PATENT PENDING] Copyright (c) 2026 Jonathan Anthony Taylor (ViperGearLabs). All Rights Reserved.
"""
VIPER-ELITE: UNIVERSAL AI API KEY VAULT RESOLUTION, LIVE DESK & TARGET TRACKING
"""
import os
import sys
import json
import gzip
import base64
import socket
from pathlib import Path
from datetime import datetime, timezone

NODE_DIR = Path.home() / "viper_node"
VAULT_PATH = NODE_DIR / ".v1p34c0de" / "V1P34C0DE.vipercode"
LEDGER_PATH = NODE_DIR / "ledger" / "chain.log"

LEDGER_PATH.parent.mkdir(parents=True, exist_ok=True)

def log_event(tag: str, msg: str):
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    line = f"[{ts}] [{tag}] {msg}"
    with open(LEDGER_PATH, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def decode_vault_payload(raw_text: str) -> str:
    """Automatically unwraps base64+gzip (H4sIA...) payloads if compressed, or returns clean string."""
    cleaned = "".join(raw_text.split())
    if cleaned.startswith("H4sI"):
        try:
            compressed = base64.b64decode(cleaned)
            return gzip.decompress(compressed).decode("utf-8", errors="replace").strip()
        except Exception:
            pass
    return raw_text.strip()

def resolve_universal_key(provider_name="venice") -> str:
    if not VAULT_PATH.exists():
        log_event("VAULT_WARN", f"Vault missing at {VAULT_PATH}")
        return ""

    target = provider_name.lower().strip()
    aliases = {
        "venice": ["venice", "venice_ai", "venice-uncensored"],
        "xai": ["xai", "grok", "xai_api_key"],
        "grok": ["grok", "xai", "xai_api_key"],
        "openai": ["openai", "gpt"],
        "gemini": ["gemini", "google"],
        "deepseek": ["deepseek"],
        "groq": ["groq"],
        "openrouter": ["openrouter"],
        "mistral": ["mistral"]
    }.get(target, [target])

    raw_content = VAULT_PATH.read_text(encoding="utf-8", errors="replace")
    decoded = decode_vault_payload(raw_content)

    # 1. Try JSON structure
    try:
        data = json.loads(decoded)
        if isinstance(data, dict):
            # Direct and uppercase matches
            for a in aliases:
                for candidate in (a, f"{a}_api_key", f"{a.upper()}_API_KEY", "api_key", "key"):
                    if candidate in data and isinstance(data[candidate], str) and data[candidate].strip():
                        return data[candidate].strip()
            # Nested credentials dictionary
            creds = data.get("credentials", {})
            if isinstance(creds, dict):
                for k, v in creds.items():
                    if any(a in k.lower() for a in aliases) and isinstance(v, str) and v.strip():
                        return v.strip()
            # Substring scan across any JSON key
            for k, v in data.items():
                if any(a in k.lower() for a in aliases) and isinstance(v, str) and len(v.strip()) > 8:
                    return v.strip()
    except Exception:
        pass

    # 2. Key=Value / .env line scan inside decoded payload
    for line in decoded.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line or ":" in line:
            sep = "=" if "=" in line else ":"
            k, v = line.split(sep, 1)
            k_clean = k.strip().strip('"\'').lower()
            v_clean = v.strip().strip('"\',')
            if any(a in k_clean for a in aliases) and len(v_clean) > 8:
                return v_clean

    # 3. Raw token fallback
    first_line = decoded.splitlines()[0].strip() if decoded else ""
    if len(first_line) > 8:
        return first_line
    return ""

def verify_live_suite(host="127.0.0.1", port=8080) -> bool:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(1.5)
    try:
        s.connect((host, port))
        return True
    except Exception:
        return False
    finally:
        s.close()

if __name__ == "__main__":
    prov = sys.argv[1] if len(sys.argv) > 1 else "venice"
    key = resolve_universal_key(prov)
    suite_live = verify_live_suite("127.0.0.1", 8080)
    log_event("TARGET_TRACK", f"Provider={prov} | KeyResolved={'YES' if key else 'NO'} | Suite8080={'ONLINE' if suite_live else 'OFFLINE'}")
    print(key if key else "NO_KEY")
