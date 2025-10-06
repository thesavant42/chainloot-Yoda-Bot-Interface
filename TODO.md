# TODO: Refactor Prompt Catalog / Chat Profiles

- Chat Profiles
  - https://docs.chainlit.io/api-reference/chat-profiles

- Chat profiles allow a user to rapidly swap between different chat templates
- This is the functionality I was looking for when I created the prompt_catalog, but I'd much prefer to use the official and recommend method.

## Partially Implemented So Far

- Profiles in app.py now properly how Avatar icons, based on their profile.
- This works, with avatar support
- This would be great to use to store and configure system prompts, and other profile-specific attributes

### app.py profiles

app.py:108-126
```
@cl.set_chat_profiles
async def chat_profile():
    return [
        cl.ChatProfile(
            name="Yoda",
            markdown_description="An AI who thinks he is a Jedi Master",
            icon="/public/avatars/yoda.png",
        ),
        cl.ChatProfile(
            name="AI",
            markdown_description="Human <-> Cyborg Relations",
            icon="/public/avatars/ai.png",
        ),
        cl.ChatProfile(
            name="Stark",
            markdown_description="Billionaire genius playboy philanthropist.",
            icon="/public/avatars/stark.png",
        ),
    ]
```

### config.toml overrides

It's possible to specify specific config.toml overrides per profile... (contrived example from the docs)

```
from chainlit.config import (
    ChainlitConfigOverrides,
    FeaturesSettings,
    McpFeature,
    UISettings,
)

@cl.set_chat_profiles
async def chat_profile(current_user: cl.User):
    return [
        cl.ChatProfile(
            name="MCP Enabled",
            markdown_description="Profile with **MCP features enabled**. This profile has *Model Context Protocol* support activated. [Learn more](https://example.com/mcp)",
            icon="https://picsum.photos/250",
            starters=starters,
            config_overrides=ChainlitConfigOverrides(
                ui=UISettings(name="MCP UI"),
                features=FeaturesSettings(
                    mcp=McpFeature(
                        enabled=True,
                        stdio={"enabled": True},
                        sse={"enabled": True},
                        streamable_http={"enabled": True},
                    )
                ),
            ),
        ),
```

###  Goal 

I'd like to refactor the prompt_catalog into a series of chat profiles, with specific overrides per character.

- Given that:
    - I have 3 profiles:
        - AI 
        - Yoda 
        - Stark 

And the prompt_catalog is:

lib\config_handler.py:22-26
```
prompt_catalog = {
    "AI": "You are a 3-P-O, a helpful AI assistant. Your responses are concise and brief. No more than 2 sentences per message.",
    "Yoda": "You are Yoda, wise Jedi Master. Reply in Yoda-speak. No more than 2 sentences per message.",
    "Stark": "You are a helpful but snarky AI assistant. Your name is Tony. No more than 2 sentences per message."
}
```
...we can move the prompts into chat profiles, and this should allow hot swapping characters.


### Tasks

- 1. Update Profiles to include configurations for each profile, setting the prompt to the corresponding Profile.
   - This is almost a direct transposition of prompt_catalog into the user profile
- 2. Update all references to prompt_catalog, point them at the Chat Profile variable created in step 1
- 3. Remove old prompt_catalog function in config_handler.

- Here's a lot of references that will for sure need to be modified or deleted. 
   - This list should be complete, but we should definitely check again for more references before we start deleting things.

### Update all prompt_catalog references, redirect to the Character profile, remove the old reference (if applicable):
 - app.py:11-16
```
from lib.config_handler import (
    config,
    client,
    tts_client,
    stt_client,
    prompt_catalog, # current reference
```


app.py:143-146
```
    system_prompt_key = config.get("system_prompt_key") 
    cl.user_session.set("system_prompt", prompt_catalog[system_prompt_key])
    # derive character name from prompt settings
    cl.user_session.set("character", system_prompt_key)
```

app.py:166-166
```
system_prompt_index = list(prompt_catalog.keys()).index(system_prompt_key) if system_prompt_key in prompt_catalog else 0
```

app.py:190-195 # Settings dropdown; this should be completely removed from Settings widget
```
            Select(
                id="system_prompt",
                label="System Prompt",
                values=list(prompt_catalog.keys()),
                initial_index=system_prompt_index
            ),
```

app.py:253-253
```
   cl.user_session.set("system_prompt", prompt_catalog[settings["system_prompt"]])
```

app.py:272-277 # cl.on_settings_update
```
        if "system_prompt" in settings:
            # We'll store the key here, and the full prompt will be resolved on load.
            current_config["system_prompt_key"] = settings["system_prompt"]
        if "character" in settings:
            # Persist character
            current_config["character"] = settings["character"]
```
### Character References
app.py:52-57
```
    # 3. Send text response to the UI
    character = cl.user_session.get("character")
    text_msg = await cl.Message(
        content=full_response,
        author=character
    )   .send()
```

app.py:143-146
```
    system_prompt_key = config.get("system_prompt_key") 
    cl.user_session.set("system_prompt", prompt_catalog[system_prompt_key])
    # derive character name from prompt settings
    cl.user_session.set("character", system_prompt_key)
```

app.py:166-166
```
system_prompt_index = list(prompt_catalog.keys()).index(system_prompt_key) if system_prompt_key in prompt_catalog else 0
```

config.json:35-36
```
    "system_prompt_key": "Stark",
    "character": null,
```


