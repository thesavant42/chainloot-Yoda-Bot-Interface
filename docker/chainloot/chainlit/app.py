# app.py

# Critical! Apply S3 client fix before ANY other imports
from lib.custom_s3_storage import FixedS3StorageClient

# More aggressive monkey patching approach
import sys
# Clear any cached modules related to chainlit storage
modules_to_clear = [k for k in sys.modules.keys() if 'chainlit.data.storage' in k]
for module in modules_to_clear:
    del sys.modules[module]
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
patch_success = patch_s3_storage()
if not patch_success:
    print("Patch failed, but continuing...")

import chainlit as cl
import logging
logger = logging.getLogger(__name__)
import asyncio
import os
from lib.mqtt_publisher import get_mqtt_publisher
import lib.audio_handler
import lib.bot_config
import lib.settings
import lib.auth
from lib.chat import ChatProcessor, process_user_input_and_respond, initialize_chat_session, handle_chat_end, validate_session_model
from dotenv import load_dotenv
from lib.container_monitor import get_container_monitor
from chainlit.config import (FeaturesSettings, UISettings)
import atexit
import signal
import anybadge
import paho.mqtt.client as mqtt
import threading

config_path = "config/config.json"

### Main Chat Logic Here ###
# Chat processing logic moved to lib/chat.py

@cl.on_stop
def on_stop():
    print("The user stopped the task!")

@cl.on_chat_start
async def on_chat_start():
    """Initialize chat session - delegates to lib/chat.py"""
    await initialize_chat_session()

@cl.on_chat_end
async def on_chat_end():
    """Handle chat session end - delegates to lib/chat.py"""
    await handle_chat_end()

@cl.on_message
async def on_message(message: cl.Message):
    """Handles text messages by calling the core logic function."""
    if message.content:
        author_name = message.author
        print(f"Received a message from User: {author_name}")
        if not validate_session_model():
            await cl.Message(content="No valid model available. Please check your provider settings and ensure models are loaded.").send()
            return        
        await process_user_input_and_respond(message.content)

async def cleanup_on_exit():
    """Clean up MQTT on app shutdown"""
    try:
        mqtt_pub = get_mqtt_publisher()
        mqtt_pub.disconnect()
        logger.info("MQTT disconnected successfully")
    except Exception as e:
        logger.error(f"Error disconnecting MQTT: {e}")

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
