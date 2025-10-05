# Audio Library Migration TODO


Goal: To modularize/simplify app.py into functional modular code.

Or, in other words, to put this thing on a diet.


## Phase I: COMPLETED Identify all audio functions, creat new library files

### COMPLETED

So far, we have parsed out all of the 
 - TTS functions and created `./lib/tts.py`
 - STT functions and created `./lib/stt.py`

An effort was made to search for all references to the functions that will be migrated to the new library files. 
Each file has been commented with the locations of functions in `app.py` known to reference the "old" locations, and will need to be updated.

## Phase II: Update app.py

### OUTSTANDING

- Update all TTS and STT references detailed in their respective libraries to point at the new library locations in `app.py`
  - As we move through the list of references, we should:
    1. Make a note of the function's location in `app.py`, and log it in the `Changelog.md` file.
      - Updates to the changelog should favor the newest commits at the top of the file. 
    2. Update references to point at new code

## Phase III: Clean app.py & Test

### OUTSTANDING

- Remove all duplicate STT functions from `app.py`
 -- Delete the lines of the duplicate STT functions in `app.py`, do not simply comment them out. 
 -- This exercise is to slim the code base down into lean elegant code
- References from `stt.py` comments:
    # --- References to update ---
    # - Calls to stt_client.audio.transcriptions.create
    # - Calls to raw_pcm_to_wav
    # - Usage of cl.AudioChunk and cl.Audio
    # - Logic within on_audio_chunk and on_audio_end related to audio processing and transcription

- Remove all duplicate TTS functions from `app.py`
 -- Delete the lines of the duplicate TTS functions in `app.py`, do not simply comment them out. 
 -- This exercise is to slim the code base down into lean elegant code
- References from the `tts.py` comments:
    # --- References to update ---
    # - Calls to tts_client.audio.speech.with_streaming_response.create
    # - Usage of cl.Audio
    # - Logic within on_audio_end related to TTS generation
    # - Fetching of available TTS voices
    # - Configuration variables related to TTS (model, voice, speed, exaggeration, etc.)


## Definition of Done

In order for this project to be considered successful, the following criteria must be met.
 - Core appication functioality remains intact and ERROR FREE!
 - NO NEW BUGS from fixing old bugs
 - Chat functionality must remain ERROR FREE!
 - Settings persistence should remain ERROR FREE!
 - Text to speech functionality must remain intact and ERROR FREE!
 - Speech to text functionality must remain intact and ERROR FREE!

 Remember, break complex tasks into small sub-tasks, always refresh your file contents before editing to avoid errors