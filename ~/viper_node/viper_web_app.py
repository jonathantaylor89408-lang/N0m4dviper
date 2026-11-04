#!/usr/bin/env python3
"""
Viper AI Suite
Full-featured universal multi-provider playground.
"""

import json
from pathlib import Path
from typing import List, Dict, Any

import gradio as gr
from openai import OpenAI

PROFILES_FILE = Path.home() / ".viper_profiles.json"

PROVIDERS = {
    "Venice AI": {
        "base_url": "https://api.venice.ai/api/v1",
        "model": "venice-uncensored",
        "docs": "https://docs.venice.ai",
        "key_page": "https://venice.ai/settings/api",
        "notes": "Uncensored / private inference.",
        "supports_image": True,
    },
    "xAI / Grok": {
        "base_url": "https://api.x.ai/v1",
        "model": "grok-4.7",
        "docs": "https://docs.x.ai",
        "key_page": "https://console.x.ai",
        "notes": "Grok models.",
        "supports_image": True,
    },
    "OpenAI": {
        "base_url": "https://api.openai.com/v1",
        "model": "gpt-4o-mini",
        "docs": "https://platform.openai.com/docs",
        "key_page": "https://platform.openai.com/api-keys",
        "notes": "Official OpenAI.",
        "supports_image": True,
    },
    "Google Gemini": {
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
        "model": "gemini-2.5-flash",
        "docs": "https://ai.google.dev/gemini-api/docs",
        "key_page": "https://aistudio.google.com/app/apikey",
        "notes": "Gemini OpenAI-compatible.",
        "supports_image": False,
    },
    "Groq": {
        "base_url": "https://api.groq.com/openai/v1",
        "model": "llama-3.3-70b-versatile",
        "docs": "https://console.groq.com/docs",
        "key_page": "https://console.groq.com/keys",
        "notes": "Ultra-fast.",
        "supports_image": False,
    },
    "Together AI": {
        "base_url": "https://api.together.xyz/v1",
        "model": "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo",
        "docs": "https://docs.together.ai",
        "key_page": "https://api.together.ai/settings/api-keys",
        "notes": "Open models.",
        "supports_image": True,
    },
    "DeepSeek": {
        "base_url": "https://api.deepseek.com/v1",
        "model": "deepseek-chat",
        "docs": "https://api-docs.deepseek.com",
        "key_page": "https://platform.deepseek.com/api_keys",
        "notes": "Strong reasoning.",
        "supports_image": False,
    },
    "OpenRouter": {
        "base_url": "https://openrouter.ai/api/v1",
        "model": "openai/gpt-4o-mini",
        "docs": "https://openrouter.ai/docs",
        "key_page": "https://openrouter.ai/keys",
        "notes": "Aggregator.",
        "supports_image": True,
    },
    "Mistral": {
        "base_url": "https://api.mistral.ai/v1",
        "model": "mistral-large-latest",
        "docs": "https://docs.mistral.ai",
        "key_page": "https://console.mistral.ai/api-keys",
        "notes": "Mistral models.",
        "supports_image": False,
    },
    "Custom": {
        "base_url": "",
        "model": "",
        "docs": "",
        "key_page": "",
        "notes": "Enter any OpenAI-compatible base URL.",
        "supports_image": False,
    },
}

def load_profiles() -> Dict[str, Any]:
    if PROFILES_FILE.exists():
        try:
            return json.loads(PROFILES_FILE.read_text())
        except Exception:
            return {}
    return {}

def save_profiles(profiles: Dict[str, Any]):
    PROFILES_FILE.write_text(json.dumps(profiles, indent=2))

def build_links_markdown() -> str:
    lines = ["### Provider Links (Docs + API Key Pages)\n"]
    for name, cfg in PROVIDERS.items():
        if name == "Custom":
            continue
        lines.append(
            f"- **{name}**: "
            f"[Docs]({cfg['docs']}) · "
            f"[Get API Key]({cfg['key_page']}) · "
            f"Base URL: `{cfg['base_url']}`"
        )
    lines.append(
        "\n> Tip: Use the profile system to save named sets of keys locally (\~/.viper_profiles.json)."
    )
    return "\n".join(lines)

def get_client(api_key: str, base_url: str) -> OpenAI:
    return OpenAI(api_key=api_key.strip(), base_url=base_url.strip())

def list_models(provider: str, api_key: str, custom_base_url: str) -> str:
    if not api_key or not api_key.strip():
        return "Enter an API key first."
    cfg = PROVIDERS.get(provider, {})
    base_url = custom_base_url.strip() if provider == "Custom" and custom_base_url else cfg.get("base_url", "")
    if not base_url:
        return "No base URL available."
    try:
        client = get_client(api_key, base_url)
        models = client.models.list()
        model_ids = sorted([m.id for m in models.data])
        return "**Available models:**\n" + "\n".join(f"- `{m}`" for m in model_ids[:50]) + (
            f"\n\n... and {len(model_ids) - 50} more" if len(model_ids) > 50 else ""
        )
    except Exception as e:
        return f"Could not list models: {e}"

def chat_stream(
    history: List[Dict[str, str]],
    provider: str,
    api_key: str,
    model: str,
    system_prompt: str,
    user_prompt: str,
    temperature: float,
    custom_base_url: str,
):
    if not api_key or not api_key.strip():
        yield history, "Error: Please enter an API key."
        return
    if not user_prompt or not user_prompt.strip():
        yield history, "Error: Please enter a prompt."
        return

    cfg = PROVIDERS.get(provider, {})
    base_url = custom_base_url.strip() if provider == "Custom" and custom_base_url else cfg.get("base_url", "")
    if not base_url:
        yield history, "Error: No base URL."
        return

    model_to_use = model.strip() if model and model.strip() else cfg.get("model", "")

    messages = []
    if system_prompt and system_prompt.strip():
        messages.append({"role": "system", "content": system_prompt.strip()})
    for msg in history:
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": user_prompt.strip()})

    new_history = history + [{"role": "user", "content": user_prompt.strip()}]
    yield new_history, ""

    try:
        client = get_client(api_key, base_url)
        stream = client.chat.completions.create(
            model=model_to_use,
            messages=messages,
            temperature=float(temperature),
            stream=True,
        )
        full_response = ""
        for chunk in stream:
            delta = chunk.choices[0].delta.content or ""
            full_response += delta
            updated = new_history + [{"role": "assistant", "content": full_response}]
            yield updated, ""
    except Exception as e:
        err_history = new_history + [{"role": "assistant", "content": f"**Error**: {str(e)}"}]
        yield err_history, ""

def generate_image(provider: str, api_key: str, prompt: str, custom_base_url: str):
    if not api_key or not api_key.strip():
        return None, "Error: API key required."
    if not prompt or not prompt.strip():
        return None, "Error: Prompt required."

    cfg = PROVIDERS.get(provider, {})
    if not cfg.get("supports_image", False) and provider != "Custom":
        return None, f"{provider} image generation not marked as supported (you can still try with Custom)."

    base_url = custom_base_url.strip() if provider == "Custom" and custom_base_url else cfg.get("base_url", "")
    try:
        client = get_client(api_key, base_url)
        image_model = "dall-e-3" if "openai.com" in base_url else "flux"
        if "venice" in base_url:
            image_model = "flux-dev"
        response = client.images.generate(
            model=image_model,
            prompt=prompt.strip(),
            n=1,
            size="1024x1024",
        )
        url = response.data[0].url
        return url, f"Generated with model `{image_model}`"
    except Exception as e:
        return None, f"Image generation failed: {e}\n\nTry a different model name or provider."

def save_profile(profile_name: str, provider: str, api_key: str, custom_base_url: str):
    if not profile_name or not profile_name.strip():
        return "Profile name required.", gr.update()
    profiles = load_profiles()
    profiles[profile_name.strip()] = {
        "provider": provider,
        "api_key": api_key,
        "custom_base_url": custom_base_url,
    }
    save_profiles(profiles)
    return f"Saved profile '{profile_name}'", gr.update(choices=list(profiles.keys()))

def load_profile(profile_name: str):
    profiles = load_profiles()
    data = profiles.get(profile_name, {})
    return (
        data.get("provider", "Venice AI"),
        data.get("api_key", ""),
        data.get("custom_base_url", ""),
        f"Loaded profile '{profile_name}'" if data else "Profile not found",
    )

def delete_profile(profile_name: str):
    profiles = load_profiles()
    if profile_name in profiles:
        del profiles[profile_name]
        save_profiles(profiles)
        return f"Deleted '{profile_name}'", gr.update(choices=list(profiles.keys()))
    return "Profile not found", gr.update()

def feed_post(
    feed_history: str,
    provider: str,
    api_key: str,
    model: str,
    system_prompt: str,
    user_prompt: str,
    custom_base_url: str,
):
    if not api_key or not api_key.strip():
        return feed_history + "\n\n**Error:** Please enter an API key."
    if not user_prompt or not user_prompt.strip():
        return feed_history + "\n\n**Error:** Please enter a prompt."

    cfg = PROVIDERS.get(provider, {})
    base_url = custom_base_url.strip() if provider == "Custom" and custom_base_url else cfg.get("base_url", "")
    if not base_url:
        return feed_history + "\n\n**Error:** No base URL."

    model_to_use = model.strip() if model and model.strip() else cfg.get("model", "")

    messages = []
    if system_prompt and system_prompt.strip():
        messages.append({"role": "system", "content": system_prompt.strip()})
    messages.append({"role": "user", "content": user_prompt.strip()})

    try:
        client = get_client(api_key, base_url)
        completion = client.chat.completions.create(
            model=model_to_use,
            messages=messages,
            temperature=0.7,
        )
        content = completion.choices[0].message.content or "(empty)"
        entry = (
            f"\n\n---\n"
            f"**You** ({provider} / `{model_to_use}`):\n{user_prompt.strip()}\n\n"
            f"**Viper:**\n{content}"
        )
        return (feed_history or "") + entry
    except Exception as e:
        return (feed_history or "") + f"\n\n**Error:** {str(e)}"

with gr.Blocks(title="Viper AI Suite") as demo:
    gr.Markdown(
        """
        # 🐍 Viper AI Suite
        Full-featured universal playground: streaming, chat history, model listing, key profiles, image gen, and custom endpoints.
        """
    )

    with gr.Tabs():
        with gr.Tab("Chat"):
            with gr.Row():
                with gr.Column(scale=1):
                    provider_dd = gr.Dropdown(
                        choices=list(PROVIDERS.keys()),
                        value="Venice AI",
                        label="Provider",
                    )
                    api_key_tb = gr.Textbox(label="API Key", type="password", placeholder="Paste key (never stored server-side)")
                    custom_url_tb = gr.Textbox(label="Custom Base URL (only for Custom provider)", placeholder="https://your-endpoint/v1")
                    model_tb = gr.Textbox(label="Model", placeholder="Leave blank for default")
                    temp_sl = gr.Slider(0.0, 2.0, value=0.7, step=0.1, label="Temperature")
                    system_tb = gr.Textbox(label="System Prompt", value="You are a helpful AI assistant.", lines=2)
                    list_models_btn = gr.Button("List Available Models")
                    models_out = gr.Markdown()

                with gr.Column(scale=2):
                    chatbot = gr.Chatbot(label="Conversation", height=480)
                    user_tb = gr.Textbox(label="Message", placeholder="Type your message...", lines=3)
                    with gr.Row():
                        send_btn = gr.Button("Send", variant="primary")
                        clear_btn = gr.Button("Clear History")

            provider_info = gr.Markdown()

        with gr.Tab("Feed"):
            gr.Markdown("### Continuous Feed Mode")
            with gr.Row():
                feed_provider_dd = gr.Dropdown(
                    choices=list(PROVIDERS.keys()),
                    value="Venice AI",
                    label="Provider",
                )
                feed_api_key = gr.Textbox(
                    label="API Key",
                    type="password",
                    placeholder="Paste your API key here",
                )
            with gr.Row():
                feed_model = gr.Textbox(label="Model (optional)", placeholder="Leave blank for default")
                feed_custom_url = gr.Textbox(label="Custom Base URL", placeholder="Only needed for Custom provider")
            feed_system = gr.Textbox(label="System Prompt (optional)", value="You are a helpful AI assistant.", lines=1)

            gr.Markdown("---")
            gr.Markdown("### Prompt Section")
            with gr.Row():
                with gr.Column(scale=3):
                    feed_input = gr.Textbox(
                        label="Your Prompt",
                        placeholder="Type your prompt here...\nExample: Explain quantum computing in simple terms",
                        lines=5,
                    )
                with gr.Column(scale=1):
                    gr.Markdown("**Quick Prompts**")
                    qp1 = gr.Button("Why is privacy important?")
                    qp2 = gr.Button("Write a short story")
                    qp3 = gr.Button("Explain AI simply")
                    qp4 = gr.Button("Code a Python function")

            with gr.Row():
                feed_post_btn = gr.Button("Post to Feed", variant="primary")
                feed_clear_btn = gr.Button("Clear Feed")
                feed_clear_prompt_btn = gr.Button("Clear Prompt")

            gr.Markdown("---")
            feed_output = gr.Markdown(label="Feed")

        with gr.Tab("Image Generation"):
            img_provider_dd = gr.Dropdown(choices=list(PROVIDERS.keys()), value="Venice AI", label="Provider")
            img_api_key = gr.Textbox(label="API Key", type="password")
            img_custom_url = gr.Textbox(label="Custom Base URL")
            img_prompt = gr.Textbox(label="Image Prompt", lines=3)
            img_btn = gr.Button("Generate Image", variant="primary")
            img_output = gr.Image(label="Generated Image")
            img_status = gr.Markdown()

        with gr.Tab("Key Profiles"):
            gr.Markdown("Profiles are saved locally to `\~/.viper_profiles.json`.")
            profile_name_tb = gr.Textbox(label="Profile Name")
            with gr.Row():
                save_btn = gr.Button("Save Current Settings")
                load_btn = gr.Button("Load Profile")
                delete_btn = gr.Button("Delete Profile")
            profile_dd = gr.Dropdown(choices=list(load_profiles().keys()), label="Saved Profiles", interactive=True)
            profile_status = gr.Markdown()

        with gr.Tab("Provider Links"):
            gr.Markdown(build_links_markdown())

    def on_provider_change(provider):
        cfg = PROVIDERS.get(provider, {})
        info = (
            f"**Selected**: {provider}\n"
            f"**Default model**: `{cfg.get('model', '')}`\n"
            f"**Base URL**: `{cfg.get('base_url', '')}`\n"
            f"**Notes**: {cfg.get('notes', '')}\n"
            f"**Docs**: [{cfg.get('docs', '')}]({cfg.get('docs', '')})\n"
            f"**Get Key**: [{cfg.get('key_page', '')}]({cfg.get('key_page', '')})"
        )
        return cfg.get("model", ""), info

    provider_dd.change(on_provider_change, provider_dd, [model_tb, provider_info])
    demo.load(on_provider_change, provider_dd, [model_tb, provider_info])

    list_models_btn.click(
        list_models,
        [provider_dd, api_key_tb, custom_url_tb],
        models_out,
    )

    send_btn.click(
        chat_stream,
        [chatbot, provider_dd, api_key_tb, model_tb, system_tb, user_tb, temp_sl, custom_url_tb],
        [chatbot, user_tb],
    )
    user_tb.submit(
        chat_stream,
        [chatbot, provider_dd, api_key_tb, model_tb, system_tb, user_tb, temp_sl, custom_url_tb],
        [chatbot, user_tb],
    )
    clear_btn.click(lambda: ([], ""), outputs=[chatbot, user_tb])

    img_btn.click(
        generate_image,
        [img_provider_dd, img_api_key, img_prompt, img_custom_url],
        [img_output, img_status],
    )

    save_btn.click(
        save_profile,
        [profile_name_tb, provider_dd, api_key_tb, custom_url_tb],
        [profile_status, profile_dd],
    )
    load_btn.click(
        load_profile,
        profile_dd,
        [provider_dd, api_key_tb, custom_url_tb, profile_status],
    )
    delete_btn.click(
        delete_profile,
        profile_dd,
        [profile_status, profile_dd],
    )

    feed_post_btn.click(
        feed_post,
        [feed_output, feed_provider_dd, feed_api_key, feed_model, feed_system, feed_input, feed_custom_url],
        feed_output,
    )
    feed_input.submit(
        feed_post,
        [feed_output, feed_provider_dd, feed_api_key, feed_model, feed_system, feed_input, feed_custom_url],
        feed_output,
    )
    feed_clear_btn.click(lambda: "", outputs=feed_output)
    feed_clear_prompt_btn.click(lambda: "", outputs=feed_input)

    qp1.click(lambda: "Why is privacy important in AI systems?", outputs=feed_input)
    qp2.click(lambda: "Write a short creative story about a robot discovering emotions.", outputs=feed_input)
    qp3.click(lambda: "Explain artificial intelligence in simple terms a 10-year-old can understand.", outputs=feed_input)
    qp4.click(lambda: "Write a Python function that calculates the Fibonacci sequence up to n terms.", outputs=feed_input)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860, share=False, theme=gr.themes.Soft())
