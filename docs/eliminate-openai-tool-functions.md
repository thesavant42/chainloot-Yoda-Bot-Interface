# Invalid OpenAI modules cause CRITICAL FAILURE

## Problem Statement:

LLM incorrectly conflates OpenAI chat API with OpenAI Tool Functions. we use their chat, not their tools.

## Task: Investigate why programming agent keeps using openai-specific tool calls.

- Create a *new markdown document*, track your work **AS YOU GO**
- **Do not write to any other files**
- **Do not execute any code**

## Open Questions

What are all of the openai references in this workspace?
- There SHOULD be openai-compatible AUDIO apis
    - text to speech
    - speech to text
- there should NOT be open ai tool functions
- there should not be comments about openai tool functions
- there should not be documentation on openai tool functions

catalog all openai references, mark whether it is:
 - tool function?
 - audio related?
 - documentation?

 Do not just search for keywords and pat yourself on the back if you don't find them. READ THE CODE and step through it


 
