#!/usr/bin/env python3
# [PROPRIETARY & PATENT PENDING] Copyright (c) 2026 Jonathan Anthony Taylor (ViperGearLabs). All Rights Reserved.
"""
Viper AI Suite - Lite (Termux friendly)
Uses only the standard library + openai package.
"""

import json
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs
from pathlib import Path

try:
    from openai import OpenAI
except ImportError:
    print("Installing openai...")
    os.system("pip install openai")
    from openai import OpenAI

PROFILES_FILE = Path.home() / ".viper_profiles.json"

PROVIDERS = {
    "Venice AI": {"base_url": "https://api.venice.ai/api/v1", "model": "venice-uncensored"},
    "xAI / Grok": {"base_url": "https://api.x.ai/v1", "model": "grok-4.7"},
    "OpenAI": {"base_url": "https://api.openai.com/v1", "model": "gpt-4o-mini"},
    "Google Gemini": {"base_url": "https://generativelanguage.googleapis.com/v1beta/openai/", "model": "gemini-2.5-flash"},
    "Groq": {"base_url": "https://api.groq.com/openai/v1", "model": "llama-3.3-70b-versatile"},
    "Together AI": {"base_url": "https://api.together.xyz/v1", "model": "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo"},
    "DeepSeek": {"base_url": "https://api.deepseek.com/v1", "model": "deepseek-chat"},
    "OpenRouter": {"base_url": "https://openrouter.ai/api/v1", "model": "openai/gpt-4o-mini"},
    "Mistral": {"base_url": "https://api.mistral.ai/v1", "model": "mistral-large-latest"},
    "Custom": {"base_url": "", "model": ""},
}

HTML = '''<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Viper AI Suite</title>
<style>
body { font-family: system-ui, sans-serif; max-width: 800px; margin: 0 auto; padding: 16px; background: #0f0f0f; color: #eee; }
h1 { color: #4ade80; }
label { display: block; margin-top: 12px; font-weight: bold; }
input, select, textarea { width: 100%; padding: 8px; margin-top: 4px; box-sizing: border-box; background: #1a1a1a; color: #eee; border: 1px solid #333; border-radius: 6px; }
button { margin-top: 12px; padding: 10px 16px; background: #4ade80; color: #000; border: none; border-radius: 6px; font-weight: bold; cursor: pointer; }
button:hover { background: #22c55e; }
#output { white-space: pre-wrap; background: #1a1a1a; padding: 12px; border-radius: 8px; margin-top: 16px; min-height: 100px; }
.tabs { display: flex; gap: 8px; margin-bottom: 16px; }
.tab { padding: 8px 16px; background: #222; border-radius: 6px; cursor: pointer; }
.tab.active { background: #4ade80; color: #000; }
.hidden { display: none; }
</style>
</head>
<body>
<h1>🐍 Viper AI Suite</h1>
<div class="tabs">
  <div class="tab active" onclick="showTab('chat')">Chat</div>
  <div class="tab" onclick="showTab('feed')">Feed</div>
</div>

<div id="chat">
  <label>Provider</label>
  <select id="provider">
    <option>Venice AI</option><option>xAI / Grok</option><option>OpenAI</option>
    <option>Google Gemini</option><option>Groq</option><option>Together AI</option>
    <option>DeepSeek</option><option>OpenRouter</option><option>Mistral</option><option>Custom</option>
  </select>
  <label>API Key</label>
  <input type="password" id="apikey" placeholder="Paste your API key">
  <label>Model (optional)</label>
  <input id="model" placeholder="Leave blank for default">
  <label>Custom Base URL (only for Custom)</label>
  <input id="customurl" placeholder="https://your-endpoint/v1">
  <label>System Prompt</label>
  <input id="system" value="You are a helpful AI assistant.">
  <label>Your Message</label>
  <textarea id="prompt" rows="4" placeholder="Type your message..."></textarea>
  <button onclick="send()">Send</button>
  <button onclick="document.getElementById('output').innerText=''">Clear</button>
  <div id="output"></div>
</div>

<div id="feed" class="hidden">
  <label>Provider</label>
  <select id="fprovider">
    <option>Venice AI</option><option>xAI / Grok</option><option>OpenAI</option>
    <option>Google Gemini</option><option>Groq</option><option>Together AI</option>
    <option>DeepSeek</option><option>OpenRouter</option><option>Mistral</option><option>Custom</option>
  </select>
  <label>API Key</label>
  <input type="password" id="fapikey" placeholder="Paste your API key">
  <label>Model (optional)</label>
  <input id="fmodel" placeholder="Leave blank for default">
  <label>Custom Base URL</label>
  <input id="fcustomurl" placeholder="https://your-endpoint/v1">
  <label>System Prompt</label>
  <input id="fsystem" value="You are a helpful AI assistant.">
  <h3>Prompt Section</h3>
  <textarea id="fprompt" rows="5" placeholder="Type your prompt here..."></textarea>
  <br>
  <button onclick="setPrompt('Why is privacy important in AI systems?')">Why is privacy important?</button>
  <button onclick="setPrompt('Write a short creative story about a robot discovering emotions.')">Write a short story</button>
  <button onclick="setPrompt('Explain artificial intelligence in simple terms a 10-year-old can understand.')">Explain AI simply</button>
  <button onclick="setPrompt('Write a Python function that calculates the Fibonacci sequence up to n terms.')">Code a Python function</button>
  <br>
  <button onclick="postFeed()">Post to Feed</button>
  <button onclick="document.getElementById('feedout').innerText=''">Clear Feed</button>
  <button onclick="document.getElementById('fprompt').value=''">Clear Prompt</button>
  <div id="feedout"></div>
</div>

<script>
function showTab(name) {
  document.getElementById('chat').classList.toggle('hidden', name !== 'chat');
  document.getElementById('feed').classList.toggle('hidden', name !== 'feed');
  document.querySelectorAll('.tab').forEach((t,i) => t.classList.toggle('active', (name==='chat'&&i===0)||(name==='feed'&&i===1)));
}
function setPrompt(text) { document.getElementById('fprompt').value = text; }

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
    const text = await r.text();
    out.innerText = text;
  } catch(e) { out.innerText = 'Error: ' + e; }
}

async function postFeed() {
  const out = document.getElementById('feedout');
  const prompt = document.getElementById('fprompt').value;
  if (!prompt.trim()) { out.innerText += '\\n\\nError: Enter a prompt.'; return; }
  out.innerText += '\\n\\n---\\n**You:** ' + prompt + '\\n**Viper:** Thinking...';
  const body = new URLSearchParams({
    provider: document.getElementById('fprovider').value,
    api_key: document.getElementById('fapikey').value,
    model: document.getElementById('fmodel').value,
    custom_url: document.getElementById('fcustomurl').value,
    system: document.getElementById('fsystem').value,
    prompt: prompt
  });
  try {
    const r = await fetch('/chat', {method:'POST', body});
    const text = await r.text();
    out.innerText = out.innerText.replace('Thinking...', text);
  } catch(e) { out.innerText += '\\nError: ' + e; }
}
</script>
</body>
</html>'''

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(HTML.encode())

    def do_POST(self):
        if self.path != '/chat':
            self.send_error(404)
            return
        length = int(self.headers.get('Content-Length', 0))
        data = parse_qs(self.rfile.read(length).decode())
        provider = data.get('provider', [''])[0]
        api_key = data.get('api_key', [''])[0]
        model = data.get('model', [''])[0]
        custom_url = data.get('custom_url', [''])[0]
        system = data.get('system', [''])[0]
        prompt = data.get('prompt', [''])[0]

        if not api_key:
            reply = "Error: Please enter an API key."
        elif not prompt:
            reply = "Error: Please enter a prompt."
        else:
            cfg = PROVIDERS.get(provider, {})
            base_url = custom_url.strip() if provider == "Custom" and custom_url else cfg.get("base_url", "")
            model_to_use = model.strip() if model else cfg.get("model", "")
            if not base_url:
                reply = "Error: No base URL."
            else:
                try:
                    client = OpenAI(api_key=api_key.strip(), base_url=base_url)
                    messages = []
                    if system.strip():
                        messages.append({"role": "system", "content": system.strip()})
                    messages.append({"role": "user", "content": prompt.strip()})
                    completion = client.chat.completions.create(
                        model=model_to_use,
                        messages=messages,
                        temperature=0.7,
                    )
                    reply = completion.choices[0].message.content or "(empty)"
                except Exception as e:
                    reply = f"Error: {str(e)}"

        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(reply.encode())

if __name__ == "__main__":
    print("Viper AI Suite Lite")
    print("Open http://127.0.0.1:7860 in your browser")
    HTTPServer(("0.0.0.0", 7860), Handler).serve_forever()
