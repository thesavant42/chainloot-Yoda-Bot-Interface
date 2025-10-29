# lib/chat.py
"""
Chat processing and session management for Chainlit application.
Handles core chat logic, session initialization, and user interaction processing.
"""

import chainlit as cl
import logging
import time
import json
import os
from typing import Dict, Any, List



from lib.config_handler import (
    config,
    available_models,
    available_voices,
    get_client,
)
from lib.bot_config import get_profile_defaults
from lib.tts_response import generate_audio_response
from lib.message_processor import process_message_for_tts
from lib.mqtt_publisher import get_mqtt_publisher
from lib.container_monitor import get_container_monitor
from lib.mcp_handler import get_all_mcp_tools, call_mcp_tool
from chainlit.input_widget import Select, Slider, Switch

logger = logging.getLogger(__name__)


class ChatProcessor:
    """Handles chat processing and session management for the Chainlit application."""
    
    @staticmethod
    async def process_user_input_and_respond(user_text: str):
        """
        Handles the core logic: gets LLM response, sends text, and generates TTS audio.
        """
        # 1. Get settings from the user session for LLM processing
        selected_model = cl.user_session.get("selected_model")
        system_prompt = cl.user_session.get("system_prompt")
        llm_temp = cl.user_session.get("llm_temp")
        max_tokens = cl.user_session.get("max_tokens")
        reasoning_enabled = cl.user_session.get("reasoning_enabled", False)
        if reasoning_enabled:
            system_prompt += " Think step by step before responding."

        # 2. Prepare LLM request parameters
        llm_start_time = time.time()
        
        request_params = {
            "model": selected_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_text}
            ],
            "temperature": llm_temp,
            "max_tokens": max_tokens,
        }
        
        # Add MCP tools if available (Chainlit handles the protocol)
        mcp_tools = get_all_mcp_tools()
        if mcp_tools:
            request_params["tools"] = mcp_tools
        
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
            # Call LLM with tools
            response = await get_client().chat.completions.create(**request_params)
            llm_end_time = time.time()
            logger.info(f"PERF: LLM call took {llm_end_time - llm_start_time:.2f} seconds.")
            
            # Validate response structure
            if not response or not hasattr(response, 'choices') or not response.choices:
                raise ValueError("Invalid response structure from LLM API")
            
            choice = response.choices[0]
            
            # Handle tool calls if present
            if choice.message.tool_calls:
                logger.info(f"LLM requested {len(choice.message.tool_calls)} tool calls")
                
                # Add the assistant message to conversation
                request_params["messages"].append(choice.message)
                
                # Process each tool call
                for tool_call in choice.message.tool_calls:
                    async with cl.Step(type="tool", name=tool_call.function.name) as step:
                        tool_name = tool_call.function.name
                        tool_input = json.loads(tool_call.function.arguments)
                        
                        # Execute tool via MCP
                        tool_result = await call_mcp_tool(tool_name, tool_input)
                        step.output = tool_result
                        
                        # Add tool result to conversation
                        request_params["messages"].append({
                            "role": "tool", 
                            "tool_call_id": tool_call.id,
                            "content": tool_result
                        })
                
                # Get final LLM response after tool calls
                final_response = await get_client().chat.completions.create(**request_params)
                if not final_response.choices[0].message.content:
                    raise ValueError("Empty final response after tool execution")
                full_response = final_response.choices[0].message.content.strip()
                
            else:
                # No tool calls, use direct response
                if not choice.message or not choice.message.content:
                    raise ValueError("Empty response content from LLM API")
                full_response = choice.message.content.strip()
            
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

    @staticmethod
    def validate_session_model():
        """Validate that we have a working model available for chat."""
        selected_model = cl.user_session.get("selected_model")
        current_available = cl.user_session.get("available_models", available_models)
        return bool(current_available and selected_model in current_available)

    @staticmethod
    async def initialize_chat_session():
        """Initialize chat session with profile defaults and settings."""
        print("A new chat session has started!")  
        
        # Start container monitoring for real-time MQTT publishing
        container_monitor = get_container_monitor()
        container_monitor.start_monitoring(interval=30)  # Publish every 30 seconds
        logger.info("Container monitoring started for real-time MQTT publishing")
        
        # Badge subscriber now runs independently in start.sh
        logger.info("Badge subscriber runs independently for event-driven badge generation")
        
        chat_profile_name = cl.user_session.get("chat_profile")
        if not chat_profile_name:
            raise RuntimeError("chat_profile is not set. Select a profile before starting the chat.")
        
        # Look up canonical per-profile settings
        PROFILE_DEFAULTS = get_profile_defaults()
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
        ChatProcessor._set_session_values(
            system_prompt, chat_profile_name, default_voice, selected_voice, 
            selected_model, tts_available
        )

        # Render the settings UI
        await ChatProcessor._render_settings_ui(tts_available)

        # Warn user if no models available
        if not available_models:
            await cl.Message(content="Warning: The current LLM provider is not accessible or has no models available. Please switch to a different provider using the settings above.").send()

        # Publish online status to MQTT
        mqtt_publisher = get_mqtt_publisher()
        mqtt_publisher.publish_status(chat_profile_name.lower(), "online", expiry_interval=60)

    @staticmethod
    def _set_session_values(system_prompt, chat_profile_name, default_voice, selected_voice, selected_model, tts_available):
        """Set all session values for the chat."""
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
        
        cl.user_session.set("llm_temp", config["lm_studio_temperature"])
        cl.user_session.set("max_tokens", config["max_tokens"])
        cl.user_session.set("tts_speed", config["tts_speed"])
        cl.user_session.set("tts_exaggeration", config["tts_exaggeration"])
        cl.user_session.set("reasoning_enabled", config["reasoning_enabled"])

        # Log audio diagnostic info
        from lib.config_handler import stt_client
        logger.info(f"AUDIO DIAG: Chat start - Session ID: {cl.context.session.id}, STT client base: {stt_client.base_url}")

    @staticmethod
    async def _render_settings_ui(tts_available):
        """Render the settings UI widgets."""
        provider = config.get("provider", "lm-studio")
        selected_model = cl.user_session.get("selected_model")
        selected_voice = cl.user_session.get("selected_voice")
        
        model_values = available_models if available_models else ["No models available"]
        model_index = 0  # Default to first item
        if available_models and selected_model in available_models:
            model_index = available_models.index(selected_model)
        
        voice_index = available_voices.index(selected_voice) if tts_available and selected_voice in available_voices else 0

        settings_widgets = [
            Select(id="provider", label="LLM Provider", values=["lm-studio", "ollama"], initial_index=0 if provider == "lm-studio" else 1),
            Select(id="model", label="LLM Model", values=model_values, initial_index=model_index),
            Select(id="model_refresh", label="Model Refresh", values=["No Action", "Refresh Now"], initial_index=0),
            Slider(id="llm_temp", label="LLM Temperature", initial=cl.user_session.get("llm_temp"), min=0.0, max=2.0, step=0.1),
            Slider(id="max_tokens", label="Max Tokens", initial=cl.user_session.get("max_tokens"), min=100, max=2000, step=50),
            Switch(id="reasoning_enabled", label="Enable Reasoning", initial=cl.user_session.get("reasoning_enabled")),
        ]
        
        # Add Ollama-specific settings
        if provider == "ollama":
            ollama_context = cl.user_session.get("ollama_context_length", 4096)
            settings_widgets.insert(3, Slider(id="ollama_context_length", label="Context Length", initial=ollama_context, min=1024, max=131072, step=1024))
        
        # Only add voice-related settings if TTS is available
        if tts_available:
            settings_widgets.insert(1, Select(id="voice", label="TTS Voice", values=available_voices, initial_index=voice_index))
            settings_widgets.extend([
                Slider(id="tts_speed", label="TTS Speed", initial=cl.user_session.get("tts_speed"), min=0.25, max=4.0, step=0.05),
                Slider(id="tts_exaggeration", label="TTS Exaggeration", initial=cl.user_session.get("tts_exaggeration"), min=0.0, max=1.0, step=0.1),
                Slider(id="tts_temperature", label="TTS Temperature", initial=config.get("tts_temperature", 0.7), min=0.0, max=2.0, step=0.1),
            ])
        
        await cl.ChatSettings(settings_widgets).send()

    @staticmethod
    async def handle_chat_end():
        """Handle chat session cleanup."""
        print("The user disconnected!")
        
        # Publish idle status and neutral emotion to MQTT
        chat_profile_name = cl.user_session.get("chat_profile")
        if chat_profile_name:
            mqtt_publisher = get_mqtt_publisher()
            mqtt_publisher.publish_status(chat_profile_name.lower(), "idle", expiry_interval=300)
            
            # Publish neutral emotion when going idle
            neutral_emotion = {
                "dominant_emotion": "neutral",
                "dominant_score": 1.0,
                "weights": {"neutral": 1.0}
            }
            mqtt_publisher.publish_emotion(chat_profile_name.lower(), neutral_emotion, expiry_interval=300)
            logger.info(f"Published idle status and neutral emotion for {chat_profile_name}")
        
        # Stop container monitoring
        container_monitor = get_container_monitor()
        container_monitor.stop_monitoring()
        logger.info("Container monitoring stopped")
        logger.info("Chat session ended")


# Convenience functions for backwards compatibility
async def process_user_input_and_respond(user_text: str):
    """Convenience wrapper for ChatProcessor.process_user_input_and_respond"""
    return await ChatProcessor.process_user_input_and_respond(user_text)

async def initialize_chat_session():
    """Convenience wrapper for ChatProcessor.initialize_chat_session"""
    return await ChatProcessor.initialize_chat_session()

async def handle_chat_end():
    """Convenience wrapper for ChatProcessor.handle_chat_end"""
    return await ChatProcessor.handle_chat_end()

def validate_session_model():
    """Convenience wrapper for ChatProcessor.validate_session_model"""
    return ChatProcessor.validate_session_model()
