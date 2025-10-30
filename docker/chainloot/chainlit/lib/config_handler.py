# lib/config_handler.py

import os
import json
import sys
import requests
from dotenv import load_dotenv
from openai import AsyncOpenAI
from chainlit.logger import logger

load_dotenv()

# --- Load Config File ---
try:
    with open('config/config.json', 'r') as f:
        config = json.load(f)
except (FileNotFoundError, json.JSONDecodeError) as e:
    logger.error(f"Fatal: Failed to load config/config.json: {e}")
    sys.exit(1)

## Is this even used anymore???? TODO
# --- Static Data & Constants ---
prompt_catalog = {
    "AI": "You are a 3-P-O, a helpful AI assistant. Your responses are concise and brief. No more than 2 sentences per message.",
    "Yoda": "You are Yoda, wise Jedi Master. Reply in Yoda-speak. No more than 2 sentences per message.",
    "Stark": "You are a helpful but snarky AI assistant. Your name is Tony. No more than 2 sentences per message."
}

lm_studio_url = config.get("lm_studio_base_url", "").rstrip('/v1')
chatterbox_url = config.get("tts_base_url", "")
api_key = os.getenv("LM_API_KEY", config.get("api_key"))

# --- API Client Initialization ---
# Ensure URLs are not empty before creating clients
if not lm_studio_url:
    logger.error("lm_studio_url not found in config.json. Exiting.")
    sys.exit(1)
if not chatterbox_url:
    logger.error("chatterbox_url not found in config.json. Exiting.")
    sys.exit(1)

# Legacy client for backward compatibility (will be replaced by get_client)
client = AsyncOpenAI(base_url=f"{lm_studio_url}/v1", api_key=api_key)
tts_client = AsyncOpenAI(base_url=f"{chatterbox_url}/v1", api_key=api_key)
stt_client = AsyncOpenAI(base_url=f"{chatterbox_url}/v1", api_key=api_key)

# --- Dynamic Client Factory ---
def get_client():
    """Get the appropriate AsyncOpenAI client based on current provider"""
    provider = config.get("provider", "lm-studio")
    
    if provider == "ollama":
        base_url = "http://ollama:11434/v1"
        api_key = os.getenv("OLLAMA_API_KEY", "ollama")
    elif provider == "lm-studio":
        base_url = f"{lm_studio_url}/v1"
        api_key = os.getenv("LM_API_KEY", config.get("api_key"))
    else:
        # Default to LM Studio
        base_url = f"{lm_studio_url}/v1"
        api_key = os.getenv("LM_API_KEY", config.get("api_key"))
    
    return AsyncOpenAI(base_url=base_url, api_key=api_key)


def get_chat_settings():
    """Get chat completion settings based on current provider and config"""
    model = config.get("last_used_model", "")
    temperature = config.get("temperature", 0.7)
    max_tokens = config.get("max_tokens", 2048)
    
    return {
        "model": model,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

# --- Dynamic Asset Fetching (Functions) ---
def fetch_available_models(provider=None):
    """Fetches available LLM models from the specified provider."""
    if provider is None:
        provider = config.get("provider", "lm-studio")
    
    try:
        if provider == "ollama":
            # Ollama uses /api/tags endpoint
            ollama_url = "http://ollama:11434/api/tags"
            response = requests.get(ollama_url, timeout=10)
            response.raise_for_status()
            models_data = response.json()
            return [model["name"] for model in models_data.get("models", [])]
        elif provider == "lm-studio":
            # LM Studio uses /api/v0/models endpoint
            response = requests.get(f"{lm_studio_url}/api/v0/models", timeout=10)
            response.raise_for_status()
            models_data = response.json()
            return [m["id"] for m in models_data.get("data", []) if m.get("type") == "llm" and "whisper" not in m.get("id", "").lower()]
        else:
            logger.error(f"Unknown provider: {provider}")
            return []
    except Exception as e:
        logger.error(f"Could not fetch models from {provider}: {e}")
        return []

def fetch_available_voices():
    """Fetches available TTS voices from Chatterbox API."""
    max_retries = 5
    for attempt in range(max_retries):
        try:
            voices_response = requests.get(f"{chatterbox_url}/v1/audio/voices/chatterbox", timeout=10)
            voices_response.raise_for_status()
            voices_data = voices_response.json()
            return voices_data.get("voices", [])
        except Exception as e:
            logger.warning(f"Could not fetch voices from TTS API (attempt {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                import time
                time.sleep(2)  # Wait 2 seconds before retry
            else:
                logger.error(f"Failed to fetch voices after {max_retries} attempts, returning empty list")
                return []

# --- Load Dynamic Assets on Startup ---
available_models = fetch_available_models()
if not available_models:
    current_provider = config.get("provider", "lm-studio")
    logger.warning(f"Preferred provider '{current_provider}' is not accessible or has no models. User can switch providers in settings.")

voices_data = fetch_available_voices()
available_voices = [v.get("value") for v in voices_data if v.get("value")]