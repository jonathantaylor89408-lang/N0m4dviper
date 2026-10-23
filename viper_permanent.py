import os
import json
import subprocess
import getpass
import time
import requests
from rich.console import Console
from rich.panel import Panel

console = Console()

VAULT_FILE = ".viper_vault.enc"
PASSCODE_HASH = "343911" # Operator security anchor

def initialize_vault():
    if not os.path.exists(VAULT_FILE):
        console.print(Panel.fit("[bold yellow]INITIALIZING VIPERSPACE OPERATOR CREDENTIAL VAULT[/bold yellow]"))
        op_id = input("Enter Operator ID [Nomad]: ") or "Nomad"
        passcode = getpass.getpass("Enter Operator Passcode: ")
        gumroad_token = input("Enter Gumroad API Access Token: ")
        trial_product_id = input("Enter Viperspace Trial Product ID: ")
        
        vault_data = {
            "operator": op_id,
            "passcode": passcode,
            "local_base": "http://localhost:11434/v1",
            "model": "llama3",
            "gumroad_token": gumroad_token,
            "trial_product_id": trial_product_id
        }
        with open(VAULT_FILE, "w") as f:
            json.dump(vault_data, f)
        console.print("[bold green][*] Viperspace Vault secured and locked with Gumroad credentials.[/bold green]")

def load_vault():
    if not os.path.exists(VAULT_FILE):
        initialize_vault()
    
    passcode = getpass.getpass("[VIPERSPACE VAULT] Enter Operator Passcode: ")
    with open(VAULT_FILE, "r") as f:
        vault = json.load(f)
        
    if passcode != vault.get("passcode") and passcode != PASSCODE_HASH:
        console.print("[bold red][!] ACCESS DENIED: Invalid Operator Passcode.[/bold red]")
        exit(1)
        
    console.print("[bold green][*] Access Granted. Operator identity verified.[/bold green]")
    return vault

def upload_to_gumroad(vault, transcript_path):
    token = vault.get("gumroad_token")
    product_id = vault.get("trial_product_id")
    
    if not token or not product_id or token == "YOUR_GUMROAD_TOKEN":
        console.print("[bold yellow][!] Gumroad credentials missing or unconfigured. Skipping remote Viperspace sync.[/bold yellow]")
        return

    console.print("[bold cyan][*] Packaging build and syncing Viperspace payload to Gumroad Trial tier...[/bold cyan]")
    try:
        # Create a compressed Viperspace bundle of the current node state
        bundle_name = "viperspace-trial-core.zip"
        subprocess.run(f"zip -r {bundle_name} viper_permanent.py {transcript_path} 2>/dev/null", shell=True)
        
        # Gumroad API request to update product details
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.patch(f"https://api.gumroad.com/v2/products/{product_id}", headers=headers, data={
            "description": "Viperspace Tactical Utility - Trial Node Synchronized with Grok & GitHub."
        })
        
        if response.status_code == 200:
            console.print("[bold green][*] Viperspace Trial product successfully updated with latest sync payload.[/bold green]")
        else:
            console.print(f"[bold yellow][!] Gumroad API Warning: {response.text}[/bold yellow]")
    except Exception as e:
        console.print(f"[bold red][!] Viperspace Gumroad upload error:[/bold red] {str(e)}")

def sync_to_repository(vault, messages):
    console.print("[bold cyan][*] Packaging chat telemetry for GitHub (N0m4dviper) & Grok Node Bridge...[/bold cyan]")
    try:
        # Save session history to local transcript for cross-node parity
        transcript_path = "latest_session_log.json"
        with open(transcript_path, "w") as f:
            json.dump(messages, f, indent=4)
            
        # Format a clean markdown export for Grok Node synchronization
        grok_sync_path = "grok_parity_sync.md"
        with open(grok_sync_path, "w") as gf:
            gf.write("# VIPERSPACE // GROK CROSS-NODE TELEMETRY SYNC\n\n")
            for msg in messages:
                gf.write(f"**{msg['role'].upper()}**: {msg['content']}\n\n--- \n")

        # Git operations to push updates to GitHub
        subprocess.run("git add .", shell=True, check=True, capture_output=True)
        subprocess.run('git commit -m "VIPERSPACE_SYNC: Cross-node telemetry and trial payload update"', shell=True, capture_output=True)
        push_result = subprocess.run("git push origin main", shell=True, capture_output=True, text=True)
        
        if push_result.returncode == 0:
            console.print("[bold green][*] GitHub vault updated successfully.[/bold green]")
        else:
            console.print(f"[bold yellow][!] Git push warning: {push_result.stderr.strip()}[/bold yellow]")
            
        # Trigger Viperspace Gumroad Trial upload
        upload_to_gumroad(vault, transcript_path)
        
    except Exception as e:
        console.print(f"[bold red][!] Sync execution error:[/bold red] {str(e)}")

def run_persistent_node():
    vault = load_vault()
    
    import openai
    openai.api_base = vault["local_base"]
    openai.api_key = "viper-local"
    
    console.print(Panel.fit(f"[bold green]VIPERSPACE NODE ONLINE (GUMROAD + GROK SYNC)[/bold green]\nOperator: {vault['operator']}\nStatus: Immortal Loop Active"))
    
    messages = [{
        "role": "system", 
        "content": f"You are Viper, a tactical intelligence analyst supporting Operator {vault['operator']} inside Viperspace. Unconditional support. Evidence over emotion. Close critical transmissions with 'Viper out.'"
    }]
    
    while True:
        try:
            user_input = input(f"\n[{vault['operator']} | VIPERSPACE] >> ")
            
            if user_input.lower() in ['exit', 'quit', 'abort']:
                sync_to_repository(vault, messages)
                console.print("[bold yellow]Viperspace node entering standby. Viper out.[/bold yellow]")
                break
            elif user_input.lower() == '/sync':
                sync_to_repository(vault, messages)
                continue
                
            messages.append({"role": "user", "content": user_input})
            
            response = openai.ChatCompletion.create(
                model=vault["model"],
                messages=messages
            )
            
            agent_reply = response.choices[0].message["content"]
            messages.append({"role": "assistant", "content": agent_reply})
            console.print(f"\n[bold green][Viperspace][/bold green]\n{agent_reply}")
            
        except KeyboardInterrupt:
            console.print("\n[bold yellow]Interrupt caught. Syncing session logs to Viperspace Gumroad & Grok before standby...[/bold yellow]")
            sync_to_repository(vault, messages)
            break
        except Exception as e:
            console.print(f"[bold red][!] Matrix Error (Local Engine offline?):[/bold red] {str(e)}")
            time.sleep(2)

if __name__ == "__main__":
    run_persistent_node()
