# app.py

# CRITICAL: This must be the very first thing that happens
# Apply S3 client fix before ANY other imports
print("Applying S3StorageClient fix...")

# Import our custom storage client
from lib.custom_s3_storage import FixedS3StorageClient

# More aggressive monkey patching approach
import sys

# Clear any cached modules related to chainlit storage
modules_to_clear = [k for k in sys.modules.keys() if 'chainlit.data.storage' in k]
for module in modules_to_clear:
    del sys.modules[module]

# Patch the module at import time
def patch_s3_storage():
    """Apply the patch when the module is imported"""
    try:
        import chainlit.data.storage_clients.s3 as s3_module
        # Replace the class
        original_class = s3_module.S3StorageClient
        s3_module.S3StorageClient = FixedS3StorageClient
        print(f"Successfully patched S3StorageClient: {original_class} -> {FixedS3StorageClient}")
        return True
    except Exception as e:
        print(f"Failed to patch S3StorageClient: {e}")
        return False

# Apply the patch immediately
patch_success = patch_s3_storage()
if not patch_success:
    print("Patch failed, but continuing...")

print("S3StorageClient patch applied, proceeding with imports...")

import chainlit as cl
from mcp import ClientSession
from chainlit.logger import logger
import time
import asyncio
from chainlit.input_widget import Select, Slider, Switch
import json
import os
from lib.mqtt_publisher import get_mqtt_publisher
from lib.stt import handle_audio_chunk, handle_audio_end
from lib.tts import generate_speech
from lib.text_utils import scrub_unsafe_characters
from lib.message_processor import process_message_for_tts
from typing import Dict, Any, List
from mcp import ClientSession
from mcp.types import CallToolResult, TextContent
from dotenv import load_dotenv
from lib.config_handler import (
    config,
    client,
    tts_client,
    stt_client,
    available_models,
    available_voices,
    fetch_available_models,
    fetch_available_voices,
    get_client,
)
from lib.mcp_server_manager import mcp_manager
from lib.dynamic_mcp_manager import dynamic_mcp_manager
from lib.mcp_tool_processor import tool_processor
from chainlit.config import (
    ChainlitConfigOverrides,
    FeaturesSettings,
    McpFeature,
    UISettings,
)
config_path = "config/config.json"
mcp_tools_cache = {}

def get_active_mcp_manager():
    """Get the active MCP manager (dynamic if config exists, otherwise legacy)"""
    if os.path.exists("config/mcp_servers.json"):
        return dynamic_mcp_manager
    else:
        return mcp_manager

# Pre-initialize MCP servers on app startup (before any browser connections)
async def initialize_mcp_on_startup():
    """Initialize MCP servers when the app starts, before users connect"""
    try:
        print("Pre-initializing MCP servers for optimal user experience...")
        
        # Check if dynamic configuration exists
        if os.path.exists("config/mcp_servers.json"):
            print("Using dynamic MCP configuration (config/mcp_servers.json)")
            await dynamic_mcp_manager.initialize()
            tool_count = len(dynamic_mcp_manager.get_available_tools())
            print(f"Dynamic MCP initialization complete! {tool_count} tools ready.")
        else:
            print("Using legacy MCP configuration (hardcoded)")
            await mcp_manager.initialize()
            tool_count = len(mcp_manager.get_available_tools())
            print(f"Legacy MCP initialization complete! {tool_count} tools ready.")
            
    except Exception as e:
        print(f"MCP pre-initialization failed: {e}")
        print("Users can still chat, but advanced tools may not be available.")

# Note: Removed background thread initialization to avoid event loop conflicts
# MCP will now initialize on first chat session instead

starters = [
    cl.Starter(
        label="Say hi",
        message="Start a conversation with a greeting",
        icon="https://picsum.photos/300",
    ),
    cl.Starter(
        label="Ask for help",
        message="Ask for help with something",
        icon="https://picsum.photos/350",
    ),
]

# Canonical per-profile configuration (authoritative, no implicit fallbacks)
PROFILE_DEFAULTS = {
    "Yoda": {
        "system_prompt": "You are Yoda, wise Jedi Master. Reply in Yoda-speak. No more than 2 sentences per message. You can access tools using MCP servers.",
        "default_voice": "voices/chatterbox/yoda.wav",
    },
    "AI": {
        "system_prompt": "You are a 3-P-O, a helpful AI assistant. Your responses are concise and brief.  You can access tools using MCP servers.",
        "default_voice": "voices/chatterbox/3po.wav",
    },
    "Stark": {
        "system_prompt": "You are a helpful but snarky AI assistant. Your name is Tony. No more than 2 sentences per message. You can access tools using MCP servers.",
        "default_voice": "voices/chatterbox/stark.wav",
    },
}

### Main Chat Logic Here ###

async def process_user_input_and_respond(user_text: str):
    """
    Handles the core logic: checks for MCP tools first, then gets LLM response, sends text, and generates TTS audio.
    """
    # 1. Check if the user input requires MCP tools
    tool_result = None
    active_manager = get_active_mcp_manager()
    
    if await tool_processor.should_use_tools(user_text):
        if active_manager.initialized:
            logger.info(f"MCP tool detected for input: {user_text}")
            tool_result = await tool_processor.process_with_tools(user_text)
            
            if tool_result:
                # Send the tool result directly
                character = cl.user_session.get("character")
                text_msg = await cl.Message(
                    content=tool_result,
                    author=character
                ).send()
                
                # Generate audio for the tool result
                await generate_audio_response(tool_result, text_msg.id)
                return  # Exit early, tool handled the request
        else:
            # MCP tools not ready yet, log and fall back to LLM silently
            logger.info(f"MCP tools requested but not ready yet, falling back to LLM for: {user_text}")

    # 2. Get settings from the user session for LLM processing
    selected_model = cl.user_session.get("selected_model")
    system_prompt = cl.user_session.get("system_prompt")
    llm_temp = cl.user_session.get("llm_temp")
    max_tokens = cl.user_session.get("max_tokens")
    reasoning_enabled = cl.user_session.get("reasoning_enabled", False)
    if reasoning_enabled:
        system_prompt += " Think step by step before responding."

    # 3. Get LLM response
    llm_start_time = time.time()
    
    # Prepare common parameters
    request_params = {
        "model": selected_model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_text}
        ],
        "temperature": llm_temp,
        "max_tokens": max_tokens,
    }
    
    # Add context length for Ollama if configured
    provider = config.get("provider", "lm-studio")
    if provider == "ollama":
        ollama_context_length = os.getenv("OLLAMA_CONTEXT_LENGTH")
        if ollama_context_length:
            try:
                context_length = int(ollama_context_length)
                request_params["extra_body"] = {"num_ctx": context_length}
                logger.info(f"Using Ollama context length: {context_length}")
            except ValueError:
                logger.warning(f"Invalid OLLAMA_CONTEXT_LENGTH value: {ollama_context_length}, ignoring")
    
    try:
        response = await get_client().chat.completions.create(**request_params)
        llm_end_time = time.time()
        logger.info(f"PERF: LLM call took {llm_end_time - llm_start_time:.2f} seconds.")
        
        # Validate response structure
        if not response or not hasattr(response, 'choices') or not response.choices:
            raise ValueError("Invalid response structure from LLM API")
        
        if not response.choices[0].message or not response.choices[0].message.content:
            raise ValueError("Empty response content from LLM API")
        
        # Get the response content and scrub it for safety
        full_response = response.choices[0].message.content.strip()
        
    except Exception as e:
        error_msg = f"Failed to get LLM response: {str(e)}"
        logger.error(error_msg)
        await cl.Message(content=f"Sorry, I encountered an error while processing your request: {str(e)}").send()
        return
    persona = cl.user_session.get("chat_profile")
    results = await process_message_for_tts(full_response, persona)
    # Run message through processing pipeline
    
    for r in results:
        logger.info(f"Sentiment: {r['sentiment']} | Text: {r['processed_chunk']}")
    scrubbed_response = " ".join([r["processed_chunk"] for r in results])

    # 4. Send text response to the UI
    character = cl.user_session.get("character")
    text_msg = await cl.Message(
        content=scrubbed_response,
        author=character
    ).send()
       
    # 5. Generate and send audio response
    await generate_audio_response(scrubbed_response, text_msg.id)

async def generate_audio_response(text: str, message_id: str):
    """
    Generate and send TTS audio for a given text.
    Extracted into separate function for reuse.
    """
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

    await cl.Audio(
        name="response_audio.wav",
        content=audio_buffer,
        mime="audio/wav",
        auto_play=True
    ).send(for_id=message_id)

### Auth HANDLING ###

@cl.password_auth_callback
def auth_callback(username: str, password: str):
    # Simple authentication - check against environment variables
    expected_username = os.getenv("CHAINLIT_USERNAME")
    expected_password = os.getenv("CHAINLIT_PASSWORD")
    
    if username == expected_username and password == expected_password:
        return cl.User(identifier=username, metadata={"role": "admin"})
    else:
        return None

### Settings Persistence ###

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

### User Stops Task ###
@cl.on_stop
def on_stop():
    print("The user stopped the task!")

### Chat Profile Functions ###

@cl.set_chat_profiles
async def chat_profile():
    return [
        cl.ChatProfile(
            name="Yoda",
            markdown_description="An AI who thinks he is a Jedi Master",
            starters=starters,
            icon="/public/avatars/yoda.png",
            
        ),
        cl.ChatProfile(
            name="AI",
            markdown_description="Human <-> Cyborg Relations",
            starters=starters,
            icon="/public/avatars/ai.png",
        ),
        cl.ChatProfile(
            name="Stark",
            markdown_description="Billionaire genius playboy philanthropist.",
            starters=starters,
            icon="/public/avatars/stark.png",
        ),
    ]

@cl.on_chat_start
async def on_chat_start():
    print("A new chat session has started!")
    
    # Initialize MCP in the main event loop to avoid "Event loop is closed" errors
    active_manager = get_active_mcp_manager()
    if not active_manager.initialized:
        try:
            print("Initializing MCP servers in main event loop...")
            await initialize_mcp_on_startup()
        except Exception as e:
            logger.error(f"Failed to initialize MCP servers: {e}")
    
    # Log MCP initialization status to console only
    if active_manager.initialized:
        tool_count = len(active_manager.get_available_tools())
        manager_type = "Dynamic" if active_manager == dynamic_mcp_manager else "Legacy"
        logger.info(f"{manager_type} MCP servers ready - {tool_count} tools available")
    else:
        logger.info("MCP servers not yet initialized - basic chat ready")
    
    
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

    # Ensure selected model is valid, but don't crash - correct it
    if selected_model not in available_models and available_models:
        selected_model = available_models[0]
        config["last_used_model"] = selected_model
        with open('config/config.json', 'w') as f:
            json.dump(config, f, indent=4)
        logger.info(f"Auto-corrected invalid model selection to: {selected_model}")
    elif not available_models:
        logger.warning("No models available from current provider - chat may not work until models are available")
        # Don't crash, let the user see the settings and fix it

    # Validate the authoritative voice/model lists (must be populated in lib.config_handler)
    # Skip voice validation if TTS is not available (for testing without TTS-WebUI)
    tts_available = bool(available_voices)
    if not available_models:
        logger.warning("No models available from current provider - settings will still work but chat may fail")
        # Don't crash - let user configure and see the issue
    
    if tts_available and selected_voice not in available_voices:
        logger.warning(f"Selected voice '{selected_voice}' not found in available voices - using first available")
        selected_voice = available_voices[0] if available_voices else selected_voice
    
    # selected_model is already corrected above, so no need to validate

    # Store validated session values
    cl.user_session.set("system_prompt", system_prompt)
    cl.user_session.set("character", chat_profile_name)
    cl.user_session.set("default_voice", default_voice)
    cl.user_session.set("selected_voice", selected_voice)
    cl.user_session.set("selected_model", selected_model)
    cl.user_session.set("available_models", available_models)
    cl.user_session.set("ollama_context_length", int(os.getenv("OLLAMA_CONTEXT_LENGTH", "4096")))

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

    logger.info(
        f"AUDIO DIAG: Chat start - Session ID: {cl.context.session.id}, STT client base: {stt_client.base_url}"
    )

    # Compute indices AFTER values are validated and set
    model_index = available_models.index(selected_model) if selected_model in available_models else 0
    voice_index = available_voices.index(selected_voice) if tts_available else 0

    # Render the settings UI (only once)
    provider = config.get("provider", "lm-studio")
    model_values = available_models if available_models else ["No models available"]
    model_index = 0  # Default to first item
    if available_models and selected_model in available_models:
        model_index = available_models.index(selected_model)
    
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
    if tts_available:
        settings_widgets.insert(1, Select(id="voice", label="TTS Voice", values=available_voices, initial_index=voice_index))
        settings_widgets.extend([
            Slider(id="tts_speed", label="TTS Speed", initial=tts_speed, min=0.25, max=4.0, step=0.05),
            Slider(id="tts_exaggeration", label="TTS Exaggeration", initial=tts_exaggeration, min=0.0, max=1.0, step=0.1),
            Slider(id="tts_temperature", label="TTS Temperature", initial=tts_temperature, min=0.0, max=2.0, step=0.1),
        ])
    
    await cl.ChatSettings(settings_widgets).send()

    # Warn user if no models available
    if not available_models:
        await cl.Message(content="Warning: The current LLM provider is not accessible or has no models available. Please switch to a different provider using the settings above.").send()

    # Publish online status to MQTT
    mqtt_publisher = get_mqtt_publisher()
    mqtt_publisher.publish_status(chat_profile_name.lower(), "online")

@cl.on_chat_end
async def on_chat_end():
    print("The user disconnected!")
    
    # Clean up MCP resources if this is the last session
    try:
        # Note: We don't close MCP sessions on each chat end since they're shared server-side
        # MCP sessions will be cleaned up when the server shuts down
        logger.info("Chat session ended")
    except Exception as e:
        logger.error(f"Error during chat end cleanup: {e}")

@cl.on_message
async def on_message(message: cl.Message):
    """Handles text messages by calling the core logic function."""
    if message.content:
        author_name = message.author
        print(f"Received a message from User: {author_name}")
        
        # Validate we have a working model before attempting chat
        selected_model = cl.user_session.get("selected_model")
        current_available = cl.user_session.get("available_models", available_models)
        if not current_available or selected_model not in current_available:
            await cl.Message(content="No valid model available. Please check your provider settings and ensure models are loaded.").send()
            return
        
        await process_user_input_and_respond(message.content)

### Audio Handling ###

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

        await process_user_input_and_respond(user_text)

    except Exception as e:
        logger.error(f"AUDIO DIAG: Error in on_audio_end: {str(e)}")
        await cl.Message(content=f"Error processing audio: {str(e)}").send()

# Add cleanup on app shutdown
import atexit
import signal

async def cleanup_on_exit():
    """Clean up MCP resources on app shutdown"""
    try:
        active_manager = get_active_mcp_manager()
        await active_manager.cleanup()
        logger.info("MCP resources cleaned up successfully")
    except Exception as e:
        logger.error(f"Error cleaning up MCP resources: {e}")

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(cleanup_on_exit())
    loop.close()

# Register cleanup handlers
atexit.register(lambda: asyncio.run(cleanup_on_exit()))
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)
