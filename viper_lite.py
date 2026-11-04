#!/usr/bin/env python3
"""
Viper AI Suite - Lite (works with openai 0.28)
"""
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs

try:
    import openai
except ImportError:
    print("Installing openai...")
    os.system("pip install openai")
    import openai

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
button { margin-top: 12px; margin-right: 8px; padding: 10px 16px; background: #4ade80; color: #000; border: none; border-radius: 6px; font-weight: bold; cursor: pointer; }
#output, #feedout { white-space: pre-wrap; background: #1a1a1a; padding: 12px; border-radius: 8px; margin-top: 16px; min-height: 100px; }
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
    out.innerText = out.innerText.replace('**Viper:** Thinking...', '**Viper:** ' + text);
  } catch(e) { out.innerText += '\\nError: ' + e; }
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
        
        provider = params.get('provider', [''])[0]
        api_key = params.get('api_key', [''])[0]
        model_input = params.get('model', [''])[0]
        custom_url = params.get('custom_url', [''])[0]
        system_prompt = params.get('system', [''])[0]
        user_prompt = params.get('prompt', [''])[0]

        cfg = PROVIDERS.get(provider, PROVIDERS["Custom"])
        base_url = custom_url if provider == "Custom" else cfg["base_url"]
        model = model_input if model_input else cfg["model"]

        if not api_key and provider != "Custom":
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Error: API Key is required.")
            return

        try:
            openai.api_key = api_key if api_key else "placeholder"
            openai.api_base = base_url

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
    print("🐍 Viper AI Suite running at http://127.0.0.1:8080")
    server.serve_forever()
