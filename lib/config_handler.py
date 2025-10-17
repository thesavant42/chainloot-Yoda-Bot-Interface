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

client = AsyncOpenAI(base_url=f"{lm_studio_url}/v1", api_key=api_key)
tts_client = AsyncOpenAI(base_url=f"{chatterbox_url}/v1", api_key=api_key)
stt_client = AsyncOpenAI(base_url=f"{chatterbox_url}/v1", api_key=api_key)

# --- Dynamic Asset Fetching (Functions) ---
def fetch_available_models():
    """Fetches available LLM models from LM Studio."""
    try:
        response = requests.get(f"{lm_studio_url}/api/v0/models")
        response.raise_for_status()
        models_data = response.json()["data"]
        return [m["id"] for m in models_data if m.get("type") == "llm" and "whisper" not in m.get("id", "").lower()]
    except Exception as e:
        logger.error(f"Could not fetch models from LM Studio: {e}")
        return []

def fetch_available_voices():
    """Fetches available TTS voices from Chatterbox API."""
    try:
        voices_response = requests.get(f"{chatterbox_url}/v1/audio/voices/chatterbox")
        voices_response.raise_for_status()
        voices_data = voices_response.json()
        return voices_data.get("voices", [])
    except Exception as e:
        logger.error(f"Could not fetch voices from TTS API: {e}")
        return []

# --- Load Dynamic Assets on Startup ---
available_models = fetch_available_models()
voices_data = fetch_available_voices()
available_voices = [v.get("value") for v in voices_data if v.get("value")]