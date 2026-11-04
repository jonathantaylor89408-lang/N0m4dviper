#!/usr/bin/env bash
# [PROPRIETARY & PATENT PENDING] Copyright (c) 2026 Jonathan Anthony Taylor (ViperGearLabs). All Rights Reserved.
echo "[*] Checking local Ollama engine status..."
if ! pgrep -x "ollama" > /dev/null; then
    echo "[+] Starting Ollama background server..."
    ollama serve > /dev/null 2>&1 &
    sleep 3
else
    echo "[*] Ollama server already active."
fi

echo "[+] Launching Viperspace Node..."
cd ~/viper_node && python3 viper_permanent.py
