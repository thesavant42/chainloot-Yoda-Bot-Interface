# TTS (Text-to-Speech) related functions

import requests
import json
from openai import AsyncOpenAI
import cl
from chainlit.logger import logger
from io import BytesIO

# Placeholder for configuration loading - this will be handled by app.py or a shared config module
# For now, we'll assume these are passed in or globally available.

# --- TTS Core Functionality ---

def fetch_available_voices(tts_api_url: str) -> list[dict]:
    """
    Fetches available TTS voices from the Chatterbox API.

    Args:
        tts_api_url: The base URL for the Chatterbox TTS API.

    Returns:
        A list of voice dictionaries, each containing 'value' and 'label'.

    Raises:
        Exception: If there's an error communicating with the TTS API.
    """
    try:
        voices_response = requests.get(f"{tts_api_url}/v1/audio/voices/chatterbox")
        voices_response.raise_for_status()
        voices_data = voices_response.json()
        return voices_data.get("voices", [])
    except Exception as e:
        logger.error(f"TTS: Could not fetch voices from {tts_api_url}: {e}")
        raise Exception(f"Failed to fetch TTS voices: {e}")

async def generate_speech(
    tts_client: AsyncOpenAI,
    text: str,
    voice: str,
    tts_model: str,
    response_format: str = "wav",
    speed: float = 1.0,
    exaggeration: float = 1.0,
    tts_config: dict = None # Dictionary containing extra TTS parameters
) -> bytes:
    """
    Generates speech audio from text using the provided TTS client.

    Args:
        tts_client: An initialized AsyncOpenAI client configured for TTS.
        text: The text to convert to speech.
        voice: The TTS voice to use.
        tts_model: The TTS model to use.
        response_format: The format of the audio response (e.g., "wav", "mp3").
        speed: The speed of the speech.
        exaggeration: The exaggeration factor for the speech.
        tts_config: Dictionary containing additional TTS parameters like cfg_weight, temperature, etc.

    Returns:
        The generated audio as bytes.

    Raises:
        Exception: If speech generation fails.
    """
    if tts_config is None:
        tts_config = {}

    # Ensure all required keys are present with defaults if not provided in tts_config
    # These defaults should align with those in app.py or be sensible fallbacks.
    params_dict = {
        "exaggeration": exaggeration,
        "cfg_weight": tts_config.get("cfg_weight", 5.0),
        "temperature": tts_config.get("temperature", 1.4),
        "device": tts_config.get("device", "cpu"),
        "dtype": tts_config.get("dtype", "float32"),
        "seed": tts_config.get("seed", -1),
        "chunked": tts_config.get("chunked", False),
        "use_compilation": tts_config.get("use_compilation", False),
        "max_new_tokens": tts_config.get("max_new_tokens", 512),
        "max_cache_len": tts_config.get("max_cache_len", 0),
        "desired_length": tts_config.get("desired_length", None),
        "max_length": tts_config.get("max_length", None),
        "halve_first_chunk": tts_config.get("halve_first_chunk", True),
        "cpu_offload": tts_config.get("cpu_offload", False),
        "cache_voice": tts_config.get("cache_voice", False),
        "tokens_per_slice": tts_config.get("tokens_per_slice", None),
        "remove_milliseconds": tts_config.get("remove_milliseconds", None),
        "remove_milliseconds_start": tts_config.get("remove_milliseconds_start", None),
        "chunk_overlap_method": tts_config.get("chunk_overlap_method", "undefined")
    }

    logger.info(f"TTS: Generating speech - Model: {tts_model}, Voice: {voice}, Speed: {speed}, Exaggeration: {exaggeration}")

    buffer = b""
    try:
        async with tts_client.audio.speech.with_streaming_response.create(
            model=tts_model,
            input=text,
            voice=voice,
            response_format=response_format,
            speed=speed,
            extra_body={"params": params_dict}
        ) as response:
            async for chunk in response.iter_bytes():
                buffer += chunk
        logger.info(f"TTS: Speech generation successful - Audio bytes: {len(buffer)}")
        return buffer
    except Exception as e:
        logger.error(f"TTS: Speech generation failed: {str(e)}")
        raise Exception(f"TTS speech generation failed: {str(e)}")

# --- References to update ---
# - Calls to tts_client.audio.speech.with_streaming_response.create
# - Usage of cl.Audio
# - Logic within on_audio_end related to TTS generation
# - Fetching of available TTS voices
# - Configuration variables related to TTS (model, voice, speed, exaggeration, etc.)