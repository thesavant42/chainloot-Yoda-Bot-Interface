# helm_optimized.py - Optimized version with immediate playback and background processing
# This version starts playback immediately while processing effects in parallel

import io
import argparse
import time
import threading
import queue
from openai import OpenAI
from pydub import AudioSegment
import sounddevice as sd
import numpy as np
from collections import namedtuple

# Define AudioProperties for efficient property access
AudioProperties = namedtuple('AudioProperties', ['channels', 'sample_width', 'frame_rate'])

api_key="sk-1234567890"
base_url="http://192.168.1.98:7778/v1"

# --- Argument Parsing ---
parser = argparse.ArgumentParser(description="Generate TTS audio with optimized doubler effect.")
parser.add_argument('--input', type=str, default="What up, everybody, so glad you're here!")
parser.add_argument('--voice', type=str, default="stark")
args = parser.parse_args()

def apply_doubler_effect_pydub(audio_segment):
    """Apply the vintage doubler effect using pydub - preserves audio quality"""
    # Define the delay in milliseconds (20 ms creates a tight doubling effect)
    delay_ms = 20

    # Create a silent audio segment to act as a delay
    silence = AudioSegment.silent(duration=delay_ms)

    # Create the delayed track by prepending silence to the original
    delayed_audio = silence + audio_segment

    # Slightly reduce the volume of the delayed track to make the mix clearer
    delayed_audio = delayed_audio - 4

    # Overlay the delayed track onto the original track
    doubled_audio = audio_segment.overlay(delayed_audio)

    # Normalize the final audio to prevent digital clipping
    doubled_audio = doubled_audio.normalize()

    return doubled_audio

def prepare_audio_for_playback(audio_segment, audio_props=None):
    """Prepare AudioSegment for playback by converting to numpy array with optimized operations"""
    if audio_props is None:
        # Fallback to extracting properties from segment
        channels = audio_segment.channels
        sample_width = audio_segment.sample_width
    else:
        channels = audio_props.channels
        sample_width = audio_props.sample_width

    # Get raw samples - pydub already provides the correct format
    raw_samples = audio_segment.get_array_of_samples()

    # Convert to numpy array with appropriate dtype
    if sample_width == 2:
        # 16-bit samples
        samples = np.frombuffer(raw_samples, dtype=np.int16)
    else:
        # 32-bit samples (less common but supported)
        samples = np.frombuffer(raw_samples, dtype=np.int32)

    # Reshape for stereo if needed (vectorized operation)
    if channels == 2:
        samples = samples.reshape(-1, 2)

    return samples

def background_processing(original_audio, audio_props, result_queue):
    """Process audio in background thread"""
    try:
        print("Processing doubler effect in background...")

        # Apply the doubler effect
        doubled_audio = apply_doubler_effect_pydub(original_audio)

        # Convert to numpy array for playback
        samples = prepare_audio_for_playback(doubled_audio)

        # Put result in queue
        result_queue.put(('processed', samples, audio_props.frame_rate))
        print("Doubler effect processing complete")

    except Exception as e:
        result_queue.put(('error', str(e)))

def main():
    # Record launch time
    launch_time = time.time()
    print(f"SCRIPT LAUNCHED at {time.strftime('%H:%M:%S', time.localtime(launch_time))}")

    # --- OpenAI-Compatible API Configuration ---
    client = OpenAI(api_key=api_key, base_url=base_url)

    print(f"Generating audio for: \"{args.input}\"")
    try:
        with client.audio.speech.with_streaming_response.create(
            model="global_preset",
            voice=args.voice,
            input=args.input,
            response_format="wav"
        ) as response:
            # Read the entire audio stream into a bytes object
            audio_bytes = response.read()
            print(f"Received {len(audio_bytes)} bytes of audio data")

    except Exception as e:
        print(f"Error connecting to the API: {e}")
        return

    # Load audio to check duration and decide processing strategy
    original_audio = AudioSegment.from_file(io.BytesIO(audio_bytes), format="wav")
    audio_props = AudioProperties(
        channels=original_audio.channels,
        sample_width=original_audio.sample_width,
        frame_rate=original_audio.frame_rate
    )
    audio_duration_ms = len(original_audio)

    # For very short audio (< 2 seconds), process synchronously to avoid threading overhead
    if audio_duration_ms < 2000:
        print("Short audio detected - processing synchronously")
        # Apply doubler effect synchronously
        doubled_audio = apply_doubler_effect_pydub(original_audio)
        processed_samples = prepare_audio_for_playback(doubled_audio)

        # Start playback immediately
        playback_start_time = time.time()
        print(f"PROCESSED AUDIO PLAYBACK STARTED at {time.strftime('%H:%M:%S', time.localtime(playback_start_time))}")

        print("Playing modulated audio with doubler effect...")
        sd.play(processed_samples, audio_props.frame_rate, blocking=True)

        playback_end_time = time.time()
        total_latency = playback_end_time - launch_time
        print(f"TOTAL LATENCY TO AUDIO COMPLETE: {total_latency:.3f} seconds")
        print("Playback finished.")
        return

    # For longer audio, use background processing
    print("Longer audio detected - using background processing")
    result_queue = queue.Queue()
    processing_thread = threading.Thread(target=background_processing, args=(original_audio, audio_props, result_queue))
    processing_thread.daemon = True
    processing_thread.start()

    # Wait for processed audio to be ready
    print("Waiting for doubler effect processing to complete...")
    try:
        result = result_queue.get(timeout=5.0)  # Wait up to 5 seconds for processing
        if result[0] == 'processed':
            processed_samples, sample_rate = result[1], result[2]

            # Start playback of processed audio
            playback_start_time = time.time()
            print(f"PROCESSED AUDIO PLAYBACK STARTED at {time.strftime('%H:%M:%S', time.localtime(playback_start_time))}")

            print("Playing modulated audio with doubler effect...")
            sd.play(processed_samples, sample_rate, blocking=True)

            # Record when playback finishes
            playback_end_time = time.time()
            total_latency = playback_end_time - launch_time
            print(f"TOTAL LATENCY TO AUDIO COMPLETE: {total_latency:.3f} seconds")
            print("Playback finished.")

        elif result[0] == 'error':
            print(f"Processing failed: {result[1]}")
            # Fallback to original audio (already loaded)
            print("Falling back to original audio...")
            original_samples = prepare_audio_for_playback(original_audio, audio_props)

            playback_start_time = time.time()
            print(f"ORIGINAL AUDIO PLAYBACK STARTED at {time.strftime('%H:%M:%S', time.localtime(playback_start_time))}")

            sd.play(original_samples, audio_props.frame_rate, blocking=True)

            playback_end_time = time.time()
            total_latency = playback_end_time - launch_time
            print(f"TOTAL LATENCY TO AUDIO COMPLETE: {total_latency:.3f} seconds")

    except queue.Empty:
        print("Processing timeout - using original audio")
        # Fallback to original audio (already loaded)
        original_samples = prepare_audio_for_playback(original_audio, audio_props)

        playback_start_time = time.time()
        print(f"ORIGINAL AUDIO PLAYBACK STARTED at {time.strftime('%H:%M:%S', time.localtime(playback_start_time))}")

        sd.play(original_samples, audio_props.frame_rate, blocking=True)

        playback_end_time = time.time()
        total_latency = playback_end_time - launch_time
        print(f"TOTAL LATENCY TO AUDIO COMPLETE: {total_latency:.3f} seconds")

if __name__ == "__main__":
    main()