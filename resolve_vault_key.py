#!/usr/bin/env python3
# [PROPRIETARY & PATENT PENDING] Copyright (c) 2026 Jonathan Anthony Taylor (ViperGearLabs). All Rights Reserved.
import json
from pathlib import Path

VAULT_PATH = Path.home() / "viper_node" / ".v1p34c0de" / "V1P34C0DE.vipercode"

def load_key(provider="venice"):
    if not VAULT_PATH.exists():
        print(f"Vault not found at {VAULT_PATH}")
        return None
    try:
        data = json.loads(VAULT_PATH.read_text())
        for key_name in [f"{provider}_api_key", "VENICE_API_KEY", "XAI_API_KEY", "OPENAI_API_KEY", "api_key", "key"]:
            if key_name in data:
                return data[key_name]
        if "credentials" in data and provider in data["credentials"]:
            return data["credentials"][provider]
        return None
    except json.JSONDecodeError:
        text = VAULT_PATH.read_text().strip()
        return text if text else None

if __name__ == "__main__":
    import sys
    provider = sys.argv[1] if len(sys.argv) > 1 else "venice"
    key = load_key(provider)
    print(key if key else "NO_KEY")
