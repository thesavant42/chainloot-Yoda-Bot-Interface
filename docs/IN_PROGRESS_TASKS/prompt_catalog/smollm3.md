A quick heads up for anyone playing with the little HuggingFaceTB/SmolLM3-3B model that was released a few weeks ago with llama.cpp.

SmolLM3-3B supports toggling thinking mode using /think or /no_think in a system prompt, but it relies on Jinja template features that weren't available in llama.cpp's jinja processor until very recently (merged yesterday: b56683eb).

So to get system-prompt /think and /no_think working, you need to be running the current master version of llama.cpp (until the next official release). I believe some Qwen3 templates might also be affected, so keep that in mind if you're using those.

(And since it relies on the jinja template, if you want to be able to enable/disable thinking from the system prompt remember to pass --jinja to llama-cli and llama-server. Otherwise it will use a fallback template with no system prompt and no thinking.)

Additionally, I ran into a frustrating issue while using the llama-server with the built-in web client where SmolLM3-3B would stop thinking after a few messages even with thinking enabled. It turns out the model needs to see the <think></think> tags in previous messages or it will stop thinking. The llama web client, by default, has an option enabled that strips those tags.

To fix this, go to your web client settings -> Reasoning and disable "Exclude thought process when sending requests to API (Recommended for DeepSeek-R1)".

Finally, to have the web client correctly show the "thinking" section (that you can click to expand/collapse), you need to pass the --reasoning-format none option to llama-server. Example invocation:

```
./llama-server --jinja -ngl 99 --temp 0.6 --reasoning-format none -c 64000 -fa -m ~/llama/models/smollm3-3b/SmolLM3-Q8_0.gguf
```


https://docs.docker.com/ai/compose/models-and-compose/#service-model-binding

```yaml
models:
  SmolLM3-savant:
    model: hf.co/unsloth/SmolLM3-3B-128K-GGUF:Q4_K_M
    context_size: 131072
    runtime_flags:
      - "--jinja"                         # enable builtin template
      - "--temp"
      - "0.8"
      - "--top-p"
      - "0.9"
      - "--verbose"                       # Set verbosity level to infinity
      - "--verbose-prompt"                # Print a verbose prompt before generation
      - "--log-prefix"                    # Enable prefix in log messages
      - "--log-timestamps"                # Enable timestamps in log messages
      - "--log-colors"                    # Enable colored logging
      - "--metrics"
      - "--host" 
      - "192.168.1.98"
      - "--port"
      - "8242"
```      
