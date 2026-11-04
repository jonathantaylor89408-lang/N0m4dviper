#!/data/data/com.termux/files/usr/bin/bash
# [PROPRIETARY & PATENT PENDING] Copyright (c) 2026 Jonathan Anthony Taylor (ViperGearLabs). All Rights Reserved.
# VIPER NODE :: PERSISTENT WAKE-LOCK KEEPALIVE
while true; do
    termux-wake-lock
    if ! pgrep -f "viper_daemon.py" >/dev/null 2>&1; then
        cd ~/viper_node
        nohup python3 viper_daemon.py >/dev/null 2>&1 &
    fi
    sleep 300
done
