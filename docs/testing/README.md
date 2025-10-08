# Put helper/testing scripts in here. This is only for dev purposes, no production code allowed.

## Directory Structure

datalayer\ - DB test scripts, obsolete, dont use

mcp\ - MCP Testing chainlit apps
    - mcp-time-search.py                # Uses `mcp-server-time` to get local time, and Brave Search API to use search engine results
    - mcp-server-time-demo.py           # Uses `mcp-server-time` to get local timeS

stt\ - Speech-to-Text (Whisper Tests)
    - stark-downfall.wav                # Generated audio example, Stark
    - stives.wav                        # Nursery rhyme WAV to test transcription
    - test_stt.md                       # Testing helper notes

- .\feels-test.py - Test script to classify a block of text based upon emotional sentiment

- .\README.md - This doc