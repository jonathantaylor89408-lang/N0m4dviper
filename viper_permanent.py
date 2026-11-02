#!/usr/bin/env python3
import os, sys, requests

BANNER = """
+----------------------------------------------+
| VIPERSPACE NODE ONLINE (GUMROAD + GROK SYNC) |
| Operator: Nomad                              |
| Status: Immortal Loop Active                 |
+----------------------------------------------+
"""

def main():
    print("+---------------------------------------------------+")
    print("| INITIALIZING VIPERSPACE OPERATOR CREDENTIAL VAULT |")
    print("+---------------------------------------------------+")
    op_id = input("Enter Operator ID [Nomad]: ").strip() or "Nomad"
    passcode = input("Enter Operator Passcode: ").strip()

    if passcode != "343911":
        print("[!] Access Denied. Invalid passcode.")
        sys.exit(1)

    print("[*] Access Granted. Operator identity verified.")
    print(BANNER)

    while True:
        try:
            cmd = input(f"[{op_id} | VIPERSPACE] >> ").strip()
            if cmd.lower() in ["exit", "quit"]:
                break
            if not cmd:
                continue

            response = requests.post(
                "http://127.0.0.1:11434/v1/chat/completions",
                json={
                    "model": "llama3",
                    "messages": [{"role": "user", "content": cmd}]
                },
                timeout=30
            )
            if response.status_code == 200:
                data = response.json()
                print(data["choices"][0]["message"]["content"])
            else:
                print(f"[!] Matrix Error: HTTP {response.status_code}")
        except Exception as e:
            print(f"[!] Matrix Error (Local Engine offline?): {e}")

if __name__ == "__main__":
    main()
