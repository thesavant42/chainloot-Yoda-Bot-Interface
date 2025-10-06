# app.py

import chainlit as cl
from chainlit.logger import logger
import time
from chainlit.input_widget import Select, Slider, Switch
import json # You'll need this for on_settings_update
from lib.stt import handle_audio_chunk, handle_audio_end
from lib.tts import generate_speech

from lib.config_handler import (
    config,
    client,
    tts_client,
    stt_client,
    prompt_catalog,
    available_models,
    available_voices,
    fetch_available_models,
    fetch_available_voices
)

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
    full_response = response.choices[0].message.content.strip()
    logger.info(f"LLM Response: {full_response}")

    # 3. Send text response to the UI
    character = cl.user_session.get("character")
    text_msg = await cl.Message(
        content=full_response,
        author=character
    )   .send()
       
    # 4. Generate and send audio response
    selected_voice = cl.user_session.get("selected_voice")
    tts_speed = cl.user_session.get("tts_speed")
    tts_exaggeration = cl.user_session.get("tts_exaggeration")
    
    # --- THIS IS THE CORRECTED, FULL DICTIONARY ---
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
        text=full_response,
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
    chat_profile = cl.user_session.get("chat_profile")
    await cl.Message(
        content=f"starting chat using the {chat_profile} chat profile"
    ).send()
    logger.info(f"AUDIO DIAG: Chat start - Session ID: {cl.context.session.id}, STT client base: {stt_client.base_url}")

    # Load initial settings from config.json
    selected_model = config.get("last_used_model")
    cl.user_session.set("selected_model", selected_model)

    selected_voice = config.get("tts_voice")
    cl.user_session.set("selected_voice", selected_voice)

    system_prompt_key = config.get("system_prompt_key") 
    cl.user_session.set("system_prompt", prompt_catalog[system_prompt_key])
    # derive character name from prompt settings
    cl.user_session.set("character", system_prompt_key)

    llm_temp = config.get("lm_studio_temperature")
    cl.user_session.set("llm_temp", llm_temp)

    max_tokens = config.get("max_tokens")
    cl.user_session.set("max_tokens", max_tokens)

    tts_speed = config.get("tts_speed")
    cl.user_session.set("tts_speed", tts_speed)

    tts_exaggeration = config.get("tts_exaggeration")
    cl.user_session.set("tts_exaggeration", tts_exaggeration)

    reasoning_enabled = config.get("reasoning_enabled")
    cl.user_session.set("reasoning_enabled", reasoning_enabled)

    # Find initial index for voice and model
    voice_index = available_voices.index(selected_voice) if selected_voice in available_voices else 0
    model_index = available_models.index(selected_model) if selected_model in available_models else 0
    system_prompt_index = list(prompt_catalog.keys()).index(system_prompt_key) if system_prompt_key in prompt_catalog else 0
    

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
                new_selected = updated_models if updated_models else available_models
                cl.user_session.set("selected_model", new_selected)
                notification += f" Switched to {new_selected}."

            await cl.Message(content=notification).send()
        except Exception as e:
            await cl.Message(content=f"Failed to refresh models: {str(e)}").send()
        # Note: User can select "No Action" to stop further refreshes

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