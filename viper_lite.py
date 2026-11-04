#!/usr/bin/env python3
# [PROPRIETARY & PATENT PENDING] Copyright (c) 2026 Jonathan Anthony Taylor (ViperGearLabs). All Rights Reserved.
"""
Viper AI Suite - Lite (Auto-Vault Key Resolution + Live Desk & Target Tracking)
"""
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs
from viper_universal_vault import resolve_universal_key, log_event

try:
    import openai
except ImportError:
    os.system("pip install openai")
    import openai

PROVIDERS = {
    "Venice AI": {"base_url": "https://api.venice.ai/api/v1", "model": "venice-uncensored", "vault_id": "venice"},
    "xAI / Grok": {"base_url": "https://api.x.ai/v1", "model": "grok-4.7", "vault_id": "xai"},
    "OpenAI": {"base_url": "https://api.openai.com/v1", "model": "gpt-4o-mini", "vault_id": "openai"},
    "Google Gemini": {"base_url": "https://generativelanguage.googleapis.com/v1beta/openai/", "model": "gemini-2.5-flash", "vault_id": "gemini"},
    "Groq": {"base_url": "https://api.groq.com/openai/v1", "model": "llama-3.3-70b-versatile", "vault_id": "groq"},
    "Together AI": {"base_url": "https://api.together.xyz/v1", "model": "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo", "vault_id": "together"},
    "DeepSeek": {"base_url": "https://api.deepseek.com/v1", "model": "deepseek-chat", "vault_id": "deepseek"},
    "OpenRouter": {"base_url": "https://openrouter.ai/api/v1", "model": "openai/gpt-4o-mini", "vault_id": "openrouter"},
    "Mistral": {"base_url": "https://api.mistral.ai/v1", "model": "mistral-large-latest", "vault_id": "mistral"},
    "Custom": {"base_url": "", "model": "", "vault_id": "custom"},
}

HTML = '''<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Viper AI Suite | ViperGearLabs</title>
<style>
body { font-family: system-ui, sans-serif; max-width: 820px; margin: 0 auto; padding: 16px; background: #0b0f0c; color: #e5e7eb; }
h1 { color: #4ade80; margin-bottom: 4px; }
.sub { font-size: 12px; color: #9ca3af; margin-bottom: 16px; }
label { display: block; margin-top: 10px; font-weight: bold; font-size: 13px; color: #86efac; }
input, select, textarea { width: 100%; padding: 8px; margin-top: 4px; box-sizing: border-box; background: #141a16; color: #eee; border: 1px solid #2d3b32; border-radius: 6px; }
button { margin-top: 12px; margin-right: 8px; padding: 10px 16px; background: #4ade80; color: #000; border: none; border-radius: 6px; font-weight: bold; cursor: pointer; }
#output { white-space: pre-wrap; background: #141a16; padding: 12px; border-radius: 8px; margin-top: 16px; min-height: 110px; border: 1px solid #2d3b32; }
</style>
</head>
<body>
<h1>🐍 Viper AI Suite — Live Desk</h1>
<div class="sub">Proprietary & Patent Pending | Jonathan Anthony Taylor (ViperGearLabs) | Auto-Vault V1P34C0DE Active</div>
<label>Provider</label>
<select id="provider">
  <option>Venice AI</option><option>xAI / Grok</option><option>OpenAI</option>
  <option>Google Gemini</option><option>Groq</option><option>Together AI</option>
  <option>DeepSeek</option><option>OpenRouter</option><option>Mistral</option><option>Custom</option>
</select>
<label>API Key (Leave blank to auto-resolve from V1P34C0DE Vault)</label>
<input type="password" id="apikey" placeholder="Auto-resolving from local V1P34C0DE vault...">
<label>Model (optional)</label>
<input id="model" placeholder="Leave blank for provider default">
<label>Custom Base URL (only for Custom)</label>
<input id="customurl" placeholder="https://your-endpoint/v1">
<label>System Prompt</label>
<input id="system" value="You are Viper-Elite, a tactical and precise AI node assistant.">
<label>Command / Prompt</label>
<textarea id="prompt" rows="4" placeholder="Enter tactical query..."></textarea>
<button onclick="send()">Execute</button>
<button onclick="document.getElementById('output').innerText=''">Clear Desk</button>
<div id="output">Ready.</div>
<script>
async function send() {
  const out = document.getElementById('output');
  out.innerText = 'Thinking...';
  const body = new URLSearchParams({
    provider: document.getElementById('provider').value,
    api_key: document.getElementById('apikey').value,
    model: document.getElementById('model').value,
    custom_url: document.getElementById('customurl').value,
    system: document.getElementById('system').value,
    prompt: document.getElementById('prompt').value
  });
  try {
    const r = await fetch('/chat', {method:'POST', body});
    out.innerText = await r.text();
  } catch(e) { out.innerText = 'Error: ' + e; }
}
</script>
</body>
</html>
'''

class ViperHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(HTML.encode('utf-8'))

    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        body = self.wfile.read(length).decode('utf-8')
        params = parse_qs(body)

        provider = params.get('provider', ['Venice AI'])[0]
        api_key = params.get('api_key', [''])[0].strip()
        model_input = params.get('model', [''])[0].strip()
        custom_url = params.get('custom_url', [''])[0].strip()
        system_prompt = params.get('system', [''])[0]
        user_prompt = params.get('prompt', [''])[0]

        cfg = PROVIDERS.get(provider, PROVIDERS["Custom"])
        base_url = custom_url if provider == "Custom" else cfg["base_url"]
        model = model_input if model_input else cfg["model"]

        if not api_key:
            api_key = resolve_universal_key(cfg.get("vault_id", provider))

        if not api_key and provider != "Custom":
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Error: No API key provided or found in V1P34C0DE vault.")
            return

        try:
            openai.api_key = api_key if api_key else "placeholder"
            openai.api_base = base_url
            log_event("SUITE_DISPATCH", f"Provider={provider} Model={model}")

            response = openai.ChatCompletion.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            )
            reply = response.choices[0].message['content']
            self.send_response(200)
            self.send_header('Content-type', 'text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write(reply.encode('utf-8'))
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(f"API Error: {str(e)}".encode('utf-8'))

if __name__ == '__main__':
    server = HTTPServer(('127.0.0.1', 8080), ViperHandler)
    print("🐍 Viper AI Suite (ViperGearLabs) running at http://127.0.0.1:8080")
    server.serve_forever()
