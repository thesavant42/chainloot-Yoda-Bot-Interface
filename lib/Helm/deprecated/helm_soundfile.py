# helm_soundfile.py - Alternative using soundfile for more efficient WAV handling
import io
import argparse
import threading
import queue
import numpy as np
from openai import OpenAI
import sounddevice as sd
import soundfile as sf

def create_soundfile_streaming_version():
    """Alternative implementation using soundfile for direct WAV processing"""
    
    # This approach reads the WAV stream directly into soundfile
    # which can handle the format parsing more efficiently
    
    client = OpenAI(api_key="sk-1234567890", base_url="http://192.168.1.98:7778/v1")
    
    with client.audio.speech.with_streaming_response.create(
        model="global_preset",
        voice="stark",
        input="Test streaming",
        response_format="wav"
    ) as response:
        
        # Collect all bytes first (for soundfile compatibility)
        audio_data = response.read()
        
        # Use soundfile to parse WAV efficiently
        with sf.SoundFile(io.BytesIO(audio_data)) as f:
            sample_rate = f.samplerate
            channels = f.channels
            
            # Process in chunks using soundfile's built-in chunking
            chunk_size = 1024
            delay_samples = int(0.02 * sample_rate)  # 20ms delay
            delay_buffer = np.zeros(delay_samples)
            delay_idx = 0
            
            # Setup streaming playback
            audio_queue = queue.Queue(maxsize=5)
            
            def callback(outdata, frames, time, status):
                try:
                    chunk = audio_queue.get_nowait()
                    outdata[:len(chunk)] = chunk.reshape(-1, 1)
                    if len(chunk) < frames:
                        outdata[len(chunk):] = 0
                except queue.Empty:
                    outdata[:] = 0
            
            with sd.OutputStream(samplerate=sample_rate, channels=1, callback=callback):
                # Read and process chunks
                while True:
                    chunk = f.read(chunk_size)
                    if len(chunk) == 0:
                        break
                    
                    # Apply doubler effect
                    if channels == 1:
                        processed = apply_doubler_effect(chunk, delay_buffer, delay_idx)
                    else:
                        # Convert stereo to mono for processing
                        mono_chunk = np.mean(chunk, axis=1)
                        processed = apply_doubler_effect(mono_chunk, delay_buffer, delay_idx)
                    
                    audio_queue.put(processed)
                
                # Wait for playback completion
                threading.Event().wait(2)

def apply_doubler_effect(chunk, delay_buffer, delay_idx):
    """Optimized doubler effect using numpy operations"""
    chunk = chunk.astype(np.float32)
    output = np.zeros_like(chunk)
    
    for i, sample in enumerate(chunk):
        delayed_sample = delay_buffer[delay_idx]
        output[i] = sample + (delayed_sample * 0.63)  # -4dB ≈ 0.63
        
        delay_buffer[delay_idx] = sample
        delay_idx = (delay_idx + 1) % len(delay_buffer)
    
    # Normalize
    max_val = np.max(np.abs(output))
    if max_val > 0.8:
        output *= (0.8 / max_val)
    
    return output