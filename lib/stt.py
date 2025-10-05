# STT (Speech-to-Text) related functions

from io import BytesIO
from openai import OpenAI
import cl
from chainlit.logger import logger
import wave
import sys

# Placeholder for configuration loading - this will be handled by app.py or a shared config module
# For now, we'll assume these are passed in or globally available.
# In a real scenario, you'd want to manage configuration more robustly.

# --- Helper Functions ---

def raw_pcm_to_wav(pcm_bytes: bytes, sample_rate: int = 16000, channels: int = 1, sample_width: int = 2) -> bytes:
    """
    Convert raw PCM bytes to WAV bytes.

    Args:
        pcm_bytes: The raw PCM audio data as bytes.
        sample_rate: The sample rate of the audio. Defaults to 16000.
        channels: The number of audio channels. Defaults to 1.
        sample_width: The sample width in bytes (e.g., 2 for 16-bit audio). Defaults to 2.

    Returns:
        The WAV audio data as bytes.
    """
    wav_buffer = BytesIO()
    with wave.open(wav_buffer, 'wb') as wav_file:
        wav_file.setnchannels(channels)
        wav_file.setsampwidth(sample_width)  # 2 bytes for 16-bit
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(pcm_bytes)
    return wav_buffer.getvalue()

# --- STT Core Functionality ---

def transcribe_audio(stt_client: OpenAI, audio_bytes: bytes, model: str = "openai/whisper-small.en", sample_rate: int = 24000) -> str:
    """
    Transcribes audio bytes to text using the provided STT client.

    Args:
        stt_client: An initialized OpenAI client configured for STT.
        audio_bytes: The raw audio data as bytes (expected to be PCM).
        model: The STT model to use (e.g., "openai/whisper-small.en").
        sample_rate: The sample rate of the audio in Hz.

    Returns:
        The transcribed text.

    Raises:
        Exception: If transcription fails.
    """
    logger.info(f"STT: Calling transcription API - Model: {model}, Bytes: {len(audio_bytes)}")
    
    try:
        # Convert raw PCM to WAV for STT
        wav_bytes: bytes = raw_pcm_to_wav(audio_bytes, sample_rate=sample_rate)
        logger.info(f"STT: Converted {len(audio_bytes)} PCM bytes to {len(wav_bytes)} WAV bytes")
        
        transcription = stt_client.audio.transcriptions.create(
            model=model,
            file=("recorded_audio.wav", BytesIO(wav_bytes)),
        )
        user_text: str = transcription.text.strip()
        logger.info(f"STT: Transcription successful - Text length: {len(user_text)}, Text: '{user_text[:50]}...'")
        return user_text
    except Exception as e:
        logger.error(f"STT: Transcription failed: {str(e)}")
        raise Exception(f"STT transcription failed: {str(e)}")

# --- Event Handlers (to be called from app.py) ---

async def handle_audio_chunk(chunk: cl.AudioChunk, audio_buffer: list[bytes] | None) -> list[bytes]:
    """
    Appends audio chunk data to the provided buffer.

    Args:
        chunk: The audio chunk received from the microphone.
        audio_buffer: The current list of audio byte chunks.

    Returns:
        The updated list of audio byte chunks.
    """
    if chunk.isStart:
        logger.info(f"STT: on_audio_chunk START - Initializing buffer.")
        return [] # Start a new buffer
    
    if audio_buffer is not None:
        audio_buffer.append(chunk.data)
    else:
        # This case should ideally not happen if chunk.isStart is handled correctly
        logger.warning("STT: Received audio chunk but audio_buffer was None. Initializing new buffer.")
        audio_buffer = [chunk.data]
        
    return audio_buffer

async def handle_audio_end(stt_client: OpenAI, audio_buffer: list[bytes] | None, stt_model: str) -> str:
    """
    Processes the recorded audio buffer, performs STT, and returns the transcription.

    Args:
        stt_client: An initialized OpenAI client configured for STT.
        audio_buffer: The list of audio byte chunks recorded.
        stt_model: The STT model to use for transcription.

    Returns:
        The transcribed text.

    Raises:
        Exception: If no audio data is found or transcription fails.
    """
    if not audio_buffer:
        logger.warning("STT: Empty audio buffer at end of recording.")
        raise Exception("No speech detected in audio.")
    
    # Combine all chunks into single audio bytes
    audio_bytes: bytes = b"".join(audio_buffer)
    logger.info(f"STT: Combined audio chunks - Total bytes: {len(audio_bytes)}")
    
    # Perform transcription
    user_text = transcribe_audio(stt_client=stt_client, audio_bytes=audio_bytes, model=stt_model)
    
    return user_text

# --- References to update ---
# - Calls to stt_client.audio.transcriptions.create
# - Calls to raw_pcm_to_wav
# - Usage of cl.AudioChunk and cl.Audio
# - Logic within on_audio_chunk and on_audio_end related to audio processing and transcription