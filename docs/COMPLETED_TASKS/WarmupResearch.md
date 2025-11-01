# Warmup Research

A place to track our designs for improving user experiencing by reducing the time spent waiting for the first response from the model.

The approach proposed is to create a script that runs on the TTS-WebUI container as part of the application/conatiner startup process.


### Outline of how this might work

- Once the chatterbox tts-webui extension is fully loaded 
- and the tts OpenaiAPI audio extension is completely loaded
    - 1. Send curl request to generate speech via TTS Audio :
        ```shell
        curl example should go here;
        ```
    - 2. and the STT curl example goes here:
        ```shell
        curl blah
        ```

Docs:
http://alfred:7778/docs#/audio/create_speech_v1_audio_speech_post

### Questions to explore:

**Q: Which TTS models need warming? (chatterbox, others?)**
**A: - chatterbox**

**Q: Which STT models? (whisper-small.en, others?)**
A: I am not sure, what are we loading now?

**Q: Should warmup be part of container build or runtime?**
**A: Runtime, it loads it into memory. It should happen every time the container starts.**

**Q:** How do we verify warmup succeeded?
**A:** For text to speech, the test will generate wav audio output, if we include a time stamp we can confirm by listening to the audio.
    - For speech to text, we can pipe the audio from the text to speech test into the speech to text: if it's successful it should debug print the text to the onsole.
    - docs\testing\stt\test_stt.md **testing doc**
    - docs\testing\stt\stark-downfall.wav  **WAV to test STT for development**

**Q: What's the current TTS-webui container startup process?**
**A: see the start-tts-webui.sh script I attached to teh chat window. It's also in the tts-webui container folder**


This command generates a wav with the timestamp, then runs it through STT to transcribe
```shell
TIMESTAMP=$(date +"%A, %B %d, %Y"); curl --silent -X POST "http://localhost:7778/v1/audio/speech" -H "Content-Type: application/json" -d "{\"model\": \"chatterbox\", \"input\": \"TTS warmup test at $TIMESTAMP\", \"voice\": \"voices/chatterbox/yoda.wav\", \"exaggeration\": 0.5, \"cfg_weight\": 0.5, \"temperature\": 1.4, \"device\": \"cuda\", \"dtype\": \"float32\", \"chunked\": true, \"halve_first_chunk\": true, \"desired_length\": 200, \"max_length\": 300, \"cpu_offload\": false, \"initial_forward_pass_backend\": \"eager\", \"generate_token_backend\": \"cudagraphs-manual\", \"max_new_tokens\": 1000, \"max_cache_len\": 1500, \"language_id\": \"en\"}" --output /tmp/warmup.wav || echo "TTS warmup failed" && curl -X POST "http://localhost:7778/v1/audio/transcriptions" -H "Content-Type: multipart/form-data" -F "file=@/tmp/warmup.wav" -F "model=openai/whisper-small.en" || echo "STT warmup failed" && rm /tmp/warmup.wav;
```
