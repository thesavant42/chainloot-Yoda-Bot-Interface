# app.py

import chainlit as cl
from chainlit.logger import logger
import time
from chainlit.input_widget import Select, Slider, Switch
import json # You'll need this for on_settings_update
from lib.stt import handle_audio_chunk, handle_audio_end
from lib.tts import generate_speech
from lib.text_utils import scrub_unsafe_characters
from lib.config_handler import (
    config,
    client,
    tts_client,
    stt_client,
    available_models,
    available_voices,
    fetch_available_models,
    fetch_available_voices
)
from chainlit.config import (
    ChainlitConfigOverrides,
    FeaturesSettings,
    McpFeature,
    UISettings,
)
config_path = "config.json"

# Canonical per-profile configuration (authoritative, no implicit fallbacks)
PROFILE_DEFAULTS = {
    "Yoda": {
        "system_prompt": "You are Yoda, wise Jedi Master. Reply in Yoda-speak. No more than 2 sentences per message.",
        "default_voice": "voices/chatterbox/yoda.wav",
    },
    "AI": {
        "system_prompt": "You are a 3-P-O, a helpful AI assistant. Your responses are concise and brief. No more than 2 sentences per message.",
        "default_voice": "voices/chatterbox/3po.wav",
    },
    "Stark": {
        "system_prompt": "You are a helpful but snarky AI assistant. Your name is Tony. No more than 2 sentences per message.",
        "default_voice": "voices/chatterbox/stark.wav",
    },
}

async def process_user_input_and_respond(user_text: str):
    """
    Handles the core logic: gets LLM response, sends text, and generates TTS audio.
    """
    # 1. Get settings from the user session
    selected_model = cl.user_session.get("selected_model")
    system_prompt = cl.user_session.get("system_prompt")
    llm_temp = cl.user_session.get("llm_temp")
    max_tokens = cl.user_session.get("max_tokens")
    reasoning_enabled = cl.user_session.get("reasoning_enabled", False)
    if reasoning_enabled:
        system_prompt += " Think step by step before responding."

    # 2. Get LLM response
    llm_start_time = time.time()
    response = await client.chat.completions.create(
        model=selected_model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_text}
        ],
        temperature=llm_temp,
        max_tokens=max_tokens,
    )
    llm_end_time = time.time()
    logger.info(f"PERF: LLM call took {llm_end_time - llm_start_time:.2f} seconds.")
    
    # Get the response content and scrub it for safety
    full_response = response.choices[0].message.content.strip()
    scrubbed_response = scrub_unsafe_characters(full_response)
    logger.info(f"LLM Response: {scrubbed_response}")


    # 3. Send text response to the UI
    character = cl.user_session.get("character")
    text_msg = await cl.Message(
        content=scrubbed_response, # Use the scrubbed response
        author=character
    )   .send()
       
    # 4. Generate and send audio response
    selected_voice = cl.user_session.get("selected_voice")
    tts_speed = cl.user_session.get("tts_speed")
    tts_exaggeration = cl.user_session.get("tts_exaggeration")
    

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

    tts_start_time = time.time()
    audio_buffer = await generate_speech(
        tts_client=tts_client,
        text=scrubbed_response, # Use the scrubbed response
        voice=selected_voice,
        tts_model=config.get("tts_model_name"),
        response_format=config.get("tts_response_format"),
        speed=tts_speed,
        exaggeration=tts_exaggeration,
        tts_config=tts_config_params
    )
    tts_end_time = time.time()
    logger.info(f"PERF: TTS call took {tts_end_time - tts_start_time:.2f} seconds.")

    await cl.Audio(
        name="response_audio.wav",
        content=audio_buffer,
        mime="audio/wav",
        auto_play=True
    ).send(for_id=text_msg.id)

### Main Chat Logic Here ###

@cl.set_chat_profiles
async def chat_profile():
    return [
        cl.ChatProfile(
            name="Yoda",
            markdown_description="An AI who thinks he is a Jedi Master",
            icon="/public/avatars/yoda.png",
        ),
        cl.ChatProfile(
            name="AI",
            markdown_description="Human <-> Cyborg Relations",
            icon="/public/avatars/ai.png",
        ),
        cl.ChatProfile(
            name="Stark",
            markdown_description="Billionaire genius playboy philanthropist.",
            icon="/public/avatars/stark.png",
        ),
    ]

@cl.on_chat_start
async def on_chat_start():
    chat_profile_name = cl.user_session.get("chat_profile")
    if not chat_profile_name:
        raise RuntimeError("chat_profile is not set. Select a profile before starting the chat.")

    # Look up canonical per-profile settings
    if chat_profile_name not in PROFILE_DEFAULTS:
        raise KeyError(f"No PROFILE_DEFAULTS entry for '{chat_profile_name}'")

    defaults = PROFILE_DEFAULTS[chat_profile_name]

    # Required: system_prompt, default_voice
    if not defaults.get("system_prompt"):
        raise KeyError(f"PROFILE_DEFAULTS['{chat_profile_name}']['system_prompt'] is missing or empty")
    if not defaults.get("default_voice"):
        raise KeyError(f"PROFILE_DEFAULTS['{chat_profile_name}']['default_voice'] is missing or empty")

    system_prompt = defaults["system_prompt"]
    default_voice = defaults["default_voice"]

    # Optional override via config['profile_voices'] — if present, it must contain this profile
    selected_voice = default_voice
    if "profile_voices" in config:
        pv = config["profile_voices"]
        if chat_profile_name not in pv:
            raise KeyError(
                f"config['profile_voices'] does not contain a voice for profile '{chat_profile_name}'. "
                "Either add it or remove 'profile_voices' from config."
            )
        selected_voice = pv[chat_profile_name]

    # Required model from config (no implicit defaults)
    if "last_used_model" not in config or not config["last_used_model"]:
        raise KeyError("config['last_used_model'] is missing or empty")
    selected_model = config["last_used_model"]

    # Validate the authoritative voice/model lists (must be populated in lib.config_handler)
    if not available_voices:
        raise RuntimeError("available_voices is empty. Ensure TTS voices are fetched before starting the chat.")
    if not available_models:
        raise RuntimeError("available_models is empty. Ensure models are fetched before starting the chat.")
    if selected_voice not in available_voices:
        raise ValueError(f"selected_voice '{selected_voice}' not found in available_voices: {available_voices}")
    if selected_model not in available_models:
        raise ValueError(f"selected_model '{selected_model}' not found in available_models: {available_models}")

    # Store validated session values
    cl.user_session.set("system_prompt", system_prompt)
    cl.user_session.set("character", chat_profile_name)
    cl.user_session.set("default_voice", default_voice)
    cl.user_session.set("selected_voice", selected_voice)
    cl.user_session.set("selected_model", selected_model)

    # Remaining settings pulled from config (these keys must exist)
    required_scalar_keys = ["lm_studio_temperature", "max_tokens", "tts_speed", "tts_exaggeration", "tts_temperature", "reasoning_enabled"]
    for k in required_scalar_keys:
        if k not in config:
            raise KeyError(f"Missing required config key: '{k}'")
    llm_temp = config["lm_studio_temperature"]
    max_tokens = config["max_tokens"]
    tts_speed = config["tts_speed"]
    tts_exaggeration = config["tts_exaggeration"]
    tts_temperature = config["tts_temperature"]
    reasoning_enabled = config["reasoning_enabled"]

    cl.user_session.set("llm_temp", llm_temp)
    cl.user_session.set("max_tokens", max_tokens)
    cl.user_session.set("tts_speed", tts_speed)
    cl.user_session.set("tts_exaggeration", tts_exaggeration)
    cl.user_session.set("reasoning_enabled", reasoning_enabled)

    await cl.Message(content=f"starting chat using the {chat_profile_name} chat profile").send()
    logger.info(
        f"AUDIO DIAG: Chat start - Session ID: {cl.context.session.id}, STT client base: {stt_client.base_url}"
    )

    # Compute indices AFTER values are validated and set
    voice_index = available_voices.index(selected_voice)
    model_index = available_models.index(selected_model)

    # Render the settings UI (only once)
    await cl.ChatSettings(
        [
            Select(id="voice", label="TTS Voice", values=available_voices, initial_index=voice_index),
            Select(id="model", label="LLM Model", values=available_models, initial_index=model_index),
            Select(id="model_refresh", label="Model Refresh", values=["No Action", "Refresh Now"], initial_index=0),
            Slider(id="llm_temp", label="LLM Temperature", initial=llm_temp, min=0.0, max=2.0, step=0.1),
            Slider(id="max_tokens", label="Max Tokens", initial=max_tokens, min=100, max=2000, step=50),
            Slider(id="tts_speed", label="TTS Speed", initial=tts_speed, min=0.25, max=4.0, step=0.05),
            Slider(id="tts_exaggeration", label="TTS Exaggeration", initial=tts_exaggeration, min=0.0, max=1.0, step=0.1),
            Slider(id="tts_temperature", label="TTS Temperature", initial=tts_temperature, min=0.0, max=2.0, step=0.1),
            Switch(id="reasoning_enabled", label="Enable Reasoning", initial=reasoning_enabled),
        ]
    ).send()

    await cl.Message(content=f"Model: {selected_model}  Voice: {selected_voice}").send()
    await cl.Message(content="Voice mode ready! Click the microphone icon, record your speech, and send – it will be transcribed automatically.").send()

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
                initial=config.get("tts_temperature"),
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
    # Update the user session with the new settings
    cl.user_session.set("selected_model", settings["model"])
    cl.user_session.set("selected_voice", settings["voice"])
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
            chat_profile_name = cl.user_session.get("chat_profile")
            if "profile_voices" not in current_config:
                current_config["profile_voices"] = {}
            current_config["profile_voices"][chat_profile_name] = settings["voice"]
        if "model" in settings:
            current_config["last_used_model"] = settings["model"]
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

# This message hook runs when the user sends a new message. We use it to 
# process user input, call an LLM, or return a response.

@cl.on_chat_end
async def on_chat_end():
    print("The user disconnected!")

@cl.on_message
async def on_message(message: cl.Message):
    """Handles text messages by calling the core logic function."""
    if message.content:
        author_name = message.author
        print(f"Received a message from: {author_name}")
        await process_user_input_and_respond(message.content)


@cl.on_audio_chunk
async def on_audio_chunk(chunk):
    """Handle audio chunks from microphone recording."""
    # Use the imported handle_audio_chunk function from lib.stt
    updated_buffer = await handle_audio_chunk(chunk, cl.user_session.get("audio_buffer"))
    cl.user_session.set("audio_buffer", updated_buffer)

@cl.on_audio_start
async def on_audio_start():
    logger.info(f"AUDIO DIAG: on_audio_start triggered - Session ID: {cl.context.session.id}")
    return True

@cl.on_audio_end
async def on_audio_end():
    """Transcribes audio, then calls the core logic function."""
    audio_buffer = cl.user_session.get("audio_buffer")
    try:
        # Perform STT
        user_text = await handle_audio_end(
            stt_client=stt_client, 
            audio_buffer=audio_buffer, 
            stt_model=config.get("whisper_model")
        )

        if not user_text:
            await cl.Message(content="No speech detected in audio.").send()
            return

        await cl.Message(content=user_text, author="You").send()

        # SLIMMED DOWN: Just one call here!
        await process_user_input_and_respond(user_text)

    except Exception as e:
        logger.error(f"AUDIO DIAG: Error in on_audio_end: {str(e)}")
        await cl.Message(content=f"Error processing audio: {str(e)}").send()