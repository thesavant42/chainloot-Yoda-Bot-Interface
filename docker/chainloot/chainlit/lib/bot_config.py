# lib/bot_config.py

import chainlit as cl

# Starter messages configuration
def get_starters():
    """
    Generate starter messages programmatically.
    Returns a list of cl.Starter objects for the chat interface.
    """
    return [
        cl.Starter(
            label="time",
            message="what is the current time in Los Angeles? Use mcp.",
            icon="https://picsum.photos/300",
        ),
        cl.Starter(
            label="Fetch",
            message="Fetch the title from http://ifconfig.me/ using mcp.",
            icon="https://picsum.photos/350",
        ),
    ]

# Canonical per-profile configuration (authoritative, no implicit fallbacks)
PROFILE_DEFAULTS = {
    "Yoda": {
        "system_prompt": "You are a helpful AI assistant, who completely believes that he actually *is* Yoda, wise Jedi Master. Reply in Yoda-speak. No more than 2 sentences per message. Never break character. You have access to tools via MCP.",
        "default_voice": "voices/chatterbox/yoda.wav",
    },
    "AI": {
        "system_prompt": "You are a 3-P-O, a helpful AI assistant. Your responses are concise and brief.",
        "default_voice": "voices/chatterbox/3po.wav",
    },
    "Stark": {
        "system_prompt": "You are a helpful but snarky AI assistant. Your name is Tony. No more than 2 sentences per message.",
        "default_voice": "voices/chatterbox/stark.wav",
    },
}

def get_profile_defaults():
    """
    Get the profile defaults dictionary.
    Returns the PROFILE_DEFAULTS configuration.
    """
    return PROFILE_DEFAULTS

@cl.set_chat_profiles
async def chat_profile():
    """
    Define chat profiles for the Chainlit interface.
    This function is automatically registered with Chainlit when imported.
    """
    starters = get_starters()
    return [
        cl.ChatProfile(
            name="Yoda",
            markdown_description="An AI who thinks he is a Jedi Master",
            starters=starters,
            icon="/public/avatars/yoda.png",
        ),
        cl.ChatProfile(
            name="AI",
            markdown_description="Human <-> Cyborg Relations",
            starters=starters,
            icon="/public/avatars/ai.png",
        ),
        cl.ChatProfile(
            name="Stark",
            markdown_description="Billionaire genius playboy philanthropist.",
            starters=starters,
            icon="/public/avatars/stark.png",
        ),
    ]