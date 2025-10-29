# lib/audio_handler.py

import chainlit as cl
import logging
from lib.stt import handle_audio_chunk, handle_audio_end
from lib.config_handler import config, stt_client

logger = logging.getLogger(__name__)


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
    # Import here to avoid circular imports
    from app import process_user_input_and_respond
    
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