# Project: Websocket Streaming Audio

Audio is the most important component of this application, and latency is a user experience killer.
To improve this, I propose we implement streaming audio, both for text to speech and speech to text.

- Streaming audio is supported by Chainlit since 2.0.0 and we should implement it. 
- Streaming utilizes websockets
- The chainli react webui supports streaming audio

- I've begun some cursory research, detailed here: 
  - docs/streaming_audio_research.md
- Check out this proof of concept, Helm, which uses streaming audio + post processing effects to make voices in chainloot sound like Iron Man and C3PO robots:
  - lib/Helm/helm-README.md
  - lib/Helm/helm_optimized.py

## Task:

1. Update your documentation via context7
2. Review docs/streaming_audio_research.md
3. Propose an architecture with me and let's have a conversation about how to implement streaming audio
4. Once we've agreed on the implementation details and settled any outstanding questions, create an actionable task list for this project INSIDE OF THIS DOCUMENT.
   1. NO EMOJIS ARE ALLOWED! Not in the spec, not in the comments, not in the code.
      - No Emojis are allowed, no exceptions.
     - Empojis are lame and they will break the text-to-speech function

### Open Questions: 

Q: The "stopwatch" function of the helm_optimized research was extremely valuable in tracking performance gains and losses while developing streaming audio Can we incorporate that into the TTS and STT functions? I want to be able to track the Time-to-play for each audio request. That is to say, the timer begnis when the request to generate tts is received by tts-webui and the counter stops when the audio for that message has finished playing out of the speakers. These would be useful to track  over time.
A:

Q: Given how critical audio is to this application, and how sensitive it is to latency, where are all of the touch points that we can optimize performance?
A:

### Notes:

- No Emojis are allowed, no exceptions.
  - Empojis are lame and they will break the text-to-speech function
- 
### Progress:
