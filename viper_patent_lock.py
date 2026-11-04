#!/usr/bin/env python3
"""
VIPERGEARLABS: INTELLECTUAL PROPERTY, PATENT MANIFEST & RIGHTS LOCKDOWN ENGINE
Owner: Jonathan Anthony Taylor (NOMAD / ViperGearLabs)
"""
import os
import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path

NODE_DIR = Path.home() / "viper_node"
MANIFEST_PATH = NODE_DIR / "PATENT_AND_IP_MANIFEST.json"
LEDGER_PATH = NODE_DIR / "ledger" / "chain.log"

HEADER_TAG = "# [PROPRIETARY & PATENT PENDING] Copyright (c) 2026 Jonathan Anthony Taylor (ViperGearLabs). All Rights Reserved."

EXCLUDED_DIRS = {".git", ".v1p34c0de", "ledger", "auth", "cache", "__pycache__"}
EXCLUDED_EXTS = {".vipercode", ".enc", ".log", ".bak", ".swp"}

def sha256_file(filepath: Path) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def stamp_proprietary_headers():
    stamped = 0
    for root, dirs, files in os.walk(NODE_DIR):
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
        for file in files:
            if file.endswith((".py", ".sh")):
                fp = Path(root) / file
                try:
                    text = fp.read_text(encoding="utf-8")
                    if "ViperGearLabs" not in text:
                        lines = text.splitlines()
                        if lines and lines[0].startswith("#!"):
                            lines.insert(1, HEADER_TAG)
                        else:
                            lines.insert(0, HEADER_TAG)
                        fp.write_text("\n".join(lines) + "\n", encoding="utf-8")
                        stamped += 1
                except Exception:
                    pass
    return stamped

def build_ip_manifest():
    artifacts = {}
    for root, dirs, files in os.walk(NODE_DIR):
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
        for file in sorted(files):
            fp = Path(root) / file
            if fp.suffix in EXCLUDED_EXTS or file.startswith(".env"):
                continue
            rel = str(fp.relative_to(NODE_DIR))
            try:
                artifacts[rel] = {
                    "sha256": sha256_file(fp),
                    "size_bytes": fp.stat().st_size
                }
            except Exception:
                pass

    manifest = {
        "entity": "ViperGearLabs",
        "owner_of_record": "Jonathan Anthony Taylor (Callsign: NOMAD)",
        "jurisdiction": "Las Vegas, Clark County, Nevada, USA",
        "retention_of_rights": "ABSOLUTE_RETENTION_INTELLECTUAL_PERSONAL_AND_REAL_PROPERTY",
        "patent_scope": [
            "Viper Node Tree Architecture & Self-Healing Daemon",
            "V1P34C0DE Universal Cryptographic API Vault Resolution",
            "Defense Pentest Network Guard & Telemetry Tree Mapper",
            "ViperGearLabs Commercial Licensing & Credential Verification Engine"
        ],
        "timestamp_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "protected_artifacts": artifacts
    }

    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return len(artifacts)

if __name__ == "__main__":
    LEDGER_PATH.parent.mkdir(parents=True, exist_ok=True)
    stamped_count = stamp_proprietary_headers()
    artifact_count = build_ip_manifest()
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    msg = f"[{ts}] [IP_LOCKDOWN] Stamped {stamped_count} scripts; registered {artifact_count} SHA-256 artifacts in PATENT_AND_IP_MANIFEST.json"
    print(msg)
    with open(LEDGER_PATH, "a", encoding="utf-8") as f:
        f.write(msg + "\n")
