# Streaming Audio Feasability Research

## Status: Not implementing at this time.

Road map to streaming

## Does the code take advantage of audio streaming?

The code partially takes advantage of audio streaming as described in the Chainlit documentation, but only for the input side (STT). 

Here's the breakdown:

### Current Implementation

- STT (Speech-to-Text) Input Streaming: 
	- Yes, it properly leverages audio streaming. 
	- The on_audio_chunk handler receives audio chunks from the microphone in real-time, buffers them incrementally, and only processes the full buffer when recording ends (on_audio_end). 
	- This aligns with Chainlit's audio streaming for real-time input capture.

- TTS (Text-to-Speech) Output Streaming: 
	- No, it does not stream the audio output. 
		- The generate_speech function uses OpenAI's streaming response API to receive audio chunks as they're generated, but it buffers all chunks into a single byte buffer before sending the complete audio via cl.Audio. 
		- Playback only starts after the entire audio is generated and sent.


### Considerations for Enabling TTS Output Streaming

Streaming TTS output would allow audio playback to begin immediately as chunks are generated, reducing perceived latency (especially for long responses) and improving real-time feel. However, there are trade-offs:

- Pros: 
	- Lower latency, 
	- better user experience for lengthy audio, 
	- aligns with real-time communication goals.

- Cons: 
	- More complex implementation, 
	- potential for audio glitches if chunks arrive out of sync, 
	- increased server load, 
	- and Chainlit's cl.Audio element doesn't natively support progressive streaming 
		- (it's designed for complete audio blobs).

### Feasibility

- Chainlit's built-in audio components don't support streaming audio output directly. 
	- You'd need a custom solution, such as:
		- Using WebSockets or a custom audio player element to stream chunks progressively.
		- Modifying the UI to handle partial audio updates 
			- (e.g., appending to an audio buffer in the browser).
	- Ensuring the TTS API (OpenAI) supports true streaming without buffering on the client side.

Performance Impact: For short responses, buffering is often faster and simpler. Streaming shines for responses >10-15 seconds.

## Steps to Implement TTS Output Streaming

If you want to pursue this, here's a high-level plan (requires custom development beyond standard Chainlit):

- Modify generate_speech in tts.py:
	- Change the return type from bytes to an async generator that yields audio chunks as they arrive.
		- Instead of buffer += chunk, yield each chunk immediately.
- Update app.py in process_user_input_and_respond:
	- Send an initial cl.Audio message with auto_play=True and an empty or placeholder content.
		- As chunks are yielded from generate_speech, append them to the audio element (if Chainlit supports updating audio content) or use a custom streaming mechanism.
	- Alternatively, implement a WebSocket-based streamer to push chunks to the client for real-time playback.

### Client-Side Changes

- Use a custom Chainlit element or JavaScript to handle streaming audio (e.g., an HTML5 Audio element that appends blobs).
- Ensure the browser can play incomplete audio streams without gaps.

### Testing and Edge Cases:

- Test with varying response lengths, network conditions, and audio formats.
- Handle errors mid-stream (e.g., stop playback if generation fails).
- Monitor for audio artifacts from chunk boundaries.
- If buffering suffices for your use case, the current setup is solid and simpler to maintain. Let me know if you'd like help implementing streaming or have more details on your requirements!