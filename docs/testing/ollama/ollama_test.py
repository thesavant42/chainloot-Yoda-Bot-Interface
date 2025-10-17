# ollama_test.py - Chainlit with local ollama
# Ollama host: http://192.168.1.98:11434/
# forked from https://raw.githubusercontent.com/Chainlit/cookbook/218e4f9a1837a46fcaaf40b3ca3033d71b7fe66e/deepseek-r1/ollama.py
# Run from workspace root with `chainlit run .\docs\testing\ollama_test.py`
# TODO Fold this functionality into the primary script

import time
import httpx
from openai import AsyncOpenAI

import chainlit as cl
from chainlit.input_widget import Select

client = AsyncOpenAI(api_key="ollama", base_url="http://192.168.1.98:11434/v1/")
# default Model: smollm2

# Fetch available models from Ollama
async def fetch_ollama_models():
    try:
        async with httpx.AsyncClient() as http_client:
            response = await http_client.get("http://192.168.1.98:11434/api/tags")
            if response.status_code == 200:
                models_data = response.json()
                return [model['name'] for model in models_data.get('models', [])]
    except Exception as e:
        print(f"Error fetching models: {e}")
    return ["smollm2:latest"]  # fallback to default model

available_models = []

@cl.on_chat_start
async def on_chat_start():
    global available_models
    # Fetch available models when chat starts
    available_models = await fetch_ollama_models()
    
    # Set default model if not in the list
    default_model = "smollm2:latest"
    if default_model not in available_models:
        default_model = available_models[0] if available_models else "smollm2:latest"
    
    # Store the selected model in the user session
    cl.user_session.set("selected_model", default_model)
    
    # Create settings UI with model selection
    settings = cl.ChatSettings(
        [
            Select(
                id="model",
                label="Ollama Model",
                values=available_models,
                initial_index=available_models.index(default_model) if default_model in available_models else 0
            )
        ]
    )
    await settings.send()

@cl.on_settings_update
async def on_settings_update(settings):
    # Update the selected model in the user session when settings change
    cl.user_session.set("selected_model", settings["model"])
    await cl.Message(content=f"Model updated to: {settings['model']}").send()

@cl.on_message
async def on_message(msg: cl.Message):
    start = time.time()
    
    # Get the selected model from user session
    selected_model = cl.user_session.get("selected_model", "smollm2:latest")
    
    stream = await client.chat.completions.create(
        model=selected_model,
        messages=[
            {"role": "system", "content": "You are an helpful assistant"},
            *cl.chat_context.to_openai(),
        ],
        stream=True,
    )

    thinking = False

    # Streaming the thinking
    async with cl.Step(name="Thinking") as thinking_step:
        final_answer = cl.Message(content="")

        async for chunk in stream:
            delta = chunk.choices[0].delta

            if delta.content == "<think>":
                thinking = True
                continue

            if delta.content == "</think>":
                thinking = False
                thought_for = round(time.time() - start)
                thinking_step.name = f"Thought for {thought_for}s"
                await thinking_step.update()
                continue

            if thinking:
                await thinking_step.stream_token(delta.content)
            else:
                await final_answer.stream_token(delta.content)

    await final_answer.send()