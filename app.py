import os
from dotenv import load_dotenv
import requests
import json
from openai import AsyncOpenAI, OpenAI
import asyncio
import chainlit as cl
from chainlit.logger import logger
from io import BytesIO
from chainlit.input_widget import Select, Slider, Switch
import sys
import wave

# Import the new message processing function
from lib.message_processor import process_message_for_tts

def raw_pcm_to_wav(pcm_bytes, sample_rate=16000, channels=1, sample_width=2):
    """Convert raw PCM bytes to WAV bytes."""
    wav_buffer = BytesIO()
    with wave.open(wav_buffer, 'wb') as wav_file:
        wav_file.setnchannels(channels)
        wav_file.setsampwidth(sample_width)  # 2 bytes for 16-bit
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(pcm_bytes)
    return wav_buffer.getvalue()

load_dotenv()

# Load config.json
config_path = 'config.json'

try:
    with open(config_path, 'r') as f:
        config = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    print(f"Error: Failed to load {config_path}. Exiting.")
    sys.exit(1)

LM_STUDIO_URL = config["lm_studio_base_url"].rstrip('/v1')
CHATTERBOX_URL = config["tts_base_url"]
TTS_WEBUI_URL = config["tts_webui_url"]

# Fetch available voices for Chatterbox dynamically from API
try:
    voices_response = requests.get(f"{CHATTERBOX_URL}/v1/audio/voices/chatterbox")
    voices_response.raise_for_status()
    voices_data = voices_response.json()
    available_voices = [v["value"] for v in voices_data["voices"]]
    if config["tts_voice"] not in available_voices:
        print(f"Warning: Config voice {config['tts_voice']} not in available voices. Using first available.")
        config["tts_voice"] = available_voices[0] if available_voices else config["tts_voice"]
except Exception as e:
    voices_data = [{"value": config["tts_voice"], "label": config["tts_voice"]}]
    available_voices = [config["tts_voice"]]
    print(f"Warning: Could not fetch voices from API: {e}. Using config voice.")

tts_model = config["tts_model_name"]
tts_voice = config["tts_voice"]
print(f"Using TTS voice: {tts_voice}")

# Fetch available LLM models dynamically
def fetch_available_models():
    try:
        response = requests.get(f"{LM_STUDIO_URL}/api/v0/models")
        response.raise_for_status()
        models_data = response.json()["data"]
        # Filter for chat/LLM models, exclude STT/Whisper models
        return [m["id"] for m in models_data if m["type"] == "llm" and "whisper" not in m["id"].lower()]
    except Exception as e:
        raise Exception(f"Could not fetch models from LM Studio: {e}")

available_models = fetch_available_models()

api_key = os.getenv("LM_API_KEY", config["api_key"])
client = AsyncOpenAI(base_url=f"{LM_STUDIO_URL}/v1", api_key=api_key)
tts_client = AsyncOpenAI(base_url=f"{CHATTERBOX_URL}/v1", api_key=api_key)

# Sync client for STT transcription
stt_client = OpenAI(base_url=f"{CHATTERBOX_URL}/v1", api_key=api_key)
# Instrument the OpenAI client
cl.instrument_openai()

# Defaults from config
default_llm_temp = 0.0
default_max_tokens = 1000
default_tts_speed = config["tts_speed"]
default_tts_exaggeration = config["tts_exaggeration"]
default_tts_voice = config["tts_voice"]
default_tts_model = config["tts_model_name"]
default_tts_response_format = config["tts_response_format"]
default_tts_stream = config["tts_stream"]

# Prompt catalog
prompt_catalog = {
    "AI": "You are a 3-P-O, a helpful AI assistant. Your responses are concise and brief. No more than 2 sentences per message.",
    "Yoda": "You are Yoda, wise Jedi Master. Reply in Yoda-speak. No more than 2 sentences per message.",
    "Stark": "You are a helpful but snarky AI assistant. Your name is Tony. No more than 2 sentences per message."
}

# Character profiles for chat participants
character_options = list(prompt_catalog.keys())

settings = {
    "temperature": default_llm_temp,
    "max_tokens": default_max_tokens,
}

@cl.on_chat_start
async def on_chat_start():
    logger.info(f"AUDIO DIAG: Chat start - Session ID: {cl.context.session.id}, STT client base: {stt_client.base_url}")
    
    # Load initial settings from config.json
    selected_model = config.get("last_used_model", available_models[0] if available_models else "default_model")
    cl.user_session.set("selected_model", selected_model)
    
    selected_voice = config.get("tts_voice", default_tts_voice)
    cl.user_session.set("selected_voice", selected_voice)
    
    system_prompt_key = config.get("system_prompt_key", "AI") # Default to "AI" if not found
    cl.user_session.set("system_prompt", prompt_catalog.get(system_prompt_key, prompt_catalog["AI"]))
    
    character = config.get("character", list(prompt_catalog.keys())[0])
    cl.user_session.set("character", character)
    
    llm_temp = config.get("lm_studio_temperature", default_llm_temp)
    cl.user_session.set("llm_temp", llm_temp)
    
    max_tokens = config.get("max_tokens", default_max_tokens)
    cl.user_session.set("max_tokens", max_tokens)
    
    tts_speed = config.get("tts_speed", default_tts_speed)
    cl.user_session.set("tts_speed", tts_speed)
    
    tts_exaggeration = config.get("tts_exaggeration", default_tts_exaggeration)
    cl.user_session.set("tts_exaggeration", tts_exaggeration)
    
    reasoning_enabled = config.get("reasoning_enabled", False)
    cl.user_session.set("reasoning_enabled", reasoning_enabled)

    # Find initial index for voice and model
    voice_index = available_voices.index(selected_voice) if selected_voice in available_voices else 0
    model_index = available_models.index(selected_model) if selected_model in available_models else 0
    system_prompt_index = list(prompt_catalog.keys()).index(system_prompt_key) if system_prompt_key in prompt_catalog else 0
    # character_index = character_options.index(character) if character in character_options else 0

    # Send dynamic chat settings form for voice and other options
    settings_form = await cl.ChatSettings(
        [
            Select(
                id="voice",
                label="TTS Voice",
                values=available_voices,
                initial_index=voice_index
            ),
            Select(
                id="model",
                label="LLM Model",
                values=available_models,
                initial_index=model_index
            ),
            Select(
                id="model_refresh",
                label="Model Refresh",
                values=["No Action", "Refresh Now"],
                initial_index=0
            ),
            Select(
                id="system_prompt",
                label="System Prompt",
                values=list(prompt_catalog.keys()),
                initial_index=system_prompt_index
            ),
            Slider(
                id="llm_temp",
                label="LLM Temperature",
                initial=llm_temp,
                min=0.0,
                max=2.0,
                step=0.1
            ),
            Slider(
                id="max_tokens",
                label="Max Tokens",
                initial=max_tokens,
                min=100,
                max=2000,
                step=50
            ),
            Slider(
                id="tts_speed",
                label="TTS Speed",
                initial=tts_speed,
                min=0.25,
                max=4.0,
                step=0.05
            ),
            Slider(
                id="tts_exaggeration",
                label="TTS Exaggeration",
                initial=tts_exaggeration,
                min=0.0,
                max=1.0,
                step=0.1
            ),
            Slider(
                id="tts_temperature",
                label="TTS Temperature",
                initial=config.get("tts_temperature", 1.4), # Use value from config.json, default to 1.4
                min=0.0,
                max=2.0,
                step=0.1
            ),
            Switch(
                id="reasoning_enabled",
                label="Enable Reasoning",
                initial=reasoning_enabled
            )
        ]
    ).send()

    await cl.Message(content=f"Model: {selected_model}  Voice: {selected_voice}").send()
    await cl.Message(content="Voice mode ready! Click the microphone icon, record your speech, and send – it will be transcribed automatically.").send()

    # Settings are now managed via user_session; UI actions removed due to API incompatibility

@cl.on_settings_update
async def on_settings_update(settings):
    cl.user_session.set("selected_model", settings["model"])
    cl.user_session.set("selected_voice", settings["voice"])
    cl.user_session.set("system_prompt", prompt_catalog[settings["system_prompt"]])
    # Set character to the same value as the system prompt key
    cl.user_session.set("character", settings["system_prompt"])
    cl.user_session.set("llm_temp", settings["llm_temp"])
    cl.user_session.set("max_tokens", int(settings["max_tokens"]))
    cl.user_session.set("tts_speed", settings["tts_speed"])
    cl.user_session.set("tts_exaggeration", settings["tts_exaggeration"])
    cl.user_session.set("reasoning_enabled", settings["reasoning_enabled"])

    # Persist settings to config.json
    try:
        with open(config_path, 'r') as f:
            current_config = json.load(f)

        # Update settings that are directly mapped to config.json
        if "voice" in settings:
            current_config["tts_voice"] = settings["voice"]
        if "model" in settings:
            # Persist the selected LLM model to last_used_model
            current_config["last_used_model"] = settings["model"]
        if "system_prompt" in settings:
            # Persist system prompt (note: prompt_catalog is defined in app.py, not config.json)
            # We'll store the key here, and the full prompt will be resolved on load.
            current_config["system_prompt_key"] = settings["system_prompt"]
        if "character" in settings:
            # Persist character
            current_config["character"] = settings["character"]
        if "llm_temp" in settings:
            current_config["lm_studio_temperature"] = settings["llm_temp"]
        if "max_tokens" in settings:
            current_config["max_tokens"] = settings["max_tokens"]
        if "tts_speed" in settings:
            current_config["tts_speed"] = settings["tts_speed"]
        if "tts_exaggeration" in settings:
            current_config["tts_exaggeration"] = settings["tts_exaggeration"]
        if "tts_temperature" in settings: # Persist TTS Temperature
            current_config["tts_temperature"] = settings["tts_temperature"]
        if "reasoning_enabled" in settings: # Persist Reasoning Enabled
            current_config["reasoning_enabled"] = settings["reasoning_enabled"]
        
        # Write the updated config back to the file
        with open(config_path, 'w') as f:
            json.dump(current_config, f, indent=4)
            
    except Exception as e:
        logger.error(f"Failed to persist settings to {config_path}: {e}")

    if settings["model_refresh"] == "Refresh Now":
        try:
            updated_models = fetch_available_models()
            old_models = cl.user_session.get("available_models", available_models)
            new_models = [m for m in updated_models if m not in old_models]
            cl.user_session.set("available_models", updated_models)
            
            if new_models:
                notification = f"Models refreshed! New models added: {', '.join(new_models)}"
            else:
                notification = "Models refreshed. No new models detected."
            
            # Update selected_model if it was removed
            selected_model = cl.user_session.get("selected_model")
            if selected_model not in updated_models:
                new_selected = updated_models[0] if updated_models else available_models[0]
                cl.user_session.set("selected_model", new_selected)
                notification += f" Switched to {new_selected}."
            
            await cl.Message(content=notification).send()
        except Exception as e:
            await cl.Message(content=f"Failed to refresh models: {str(e)}").send()
        # Note: User can select "No Action" to stop further refreshes

@cl.on_message
async def on_message(message: cl.Message):
    logger.info(f"AUDIO DIAG: on_message triggered - Session ID: {cl.context.session.id}, Elements count: {len(message.elements) if message.elements else 0}, Content: '{message.content[:50]}...'")
    logger.info(f"AUDIO DIAG: Message type: {type(message)}, Elements types: {[type(e).__name__ for e in (message.elements or [])]}")
    # Handle audio elements from mic or file uploads for STT
    if message.elements:
        logger.info(f"AUDIO DIAG: Processing {len(message.elements)} elements")
        for i, element in enumerate(message.elements):
            logger.info(f"AUDIO DIAG: Element {i}: type={type(element).__name__}, name={getattr(element, 'name', 'N/A')}")
            logger.info(f"AUDIO DIAG: Element attributes: {dir(element)}")
            logger.info(f"AUDIO DIAG: Element dict: {element.__dict__ if hasattr(element, '__dict__') else 'No __dict__'}")
            audio_bytes = None
            if isinstance(element, cl.Audio):
                # Handle direct audio from microphone widget or uploaded audio
                if element.content is not None:
                    audio_bytes = element.content
                    logger.info(f"AUDIO DIAG: Audio element content direct - Name: {element.name}, Mime: {element.mime}, Length: {len(audio_bytes)} bytes")
                else:
                    logger.warning(f"AUDIO DIAG: Audio element content is None for {element.name}")
                    # Try path if available
                    if hasattr(element, 'path') and element.path:
                        try:
                            with open(element.path, 'rb') as f:
                                audio_bytes = f.read()
                            logger.info(f"AUDIO DIAG: Audio element from path - Name: {element.name}, Path: {element.path}, Length: {len(audio_bytes)} bytes")
                        except Exception as path_err:
                            logger.error(f"AUDIO DIAG: Failed to read from path: {path_err}")
                    else:
                        logger.warning(f"AUDIO DIAG: No path available for Audio element {element.name}")
            elif isinstance(element, cl.File) and element.type.startswith("audio/"):
                # Fallback for manual file upload
                audio_bytes = await element.read()
                logger.info(f"AUDIO DIAG: Audio file uploaded - Name: {element.name}, Type: {element.type}, Length: {len(audio_bytes)} bytes")
            
            if audio_bytes is None:
                logger.warning(f"AUDIO DIAG: No audio bytes found for element {i}")
                continue
            logger.info(f"AUDIO DIAG: Found audio bytes, length: {len(audio_bytes)}")
            try:
                # 1. Speech-to-Text
                logger.info(f"AUDIO DIAG: Calling STT API - Model: {config.get('whisper_model', 'openai/whisper-tiny.en')}, URL: {stt_client.base_url}, Bytes: {len(audio_bytes)}")
                
                # For uploaded files, assume WAV; for raw (e.g., potential mic elements), convert
                # Check if it's raw PCM (no path indicates possible raw from widget)
                is_raw_pcm = not hasattr(element, 'path') or not element.path
                if is_raw_pcm:
                    wav_bytes = raw_pcm_to_wav(audio_bytes, sample_rate=16000)
                    logger.info(f"AUDIO DIAG: Converted {len(audio_bytes)} PCM bytes to {len(wav_bytes)} WAV bytes")
                    audio_for_stt = wav_bytes
                else:
                    audio_for_stt = audio_bytes
                
                transcription = stt_client.audio.transcriptions.create(
                    model=config.get("whisper_model", "openai/whisper-small.en"),
                    file=("recorded_audio.wav", BytesIO(audio_for_stt)),
                )
                user_text = transcription.text.strip()
                logger.info(f"AUDIO DIAG: STT response - Text length: {len(user_text)}, Text: '{user_text[:50]}...'")
                
                if not user_text:
                    await cl.Message(content="No speech detected in audio.").send()
                    return

                # Display transcribed text as user message
                user_msg = await cl.Message(content=user_text).send()

                # Reuse logic for LLM and TTS
                session_models = cl.user_session.get("available_models")
                current_models = session_models if session_models else available_models
                selected_model = cl.user_session.get("selected_model") or current_models[0]
                system_prompt = cl.user_session.get("system_prompt", prompt_catalog["AI"])
                reasoning_enabled = cl.user_session.get("reasoning_enabled", False)
                if reasoning_enabled:
                    system_prompt += " Think step by step before responding."
                llm_temp = cl.user_session.get("llm_temp", default_llm_temp)
                max_tokens = cl.user_session.get("max_tokens", default_max_tokens)

                # 2. LLM Inference
                response = await client.chat.completions.create(
                    model=selected_model,
                    messages=[
                        {"content": system_prompt, "role": "system"},
                        {"content": user_text, "role": "user"}
                    ],
                    temperature=llm_temp,
                    max_tokens=max_tokens,
                )
                full_response = response.choices[0].message.content

                # --- Sentiment Analysis Integration ---
                # Process the full response for sentiment analysis and debugging.
                # The process_message_for_tts function will handle chunking, scrubbing,
                # sentiment classification, and printing debug statements.
                # For now, we are not directly using the sentiment to influence TTS,
                # but the debug statements will be printed.
                # Future work could involve using processed_message_data to influence TTS.
                processed_message_data = process_message_for_tts(full_response)
                # --- End Sentiment Analysis Integration ---
            
                character = cl.user_session.get("character", list(prompt_catalog.keys())[0])
                text_msg = await cl.Message(content=f"[{character}]: {full_response}").send()
            
                # --- Sentiment Analysis Integration ---
                # Process the full response for sentiment analysis and debugging.
                # The process_message_for_tts function will handle chunking, scrubbing,
                # sentiment classification, and printing debug statements.
                # For now, we are not directly using the sentiment to influence TTS,
                # but the debug statements will be printed.
                # Future work could involve using processed_message_data to influence TTS.
                processed_message_data = process_message_for_tts(full_response)
                # --- End Sentiment Analysis Integration ---
            
                # 3. Text-to-Speech
                selected_voice = cl.user_session.get("selected_voice", default_tts_voice)
                tts_speed = cl.user_session.get("tts_speed", default_tts_speed)
                tts_exaggeration = cl.user_session.get("tts_exaggeration", default_tts_exaggeration)
            
                params_dict = {
                    "exaggeration": tts_exaggeration,
                    "cfg_weight": config["tts_cfg_weight"],
                    "temperature": config["tts_temperature"],
                    "device": config["tts_device"],
                    "dtype": config["tts_dtype"],
                    "seed": config["tts_seed"],
                    "chunked": config["tts_chunked"],
                    "use_compilation": config["tts_use_compilation"],
                    "max_new_tokens": config["tts_max_new_tokens"],
                    "max_cache_len": config["tts_max_cache_len"],
                    "desired_length": config["tts_desired_length"],
                    "max_length": config["tts_max_length"],
                    "halve_first_chunk": True,
                    "cpu_offload": False,
                    "cache_voice": False,
                    "tokens_per_slice": None,
                    "remove_milliseconds": None,
                    "remove_milliseconds_start": None,
                    "chunk_overlap_method": "undefined"
                }
            
                buffer = b""
                async with tts_client.audio.speech.with_streaming_response.create(
                    model=default_tts_model,
                    input=full_response, # Keep original full_response for TTS input for now
                    voice=selected_voice,
                    response_format=default_tts_response_format,
                    speed=tts_speed,
                    extra_body={"params": params_dict}
                ) as response:
                    async for chunk in response.iter_bytes():
                        buffer += chunk

                tts_audio = cl.Audio(
                    name="response_audio.wav",
                    content=buffer,
                    mime="audio/wav",
                    auto_play=True
                )
                await tts_audio.send(for_id=text_msg.id)

            except Exception as e:
                logger.error(f"AUDIO DIAG: STT or processing error: {str(e)}")
                await cl.Message(content=f"Error processing audio: {str(e)}").send()
            return

    # Handle text messages
    if not message.content:
        logger.info("AUDIO DIAG: Empty content and no elements, skipping")
        return

    logger.info(f"Processing text message: {message.content[:100]}...")
    
    # Use latest models from session if available, else global
    session_models = cl.user_session.get("available_models")
    current_models = session_models if session_models else available_models
    selected_model = cl.user_session.get("selected_model")
    if not selected_model:
        selected_model = current_models[0]
    
    system_prompt = cl.user_session.get("system_prompt", prompt_catalog["AI"])
    reasoning_enabled = cl.user_session.get("reasoning_enabled", False)
    if reasoning_enabled:
        system_prompt += " Think step by step before responding."
    
    llm_temp = cl.user_session.get("llm_temp", default_llm_temp)
    max_tokens = cl.user_session.get("max_tokens", default_max_tokens)
    
    response = await client.chat.completions.create(
        model=selected_model,
        messages=[
            {
                "content": system_prompt,
                "role": "system"
            },
            {
                "content": message.content,
                "role": "user"
            }
        ],
        temperature=llm_temp,
        max_tokens=max_tokens,
    )
    text_content = response.choices[0].message.content
    
    character = cl.user_session.get("character", list(prompt_catalog.keys())[0])
    # Send text response with character context if needed
    text_msg = await cl.Message(content=f"[{character}]: {text_content}").send()
    
    # Generate TTS audio streaming
    selected_voice = cl.user_session.get("selected_voice", default_tts_voice)
    tts_speed = cl.user_session.get("tts_speed", default_tts_speed)
    tts_exaggeration = cl.user_session.get("tts_exaggeration", default_tts_exaggeration)

    params_dict = {
        "exaggeration": tts_exaggeration,
        "cfg_weight": config["tts_cfg_weight"],
        "temperature": config["tts_temperature"],
        "device": config["tts_device"],
        "dtype": config["tts_dtype"],
        "seed": config["tts_seed"],
        "chunked": config["tts_chunked"],
        "use_compilation": config["tts_use_compilation"],
        "max_new_tokens": config["tts_max_new_tokens"],
        "max_cache_len": config["tts_max_cache_len"],
        "desired_length": config["tts_desired_length"],
        "max_length": config["tts_max_length"],
        "halve_first_chunk": True,
        "cpu_offload": False,
        "cache_voice": False,
        "tokens_per_slice": None,
        "remove_milliseconds": None,
        "remove_milliseconds_start": None,
        "chunk_overlap_method": "undefined"
    }

    buffer = b""
    async with tts_client.audio.speech.with_streaming_response.create(
        model=default_tts_model,
        input=text_content,
        voice=selected_voice,
        response_format=default_tts_response_format,
        speed=tts_speed,
        extra_body={"params": params_dict}
    ) as response:
        async for chunk in response.iter_bytes():
            buffer += chunk

    audio = cl.Audio(
        name="response_audio.wav",
        content=buffer,
        mime="audio/wav",
        auto_play=True
    )
    await audio.send(for_id=text_msg.id)

@cl.on_audio_chunk
async def on_audio_chunk(chunk):
    """Handle audio chunks from microphone recording."""
    if chunk.isStart:
        # Initialize audio buffer for new recording
        buffer = []
        cl.user_session.set("audio_buffer", buffer)
        logger.info(f"AUDIO DIAG: on_audio_chunk START - Session ID: {cl.context.session.id}")
        return
    
    # Append audio chunk to buffer
    audio_buffer = cl.user_session.get("audio_buffer")
    if audio_buffer is not None:
        audio_buffer.append(chunk.data)
        cl.user_session.set("audio_buffer", audio_buffer)

@cl.on_audio_start
async def on_audio_start():
    logger.info(f"AUDIO DIAG: on_audio_start triggered - Session ID: {cl.context.session.id}")
    return True

@cl.on_audio_end
async def on_audio_end():
    logger.info(f"AUDIO DIAG: on_audio_end triggered - Session ID: {cl.context.session.id}")
    audio_buffer = cl.user_session.get("audio_buffer")
    if not audio_buffer:
        logger.warning(f"AUDIO DIAG: Empty audio buffer at end of recording")
        return
    
    # Combine all chunks into single audio bytes
    audio_bytes = b"".join(audio_buffer)
    logger.info(f"AUDIO DIAG: Combined audio chunks - Total bytes: {len(audio_bytes)}")
    
    # Clear buffer
    cl.user_session.set("audio_buffer", None)
    
    try:
        # 1. Speech-to-Text
        logger.info(f"AUDIO DIAG: Calling STT API - Model: {config.get('whisper_model', 'openai/whisper-tiny.en')}, URL: {stt_client.base_url}, Bytes: {len(audio_bytes)}")
        
        # Convert raw PCM to WAV for STT
        wav_bytes = raw_pcm_to_wav(audio_bytes, sample_rate=24000)
        logger.info(f"AUDIO DIAG: Converted {len(audio_bytes)} PCM bytes to {len(wav_bytes)} WAV bytes")
        
        transcription = stt_client.audio.transcriptions.create(
            model=config.get("whisper_model", "openai/whisper-small.en"),
            file=("recorded_audio.wav", BytesIO(wav_bytes)),
        )
        user_text = transcription.text.strip()
        logger.info(f"AUDIO DIAG: STT response - Text length: {len(user_text)}, Text: '{user_text[:50]}...'")
        
        if not user_text:
            await cl.Message(content="No speech detected in audio.").send()
            return

        # Display transcribed text as user message
        await cl.Message(content=user_text, author="You").send()

        # Reuse logic for LLM and TTS
        session_models = cl.user_session.get("available_models")
        current_models = session_models if session_models else available_models
        selected_model = cl.user_session.get("selected_model") or current_models[0]
        system_prompt = cl.user_session.get("system_prompt", prompt_catalog["AI"])
        reasoning_enabled = cl.user_session.get("reasoning_enabled", False)
        if reasoning_enabled:
            system_prompt += " Think step by step before responding."
        llm_temp = cl.user_session.get("llm_temp", default_llm_temp)
        max_tokens = cl.user_session.get("max_tokens", default_max_tokens)

        # 2. LLM Inference
        response = await client.chat.completions.create(
            model=selected_model,
            messages=[
                {"content": system_prompt, "role": "system"},
                {"content": user_text, "role": "user"}
            ],
            temperature=llm_temp,
            max_tokens=max_tokens,
        )
        full_response = response.choices[0].message.content

        # --- Sentiment Analysis Integration ---
        # Process the full response for sentiment analysis and debugging.
        # The process_message_for_tts function will handle chunking, scrubbing,
        # sentiment classification, and printing debug statements.
        # For now, we are not directly using the sentiment to influence TTS,
        # but the debug statements will be printed.
        # Future work could involve using processed_message_data to influence TTS.
        processed_message_data = process_message_for_tts(full_response)
        # --- End Sentiment Analysis Integration ---

        character = cl.user_session.get("character", list(prompt_catalog.keys())[0])
        text_msg = await cl.Message(content=f"[{character}]: {full_response}").send()

        # 3. Text-to-Speech
        selected_voice = cl.user_session.get("selected_voice", default_tts_voice)
        tts_speed = cl.user_session.get("tts_speed", default_tts_speed)
        tts_exaggeration = cl.user_session.get("tts_exaggeration", default_tts_exaggeration)

        params_dict = {
            "exaggeration": tts_exaggeration,
            "cfg_weight": config["tts_cfg_weight"],
            "temperature": config["tts_temperature"],
            "device": config["tts_device"],
            "dtype": config["tts_dtype"],
            "seed": config["tts_seed"],
            "chunked": config["tts_chunked"],
            "use_compilation": config["tts_use_compilation"],
            "max_new_tokens": config["tts_max_new_tokens"],
            "max_cache_len": config["tts_max_cache_len"],
            "desired_length": config["tts_desired_length"],
            "max_length": config["tts_max_length"],
            "halve_first_chunk": True,
            "cpu_offload": False,
            "cache_voice": False,
            "tokens_per_slice": None,
            "remove_milliseconds": None,
            "remove_milliseconds_start": None,
            "chunk_overlap_method": "undefined"
        }

        buffer = b""
        async with tts_client.audio.speech.with_streaming_response.create(
            model=default_tts_model,
            input=full_response,
            voice=selected_voice,
            response_format=default_tts_response_format,
            speed=tts_speed,
            extra_body={"params": params_dict}
        ) as response:
            async for chunk in response.iter_bytes():
                buffer += chunk

        tts_audio = cl.Audio(
            name="response_audio.wav",
            content=buffer,
            mime="audio/wav",
            auto_play=True
        )
        await tts_audio.send(for_id=text_msg.id)

    except Exception as e:
        logger.error(f"AUDIO DIAG: STT or processing error: {str(e)}")
        await cl.Message(content=f"Error processing audio: {str(e)}").send()
    return True