# helm_streaming.py - Optimized streaming version with chunked processing
# This version processes audio in chunks to reduce latency

import io
import argparse
import threading
import queue
import time
import numpy as np
from openai import OpenAI
from pydub import AudioSegment
import sounddevice as sd
import soundfile as sf

api_key="sk-1234567890"
base_url="http://192.168.1.98:7778/v1"

# --- Argument Parsing ---
parser = argparse.ArgumentParser(description="Generate TTS audio with a streaming doubler effect.")
parser.add_argument('--input', type=str, default="What up, everybody, so glad you're here!")
parser.add_argument('--voice', type=str, default="stark")
parser.add_argument('--chunk-size', type=int, default=1024, help='Audio chunk size for processing')
args = parser.parse_args()

class StreamingDoubler:
    def __init__(self, sample_rate=22050, delay_ms=20, volume_reduction_db=4, chunk_size=1024):
        self.sample_rate = sample_rate
        self.delay_samples = int((delay_ms / 1000.0) * sample_rate)
        self.volume_reduction = 10 ** (-volume_reduction_db / 20)  # Convert dB to linear
        self.chunk_size = chunk_size
        
        # Circular buffer for delay line
        self.delay_buffer = np.zeros(self.delay_samples, dtype=np.float32)
        self.delay_index = 0
        
        # Queue for processed audio chunks
        self.audio_queue = queue.Queue(maxsize=50)  # Increased from 10 to 50
        self.finished = False
        
        # Timing tracking
        self.first_chunk_played = False
        self.playback_start_time = None
        
    def process_chunk(self, chunk):
        """Apply doubler effect to a chunk of audio samples"""
        chunk = chunk.astype(np.float32)
        output = np.zeros_like(chunk)
        
        for i, sample in enumerate(chunk):
            # Get delayed sample from circular buffer
            delayed_sample = self.delay_buffer[self.delay_index]
            
            # Mix original with delayed sample
            output[i] = sample + (delayed_sample * self.volume_reduction)
            
            # Store current sample in delay buffer
            self.delay_buffer[self.delay_index] = sample
            self.delay_index = (self.delay_index + 1) % self.delay_samples
            
        # Simple normalization to prevent clipping
        max_val = np.max(np.abs(output))
        if max_val > 0.8:
            output = output * (0.8 / max_val)
            
        return output
    
    def stream_audio_callback(self, outdata, frames, time, status):
        """Callback for sounddevice streaming playback"""
        if status:
            print(f"Audio callback status: {status}")
            
        try:
            # Get processed chunk from queue
            chunk = self.audio_queue.get_nowait()
            outdata[:len(chunk)] = chunk.reshape(-1, 1)
            
            # Track when first chunk is played
            if not self.first_chunk_played:
                self.first_chunk_played = True
                import time as time_module
                self.playback_start_time = time_module.time()
                print(f"PLAYBACK STARTED at {time_module.strftime('%H:%M:%S', time_module.localtime(self.playback_start_time))}")
                # Calculate total latency from launch to playback
                if hasattr(self, '_launch_time'):
                    total_latency = self.playback_start_time - self._launch_time
                    print(f"TOTAL LATENCY TO PLAYBACK: {total_latency:.3f} seconds")
            
            # Pad with silence if chunk is smaller than requested frames
            if len(chunk) < frames:
                outdata[len(chunk):] = 0
                
        except queue.Empty:
            # No audio available - fill with silence
            outdata[:] = 0
            if self.finished:
                print("🔇 Playback finished - no more audio")
                raise sd.CallbackStop()
            else:
                print("🔇 Audio queue empty - playing silence")

def process_streaming_audio():
    """Main function to process streaming audio with chunked doubler effect"""
    
    # Record launch time
    launch_time = time.time()
    print(f"SCRIPT LAUNCHED at {time.strftime('%H:%M:%S', time.localtime(launch_time))}")
    
    # --- OpenAI-Compatible API Configuration ---
    client = OpenAI(api_key=api_key, base_url=base_url)
    
    print(f"Generating streaming audio for: \"{args.input}\"")
    
    try:
        # Start streaming response
        with client.audio.speech.with_streaming_response.create(
            model="global_preset",
            voice=args.voice,
            input=args.input,
            response_format="wav"
        ) as response:
            
            # Read the entire audio stream first (OpenAI streaming doesn't support chunked reads)
            audio_bytes = response.read()
            print(f"Received {len(audio_bytes)} bytes of audio data")
            
            # Parse WAV header to get audio parameters
            if len(audio_bytes) < 44:
                raise ValueError("Invalid WAV file - too small")
                
            # WAV header parsing (little-endian)
            sample_rate = int.from_bytes(audio_bytes[24:28], byteorder='little')
            num_channels = int.from_bytes(audio_bytes[22:24], byteorder='little')
            bits_per_sample = int.from_bytes(audio_bytes[34:36], byteorder='little')
            
            print(f"Audio format: {sample_rate}Hz, {num_channels} channels, {bits_per_sample} bits")
            
            # Extract audio data (skip 44-byte WAV header)
            audio_data = audio_bytes[44:]
            
            # Initialize doubler effect processor
            doubler = StreamingDoubler(
                sample_rate=sample_rate, 
                chunk_size=args.chunk_size
            )
            doubler._launch_time = launch_time  # Store launch time for latency calculation
            
            # Start audio playback stream
            stream = sd.OutputStream(
                samplerate=sample_rate,
                channels=1,  # Always mono output
                callback=doubler.stream_audio_callback,
                blocksize=args.chunk_size
            )
            
            print("Starting streaming playback with doubler effect...")
            stream.start()
            
            # Process audio data in chunks
            chunk_count = 0
            first_chunk_queued = False
            first_chunk_time = None
            
            bytes_per_sample = bits_per_sample // 8
            chunk_bytes_size = args.chunk_size * bytes_per_sample * num_channels
            
            for i in range(0, len(audio_data), chunk_bytes_size):
                chunk_bytes = audio_data[i:i + chunk_bytes_size]
                if not chunk_bytes:
                    break
                
                # Check if we have enough bytes for complete samples
                bytes_per_sample = bits_per_sample // 8
                expected_samples = len(chunk_bytes) // (bytes_per_sample * num_channels)
                if expected_samples == 0:
                    continue
                    
                # Only process complete samples
                actual_bytes_needed = expected_samples * bytes_per_sample * num_channels
                chunk_bytes = chunk_bytes[:actual_bytes_needed]
                
                # Convert bytes to numpy array
                if bits_per_sample == 16:
                    samples = np.frombuffer(chunk_bytes, dtype=np.int16)
                elif bits_per_sample == 32:
                    samples = np.frombuffer(chunk_bytes, dtype=np.int32)
                else:
                    samples = np.frombuffer(chunk_bytes, dtype=np.int8)
                
                # Convert to mono if stereo
                if num_channels == 2:
                    samples = samples.reshape(-1, 2)
                    samples = np.mean(samples, axis=1).astype(samples.dtype)
                
                # Normalize to float32 [-1, 1]
                if samples.dtype == np.int16:
                    samples_float = samples.astype(np.float32) / 32768.0
                elif samples.dtype == np.int32:
                    samples_float = samples.astype(np.float32) / 2147483648.0
                else:
                    samples_float = samples.astype(np.float32) / 128.0
                
                # Apply doubler effect
                processed_chunk = doubler.process_chunk(samples_float)
                
                # Add to playback queue
                try:
                    doubler.audio_queue.put(processed_chunk, timeout=0.1)
                    chunk_count += 1
                    
                    # Track first chunk timing
                    if not first_chunk_queued:
                        first_chunk_queued = True
                        first_chunk_time = time.time()
                        elapsed_to_first_chunk = first_chunk_time - launch_time
                        print(f"📦 FIRST CHUNK QUEUED at {time.strftime('%H:%M:%S', time.localtime(first_chunk_time))}")
                        print(f"⏱️  TIME TO FIRST CHUNK: {elapsed_to_first_chunk:.3f} seconds")
                    
                    if chunk_count % 5 == 0:
                        print(f"Processed {chunk_count} chunks...")
                except queue.Full:
                    print(f"⚠️  Audio queue full - skipping chunk {chunk_count}")
                    continue
            # Wait for playback to finish
            print("Waiting for playback to complete...")
            doubler.finished = True
            
            # Give time for queue to empty
            while not doubler.audio_queue.empty():
                threading.Event().wait(0.1)
                
            stream.stop()
            stream.close()
            
    except Exception as e:
        print(f"Error during streaming processing: {e}")
        import traceback
        traceback.print_exc()
        return

if __name__ == "__main__":
    process_streaming_audio()
    print("Streaming playback finished.")