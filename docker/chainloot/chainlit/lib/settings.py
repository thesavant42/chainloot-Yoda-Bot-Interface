# lib/settings.py

import chainlit as cl
import logging
import json
import os
from chainlit.input_widget import Select, Slider, Switch
from lib.config_handler import (
    config,
    available_models,
    available_voices,
    fetch_available_models,
)
from lib.bot_config import get_profile_defaults

logger = logging.getLogger(__name__)
config_path = "config/config.json"


@cl.on_settings_update
async def on_settings_update(settings):
    """Handle settings updates from Chainlit UI"""
    # Update the user session with the new settings
    cl.user_session.set("selected_model", settings["model"])
    cl.user_session.set("selected_voice", settings["voice"])
    cl.user_session.set("llm_temp", settings["llm_temp"])
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
            current_config["temperature"] = settings["llm_temp"]
        if "tts_speed" in settings:
            current_config["tts_speed"] = settings["tts_speed"]
        if "tts_exaggeration" in settings:
            current_config["tts_exaggeration"] = settings["tts_exaggeration"]
        if "tts_temperature" in settings: # Persist TTS Temperature
            current_config["tts_temperature"] = settings["tts_temperature"]
        if "reasoning_enabled" in settings: # Persist Reasoning Enabled
            current_config["reasoning_enabled"] = settings["reasoning_enabled"]
        if "provider" in settings: # Persist provider selection
            current_config["provider"] = settings["provider"]
        # Note: provider model updates are handled separately below

        # Write the updated config back to the file
        with open(config_path, 'w') as f:
            json.dump(current_config, f, indent=4)

        # Update the global config dict
        config.update(current_config)

    except Exception as e:
        logger.error(f"Failed to persist settings to {config_path}: {e}")

    # If voice was changed, refresh the settings UI to show the new selection
    if "voice" in settings:
        await send_updated_settings_ui(cl.user_session.get("available_models", available_models))

    # Handle refresh models toggle switch
    if "refresh_models" in settings and settings["refresh_models"]:
        try:
            current_provider = config.get("provider", "docker-model-runner")
            updated_models = fetch_available_models(current_provider)
            cl.user_session.set("available_models", updated_models)
            
            # Update selected model if it was removed
            selected_model = cl.user_session.get("selected_model")
            if selected_model not in updated_models and updated_models:
                new_selected = updated_models[0]
                cl.user_session.set("selected_model", new_selected)
                await cl.Message(content=f"Models refreshed. Switched to {new_selected}.").send()
            else:
                await cl.Message(content="Models refreshed successfully.").send()
                
            # Refresh the settings UI with updated models (this will auto-reset the switch to False)
            await send_updated_settings_ui(updated_models)
        except Exception as e:
            await cl.Message(content=f"Failed to refresh: {str(e)}").send()

    # Handle provider change - refresh models and update UI
    if "provider" in settings:
        new_provider = settings["provider"]
        old_provider = config.get("provider", "docker-model-runner")
        try:
            updated_models = fetch_available_models(new_provider)
            cl.user_session.set("available_models", updated_models)

            if not updated_models:
                await cl.Message(content=f"Cannot switch to {new_provider}: No models available. Please ensure the provider service is running.").send()
                # Don't persist provider
                return

            # Persist the provider since models are available
            config["provider"] = new_provider
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=4)

            # Update selected model if it's not in the new list
            selected_model = cl.user_session.get("selected_model")
            if selected_model not in updated_models and updated_models:
                new_selected = updated_models[0]
                cl.user_session.set("selected_model", new_selected)
                # Also update the config so it persists across restarts
                config["last_used_model"] = new_selected
                with open(config_path, 'w') as f:
                    json.dump(config, f, indent=4)
                await cl.Message(content=f"Switched to {new_selected} (previous model not available in {new_provider})").send()
            else:
                await cl.Message(content="Settings updated!").send()

            # Send updated settings UI with new model list
            await send_updated_settings_ui(updated_models)
        except Exception as e:
            await cl.Message(content=f"Failed to switch provider: {str(e)}").send()

async def send_updated_settings_ui(updated_models):
    """Send updated settings UI with new model list"""
    # Handle empty model list gracefully
    if not updated_models:
        await cl.Message(content="Warning: No models available for the selected provider. Please check that the provider service is running.").send()
        # Still send UI but with placeholder
        model_values = ["No models available"]
        model_index = 0
    else:
        model_values = updated_models
        selected_model = cl.user_session.get("selected_model")
        model_index = updated_models.index(selected_model) if selected_model in updated_models else 0
    
    chat_profile_name = cl.user_session.get("chat_profile")
    PROFILE_DEFAULTS = get_profile_defaults()
    defaults = PROFILE_DEFAULTS[chat_profile_name]
    default_voice = defaults["default_voice"]
    selected_voice = default_voice
    if "profile_voices" in config:
        pv = config["profile_voices"]
        if chat_profile_name in pv:
            selected_voice = pv[chat_profile_name]

    voice_index = available_voices.index(selected_voice) if selected_voice in available_voices else 0

    llm_temp = config.get("temperature", 0.8)
   # max_tokens = config["max_tokens"]
    tts_speed = config["tts_speed"]
    tts_exaggeration = config["tts_exaggeration"]
    tts_temperature = config["tts_temperature"]
    reasoning_enabled = config["reasoning_enabled"]
    provider = config.get("provider", "docker-model-runner")

    settings_widgets = [
        Select(id="provider", label="LLM Provider", values=["docker-model-runner", "ollama"], initial_index=0 if provider == "docker-model-runner" else 1),
        Select(id="model", label="LLM Model", values=model_values, initial_index=model_index),
        Slider(id="llm_temp", label="LLM Temperature", initial=llm_temp, min=0.0, max=2.0, step=0.1),
        Select(id="voice", label="TTS Voice", values=available_voices if available_voices else ["No TTS Available"], initial_index=voice_index if available_voices else 0),
        Slider(id="tts_speed", label="TTS Speed", initial=tts_speed, min=0.25, max=4.0, step=0.05),
        Slider(id="tts_exaggeration", label="TTS Exaggeration", initial=tts_exaggeration, min=0.0, max=1.0, step=0.1),
        Slider(id="tts_temperature", label="TTS Temperature", initial=tts_temperature, min=0.0, max=2.0, step=0.1),
        Switch(id="reasoning_enabled", label="Enable Reasoning", initial=reasoning_enabled),
        Switch(id="refresh_models", label="Refresh Models", initial=False, description="Toggle to refresh available models"),
    ]
    
    await cl.ChatSettings(settings_widgets).send()
