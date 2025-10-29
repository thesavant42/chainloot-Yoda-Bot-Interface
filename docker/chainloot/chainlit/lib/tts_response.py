# lib/tts_response.py

import chainlit as cl
import logging
import time
from lib.tts import generate_speech
from lib.config_handler import config, tts_client

logger = logging.getLogger(__name__)


async def generate_audio_response(text: str, message_id: str):
    """
    Generate and send TTS audio for a given text to Chainlit UI.
    This is a high-level function that handles Chainlit session data and UI interaction.
    
    Args:
        text: The text to convert to speech
        message_id: The Chainlit message ID to attach the audio to
    """
    # Get session-specific TTS settings
    selected_voice = cl.user_session.get("selected_voice")
    tts_speed = cl.user_session.get("tts_speed")
    tts_exaggeration = cl.user_session.get("tts_exaggeration")
    
    # Build TTS configuration parameters from global config
    tts_config_params = {
        "cfg_weight": config.get("tts_cfg_weight"),
        "temperature": config.get("tts_temperature"),
        "device": config.get("tts_device"),
        "dtype": config.get("tts_dtype"),
        "seed": config.get("tts_seed"),
        "chunked": config.get("tts_chunked"),
        "use_compilation": config.get("tts_use_compilation"),
        "max_new_tokens": config.get("tts_max_new_tokens"),
        "max_cache_len": config.get("tts_max_cache_len"),
        "desired_length": config.get("tts_desired_length"),
        "max_length": config.get("tts_max_length"),
        "halve_first_chunk": config.get("tts_halve_first_chunk"),
        "cpu_offload": config.get("tts_cpu_offload"),
        "cache_voice": config.get("tts_cache_voice"),
        "tokens_per_slice": config.get("tts_tokens_per_slice"),
        "remove_milliseconds": config.get("tts_remove_milliseconds"),
        "remove_milliseconds_start": config.get("tts_remove_milliseconds_start"),
        "chunk_overlap_method": config.get("tts_chunk_overlap_method")
    }

    # Generate the audio using the low-level TTS function
    tts_start_time = time.time()
    audio_buffer = await generate_speech(
        tts_client=tts_client,
        text=text,
        voice=selected_voice,
        tts_model=config.get("tts_model_name"),
        response_format=config.get("tts_response_format"),
        speed=tts_speed,
        exaggeration=tts_exaggeration,
        tts_config=tts_config_params
    )
    tts_end_time = time.time()
    logger.info(f"PERF: TTS call took {tts_end_time - tts_start_time:.2f} seconds.")

    # Send the audio to Chainlit UI
    await cl.Audio(
        name="response_audio.wav",
        content=audio_buffer,
        mime="audio/wav",
        auto_play=True
    ).send(for_id=message_id)