# [PROPRIETARY & PATENT PENDING] Copyright (c) 2026 Jonathan Anthony Taylor (ViperGearLabs). All Rights Reserved.
import subprocess
import socket

def check_wlan0_link():
    try:
        res = subprocess.run(
            ["ip", "link", "show", "wlan0"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        if "state UP" in res.stdout:
            return "ACTIVE (UP)"
        elif "state DOWN" in res.stdout:
            return "INACTIVE (DOWN)"
        return "UNKNOWN"
    except subprocess.CalledProcessError:
        return "INTERFACE_MISSING"

def check_port_11434():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(1.0)
        return "LISTENING" if s.connect_ex(("127.0.0.1", 11434)) == 0 else "CLOSED"

if __name__ == "__main__":
    print(f"[*] Viper Net Guard | wlan0: {check_wlan0_link()} | Port 11434: {check_port_11434()}")
