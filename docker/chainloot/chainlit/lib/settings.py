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
    cl.user_session.set("max_tokens", int(settings["max_tokens"]))
    cl.user_session.set("tts_speed", settings["tts_speed"])
    cl.user_session.set("tts_exaggeration", settings["tts_exaggeration"])
    cl.user_session.set("reasoning_enabled", settings["reasoning_enabled"])
    
    # Handle Ollama context length
    if "ollama_context_length" in settings:
        cl.user_session.set("ollama_context_length", int(settings["ollama_context_length"]))
        # Update environment variable for current session
        os.environ["OLLAMA_CONTEXT_LENGTH"] = str(settings["ollama_context_length"])
        logger.info(f"Updated Ollama context length to: {settings['ollama_context_length']}")

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
        # Note: provider is handled separately below

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

    # Handle provider change - refresh models and update UI
    if "provider" in settings:
        new_provider = settings["provider"]
        old_provider = config.get("provider", "lm-studio")
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
                await cl.Message(content=f"Switched to {new_provider} provider").send()

            # Send updated settings UI with new model list
            await send_updated_settings_ui(updated_models)
        except Exception as e:
            await cl.Message(content=f"Failed to switch provider: {str(e)}").send()

    if settings["model_refresh"] == "Refresh Now":
        try:
            current_provider = config.get("provider", "lm-studio")
            updated_models = fetch_available_models(current_provider)
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

    llm_temp = config["lm_studio_temperature"]
    max_tokens = config["max_tokens"]
    tts_speed = config["tts_speed"]
    tts_exaggeration = config["tts_exaggeration"]
    tts_temperature = config["tts_temperature"]
    reasoning_enabled = config["reasoning_enabled"]
    provider = config.get("provider", "lm-studio")

    settings_widgets = [
        Select(id="provider", label="LLM Provider", values=["lm-studio", "ollama"], initial_index=0 if provider == "lm-studio" else 1),
        Select(id="model", label="LLM Model", values=model_values, initial_index=model_index),
        Select(id="model_refresh", label="Model Refresh", values=["No Action", "Refresh Now"], initial_index=0),
        Slider(id="llm_temp", label="LLM Temperature", initial=llm_temp, min=0.0, max=2.0, step=0.1),
        Slider(id="max_tokens", label="Max Tokens", initial=max_tokens, min=100, max=2000, step=50),
        Switch(id="reasoning_enabled", label="Enable Reasoning", initial=reasoning_enabled),
    ]
    
    # Add Ollama-specific settings
    if provider == "ollama":
        ollama_context = cl.user_session.get("ollama_context_length", 4096)
        settings_widgets.insert(3, Slider(id="ollama_context_length", label="Context Length", initial=ollama_context, min=1024, max=131072, step=1024))
    
    # Only add voice-related settings if TTS is available
    if available_voices:
        settings_widgets.insert(1, Select(id="voice", label="TTS Voice", values=available_voices, initial_index=voice_index))
        settings_widgets.extend([
            Slider(id="tts_speed", label="TTS Speed", initial=tts_speed, min=0.25, max=4.0, step=0.05),
            Slider(id="tts_exaggeration", label="TTS Exaggeration", initial=tts_exaggeration, min=0.0, max=1.0, step=0.1),
            Slider(id="tts_temperature", label="TTS Temperature", initial=tts_temperature, min=0.0, max=2.0, step=0.1),
        ])
    
    await cl.ChatSettings(settings_widgets).send()