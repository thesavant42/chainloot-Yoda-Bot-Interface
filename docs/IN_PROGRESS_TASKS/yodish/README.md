# yoda-translator library 

- https://github.com/thesavant42/yoda-translator

- I spent some time on the  Yoda language syntax message generation system and found a mostly complete solution: 
    - called "Yoda Translator" 
    - by https://github.com/haohangxu/yoda-translator which was almmost exacly what I needed. 
  I modified it to make it into a module that accepts text or text files as an argument, and then prints the sentence/text in Object-Subject-Verb (OSV) format.

### Use as a Library:

```python
from yoda import translate

print(translate('You are conflicted.'))        # "Conflicted, you are."
print(translate('Size does not matter.'))      # "Size matters not."  
print(translate('This is my home.'))           # "My home this is."
```

### Use from CLI:

```shell
# Single sentence
python yoda_cli.py --sentence "This is a normal sentence."

# Process dialogue file  
python yoda_cli.py --file dialogue.txt

# Microservice mode (quiet output)
python yoda_cli.py --sentence "You are strong." --quiet

# Pipe input for microservices
echo "Hello there" | python yoda_cli.py --stdin --quiet
```

### Chainlit Integration Example

```python
import chainlit as cl
from yoda import translate

@cl.on_message
async def main(message: cl.Message):
    yoda_text = translate(message.content)
    await cl.Message(content=f"Yoda says: {yoda_text}").send()
```

### Requirements

- We have 3 personas currently programmed into the app, only 1 of which should have the Yoda module applied. (Yoda, obviously). So we cann't just leave the library inline all of the time, as this would break the other personas, and probably a lot of other things.
- Instead, I want to only apply the Yoda filter to messages from fro the Assistant role to User, while the Yoda profile is selected. This means that any language not sent to the user will remain in standard English. 
    - One side effect of yoda syntax, it can have unpredictable results on commands and tool use. Best to do those in plain English.

---

### Present State: 

 - Yoda's dialogue is configured via the prompt, with varying levels of acceptability, but mostly disappointing or inconsistent.

### Desired State:

 - Remove the syntax instruction from the prompt entirely, and let the library handle it invisibly.
 - Tool calls work well, user gets the Yoda experience while remaining adaptable for other personas.

    1. **Clean Separation**: Separating syntax transformation from LLM logic is architecturally sound and prevents inconsistent results.
    2. **Optimal Integration Point**: Applying translation in `lib/chat.py` after LLM response but before UI send ensures only user-facing content is translated, preserving tool calls and internal processing.
    3. **Persona-Specific**: The conditional application based on `chat_profile == "Yoda"` ensures other personas remain unaffected.
    4. **Deterministic Results**: Using a rule-based translator provides consistent, predictable Yoda-speak transformation.

### Acceptance Critera:
- No new bugs
- No regressions in functionality
- Yoda persona dialogue is routed through yoda-translator library as a final step before it's passed to the TTS engine.

---

### Task: Integrate yoda-translator library

- [x] ~~Use context7 to look up docs for chainlit and Spacy~~ **DONE!**
- [x] ~~Download library from github~~ **DONE!**
    - ~~https://github.com/thesavant42/yoda-translator~~ **DONE!**
    - ~~docs\IN_PROGRESS_TASKS\yodish\yoda-translator~~ **DONE!**
- [x] ~~Integrate into container build process for chainlit container~~ **DONE!**
- [x] Ensure that messages do NOT route through translator UNLESS the persona is Yoda AND the message is dialgoue intended for the User. **DONE!**
    Chain of Thought content, A2A chats, etc, should not be translated.

#### A few considerations to address:

1. [x] ~~**SpaCy Model Download**: The yoda-translator requires the `en_core_web_sm` SpaCy model.~~ **DONE!** 
    - ~~While SpaCy 3.6.1 is already in requirements, I'll need to add the model download to the Dockerfile (similar to the existing sentiment model pre-download).~~
    - ~~`    python -m spacy download en_core_web_sm`~~
2. [x] ~~**Library Installation**: The yoda-translator library needs to be copied into the chainlit container and added to the Python path, or installed via pip/requirements.~~
        - **Copied files to chainlit lib folder.**
3. [x] ~~**Error Handling**: Consider fallback behavior if yoda-translator fails (network issues, model problems, etc.) - should gracefully fall back to original text.~~ **DONE!**
    - I do *NOT* want to add any error handling *at this stage*. The reason: I want to spot the bugs early and often, not pave over them.
4. [x] ~~**Performance Impact**: Each translation adds processing time. The library is fast (~10-50ms per sentence), but should be measured in production.~~ **DONE!**
5. [x] ~~**Prompt Update**: Remove "Reply in Yoda-speak" from the Yoda system prompt in `bot_config.py` to avoid double-encoding.~~ **DONE!**


**Q: What is the t-shirt size of this effort?**
**A: Small (2-4 hours)**

- [x] ~~**Copy library files**: 15 minutes (copy yoda-translator to chainlit/lib/)~~ **DONE!**
- [x] ~~**Update Dockerfile**: 15 minutes (add SpaCy model download)~~ **DONE!**
- [x] ~~**Update bot_config.py**: 10 minutes (remove Yoda-speak from system prompt)~~ **DONE!**  
- [ ] **Modify chat.py**: 30 minutes (add conditional translation logic)

---

## Task 2: Modify chat.py
- Use context7 to update your docs for chainlit SpaCy, any any others as needed 
- [x] **Modify chat.py**: 30 minutes (add conditional translation logic) **DONE!**

The integration point should be right after line 218 in `lib/chat.py` where `full_response` is ready but before `process_message_for_tts()`:

```python
# Apply Yoda translation if using Yoda persona
if persona == "Yoda" and full_response.strip():
    try:
        from yoda import translate
        full_response = translate(full_response)
    except Exception as e:
        logger.warning(f"Yoda translation failed: {e}")
        # Continue with original text
```
