# DeepWiki Q&A with Code Context for Repository: Chainlit/chainlit


## Q1

Does chainlit's reactUI audio player component support streaming audio responses?


### Answer

Based on the codebase context, you're asking about whether Chainlit's React UI audio player component supports streaming audio responses.

## Answer

Yes, Chainlit's React UI audio player component **does support streaming audio responses**. chainlit:234-237 

The streaming audio functionality works through a WebSocket-based system where:

1. **Backend sends audio chunks**: The backend emits `audio_chunk` events containing PCM16 audio data chainlit:198-200 

2. **Frontend receives and plays chunks**: The React client listens for these chunks and adds them to a `WavStreamPlayer` for real-time playback chainlit:234-237 

3. **Visual feedback**: The `AudioPresence` component provides visual representation of the streaming audio chainlit:16-24 

The streaming implementation uses `WavStreamPlayer` and `WavRecorder` classes that were introduced in version 2.0.0 as part of a complete audio system revamp chainlit:586-591 . The system supports bidirectional streaming - both receiving audio from the server and sending audio to the server.

This is distinct from the `Audio` element component (`frontend/src/components/Elements/Audio.tsx`), which is a simpler component for playing pre-recorded audio files attached to messages, not streaming responses.

## Notes

The audio streaming feature must be enabled in the configuration (`features.audio.enabled = true`) chainlit:131-135  and requires implementing the `on_audio_start` and `on_audio_chunk` callbacks on the backend chainlit:330-341 .

Wiki pages you might want to explore:
- [Backend Architecture (Chainlit/chainlit)](/wiki/Chainlit/chainlit#2.1)


### Citations


**File:** libs/react-client/src/useChatSession.ts (L234-237)

```typescript
      socket.on('audio_chunk', (chunk: OutputAudioChunk) => {
        wavStreamPlayer.add16BitPCM(chunk.data, chunk.track);
        setIsAiSpeaking(true);
      });
```

**File:** backend/chainlit/emitter.py (L198-200)

```python
    async def send_audio_chunk(self, chunk: OutputAudioChunk):
        """Send an audio chunk to the UI."""
        await self.emit("audio_chunk", chunk)
```

**File:** frontend/src/components/AudioPresence.tsx (L16-24)

```typescript
export default function AudioPresence({
  type,
  height,
  width,
  barCount,
  barSpacing
}: Props) {
  const { variant } = useTheme();
  const { wavRecorder, wavStreamPlayer, isAiSpeaking } = useAudio();
```

**File:** CHANGELOG.md (L586-591)

```markdown
- Realtime audio streaming and processing (#1401, #1406, #1410):
  - New `AudioPresence` component for visual representation
  - Implemented `WavRecorder` and `WavStreamPlayer` classes
  - Introduced new `on_audio_start` callback
  - Added audio interruption functionality
  - New audio connection signaling with `on` and `off` states
```

**File:** backend/chainlit/config.py (L131-135)

```python
[features.audio]
    # Enable audio features
    enabled = false
    # Sample rate of the audio
    sample_rate = 24000
```

**File:** backend/chainlit/socket.py (L330-341)

```python
@sio.on("audio_start")  # pyright: ignore [reportOptionalCall]
async def audio_start(sid):
    """Handle audio init."""
    session = WebsocketSession.require(sid)

    context = init_ws_context(session)
    config: ChainlitConfig = session.get_config()

    if config.features.audio and config.features.audio.enabled:
        connected = bool(await config.code.on_audio_start())
        connection_state = "on" if connected else "off"
        await context.emitter.update_audio_connection(connection_state)
```

