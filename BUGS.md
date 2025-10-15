## Bug: "available_voices is empty. Ensure TTS voices are fetched before starting the chat."

- Chatterbox plugin in gradio UI shows "Avaailable", making it seem as if it's not installed. 
- Upon trying to install, the following error occurs:

```
Collecting git+https://github.com/rsxdalv/extension_chatterbox@main
Cloning https://github.com/rsxdalv/extension_chatterbox (to revision main) to /tmp/pip-req-build-gtpwh4ds
Running command git clone --filter=blob:none --quiet https://github.com/rsxdalv/extension_chatterbox /tmp/pip-req-build-gtpwh4ds
Resolved https://github.com/rsxdalv/extension_chatterbox to commit 6dacb53a29ff68a662c79b60b60f9395baf09cb0
Installing build dependencies: started
Installing build dependencies: finished with status 'done'
Getting requirements to build wheel: started
Getting requirements to build wheel: finished with status 'done'
Preparing metadata (pyproject.toml): started
Preparing metadata (pyproject.toml): finished with status 'done'
...[snip for brevity...]
Downloading aiofiles-23.2.1-py3-none-any.whl.metadata (9.7 kB)
Collecting tomlkit==0.12.0 (from gradio==5.5.0)
Downloading tomlkit-0.12.0-py3-none-any.whl.metadata (2.7 kB)

Collecting resampy==0.4.3 (from chatterbox-tts@ git+https://github.com/rsxdalv/chatterbox@faster->tts_webui_extension.chatterbox==4.2.0)
Downloading resampy-0.4.3-py3-none-any.whl.metadata (3.0 kB)
Collecting python-multipart==0.0.12 (from gradio==5.5.0)
Downloading python_multipart-0.0.12-py3-none-any.whl.metadata (1.9 kB)
Collecting gradio-client==1.4.2 (from gradio==5.5.0)
Downloading gradio_client-1.4.2-py3-none-any.whl.metadata (7.1 kB)
ERROR: Cannot install gradio==5.5.0 and russian-text-stresser because these package versions have conflicting dependencies.

The conflict is caused by:
gradio 5.5.0 depends on typer<1.0 and >=0.12; sys_platform != "emscripten"
spacy 3.6.1 depends on typer<0.10.0 and >=0.3.0
spacy 3.6.0 depends on typer<0.10.0 and >=0.3.0

To fix this you could try to:
1. loosen the range of package versions you've specified
2. remove package versions to allow pip to attempt to solve the dependency conflict

ERROR: ResolutionImpossible: for help visit https://pip.pypa.io/en/latest/topics/dependency-resolution/#dealing-with-dependency-conflicts
Failed to install Chatterbox dependencies
False
```


## Multiple instances of spacy: 3.6.0 and 3.6.1

- depends on typer<0.10.0 and >=0.3.0


```
Collecting resampy==0.4.3 (from chatterbox-tts@ git+https://github.com/rsxdalv/chatterbox@faster->tts_webui_extension.chatterbox==4.2.0)
Downloading resampy-0.4.3-py3-none-any.whl.metadata (3.0 kB)
Collecting python-multipart==0.0.12 (from gradio==5.5.0)
Downloading python_multipart-0.0.12-py3-none-any.whl.metadata (1.9 kB)
Collecting gradio-client==1.4.2 (from gradio==5.5.0)
Downloading gradio_client-1.4.2-py3-none-any.whl.metadata (7.1 kB)
```

## No Cuda Toolkit: Ollama

- Install needs to setup cuda toolkit 
- GPU Info is empty
- OpenAI API not enabled by default
  - Check "Autostart API" box
  - Click "Activate API"


```
ollama     | 2025-10-15 14:49:48.719 | time=2025-10-15T21:49:48.718Z level=INFO source=routes.go:1481 msg="server config" env="map[CUDA_VISIBLE_DEVICES: GPU_DEVICE_ORDINAL: HIP_VISIBLE_DEVICES: HSA_OVERRIDE_GFX_VERSION: HTTPS_PROXY: HTTP_PROXY: NO_PROXY: OLLAMA_CONTEXT_LENGTH:4096 OLLAMA_DEBUG:INFO OLLAMA_FLASH_ATTENTION:false OLLAMA_GPU_OVERHEAD:0 OLLAMA_HOST:http://0.0.0.0:11434 OLLAMA_INTEL_GPU:false OLLAMA_KEEP_ALIVE:5m0s OLLAMA_KV_CACHE_TYPE: OLLAMA_LLM_LIBRARY: OLLAMA_LOAD_TIMEOUT:5m0s OLLAMA_MAX_LOADED_MODELS:0 OLLAMA_MAX_QUEUE:512 OLLAMA_MODELS:/root/.ollama/models OLLAMA_MULTIUSER_CACHE:false OLLAMA_NEW_ENGINE:false OLLAMA_NOHISTORY:false OLLAMA_NOPRUNE:false OLLAMA_NUM_PARALLEL:1 OLLAMA_ORIGINS:[http://localhost https://localhost http://localhost:* https://localhost:* http://127.0.0.1 https://127.0.0.1 http://127.0.0.1:* https://127.0.0.1:* http://0.0.0.0 https://0.0.0.0 http://0.0.0.0:* https://0.0.0.0:* app://* file://* tauri://* vscode-webview://* vscode-file://*] OLLAMA_REMOTES:[ollama.com] OLLAMA_SCHED_SPREAD:false ROCR_VISIBLE_DEVICES: http_proxy: https_proxy: no_proxy:]"
ollama     | 2025-10-15 14:49:48.719 | time=2025-10-15T21:49:48.719Z level=INFO source=images.go:522 msg="total blobs: 0"
ollama     | 2025-10-15 14:49:48.719 | time=2025-10-15T21:49:48.719Z level=INFO source=images.go:529 msg="total unused blobs removed: 0"
ollama     | 2025-10-15 14:49:48.720 | time=2025-10-15T21:49:48.720Z level=INFO source=routes.go:1534 msg="Listening on [::]:11434 (version 0.12.5)"
ollama     | 2025-10-15 14:49:48.720 | time=2025-10-15T21:49:48.720Z level=INFO source=runner.go:80 msg="discovering available GPUs..."
ollama     | 2025-10-15 14:49:48.762 | time=2025-10-15T21:49:48.762Z level=INFO source=types.go:129 msg="inference compute" id=cpu library=cpu compute="" name=cpu description=cpu libdirs=ollama driver="" pci_id="" type="" total="31.3 GiB" available="22.2 GiB"
ollama     | 2025-10-15 14:49:48.762 | time=2025-10-15T21:49:48.762Z level=INFO source=routes.go:1575 msg="entering low vram mode" "total vram"="0 B" threshold="20.0 GiB"
```

## Prisma error: Unsupported Engine.  Prisma only supports Node.js >= 16.13.

- Eprror in Prisma ORM
  
```
chainlit   | 2025-10-15 14:49:52.390 | An error ocurred while installing the Prisma CLI; npm install log: npm WARN EBADENGINE Unsupported engine {
chainlit   | 2025-10-15 14:49:52.390 | npm WARN EBADENGINE   package: 'prisma@5.17.0',
chainlit   | 2025-10-15 14:49:52.390 | npm WARN EBADENGINE   required: { node: '>=16.13' },
chainlit   | 2025-10-15 14:49:52.390 | npm WARN EBADENGINE   current: { node: 'v12.22.12', npm: '7.5.2' }
chainlit   | 2025-10-15 14:49:52.390 | npm WARN EBADENGINE }
chainlit   | 2025-10-15 14:49:52.390 | npm ERR! code 1
chainlit   | 2025-10-15 14:49:52.390 | npm ERR! path /root/.cache/prisma-python/binaries/5.17.0/393aa359c9ad4a4bb28630fb5613f9c281cde053/node_modules/prisma
chainlit   | 2025-10-15 14:49:52.390 | npm ERR! command failed
chainlit   | 2025-10-15 14:49:52.390 | npm ERR! command sh -c node scripts/preinstall-entry.js
chainlit   | 2025-10-15 14:49:52.390 | npm ERR! ┌──────────────────────────────────────────────┐
chainlit   | 2025-10-15 14:49:52.390 | npm ERR! │    Prisma only supports Node.js >= 16.13.    │
chainlit   | 2025-10-15 14:49:52.390 | npm ERR! │    Please upgrade your Node.js version.      │
chainlit   | 2025-10-15 14:49:52.390 | npm ERR! └──────────────────────────────────────────────┘
chainlit   | 2025-10-15 14:49:52.390 | 
chainlit   | 2025-10-15 14:49:52.390 | npm ERR! A complete log of this run can be found in:
chainlit   | 2025-10-15 14:49:52.390 | npm ERR!     /root/.npm/_logs/2025-10-15T21_49_52_374Z-debug.log
chainlit   | 2025-10-15 14:49:52.390 | 
chainlit   | 2025-10-15 14:49:52.390 | Traceback (most recent call last):
chainlit   | 2025-10-15 14:49:52.390 |   File "/usr/local/bin/prisma", line 8, in <module>
chainlit   | 2025-10-15 14:49:52.390 |     sys.exit(main())
chainlit   | 2025-10-15 14:49:52.390 |              ^^^^^^
chainlit   | 2025-10-15 14:49:52.390 |   File "/usr/local/lib/python3.11/site-packages/prisma/cli/cli.py", line 37, in main
chainlit   | 2025-10-15 14:49:52.390 |     sys.exit(prisma.run(args[1:]))
chainlit   | 2025-10-15 14:49:52.390 |              ^^^^^^^^^^^^^^^^^^^^
chainlit   | 2025-10-15 14:49:52.390 |   File "/usr/local/lib/python3.11/site-packages/prisma/cli/prisma.py", line 35, in run
chainlit   | 2025-10-15 14:49:52.390 |     entrypoint = ensure_cached().entrypoint
chainlit   | 2025-10-15 14:49:52.390 |                  ^^^^^^^^^^^^^^^
chainlit   | 2025-10-15 14:49:52.390 |   File "/usr/local/lib/python3.11/site-packages/prisma/cli/prisma.py", line 99, in ensure_cached
chainlit   | 2025-10-15 14:49:52.390 |     proc.check_returncode()
chainlit   | 2025-10-15 14:49:52.390 |   File "/usr/local/lib/python3.11/subprocess.py", line 502, in check_returncode
chainlit   | 2025-10-15 14:49:52.391 |     raise CalledProcessError(self.returncode, self.args, self.stdout,
chainlit   | 2025-10-15 14:49:52.391 | subprocess.CalledProcessError: Command '['/usr/bin/npm', 'install', 'prisma@5.17.0']' returned non-zero exit status 1.
chainlit   | 2025-10-15 14:49:52.423 | Generating Prisma client...
chainlit   | 2025-10-15 14:49:52.616 | Installing Prisma CLI
chainlit   | 2025-10-15 14:49:53.563 | An error ocurred while installing the Prisma CLI; npm install log: npm WARN EBADENGINE Unsupported engine {
chainlit   | 2025-10-15 14:49:53.563 | npm WARN EBADENGINE   package: 'prisma@5.17.0',
chainlit   | 2025-10-15 14:49:53.563 | npm WARN EBADENGINE   required: { node: '>=16.13' },
chainlit   | 2025-10-15 14:49:53.563 | npm WARN EBADENGINE   current: { node: 'v12.22.12', npm: '7.5.2' }
chainlit   | 2025-10-15 14:49:53.563 | npm WARN EBADENGINE }
chainlit   | 2025-10-15 14:49:53.563 | npm ERR! code 1
chainlit   | 2025-10-15 14:49:53.563 | npm ERR! path /root/.cache/prisma-python/binaries/5.17.0/393aa359c9ad4a4bb28630fb5613f9c281cde053/node_modules/prisma
chainlit   | 2025-10-15 14:49:53.563 | npm ERR! command failed
chainlit   | 2025-10-15 14:49:53.563 | npm ERR! command sh -c node scripts/preinstall-entry.js
chainlit   | 2025-10-15 14:49:53.563 | npm ERR! ┌──────────────────────────────────────────────┐
chainlit   | 2025-10-15 14:49:53.563 | npm ERR! │    Prisma only supports Node.js >= 16.13.    │
chainlit   | 2025-10-15 14:49:53.563 | npm ERR! │    Please upgrade your Node.js version.      │
chainlit   | 2025-10-15 14:49:53.563 | npm ERR! └──────────────────────────────────────────────┘
chainlit   | 2025-10-15 14:49:53.563 | 
chainlit   | 2025-10-15 14:49:53.563 | npm ERR! A complete log of this run can be found in:
chainlit   | 2025-10-15 14:49:53.563 | npm ERR!     /root/.npm/_logs/2025-10-15T21_49_53_507Z-debug.log
chainlit   | 2025-10-15 14:49:53.563 | 
chainlit   | 2025-10-15 14:49:53.564 | Traceback (most recent call last):
chainlit   | 2025-10-15 14:49:53.564 |   File "/usr/local/bin/prisma", line 8, in <module>
chainlit   | 2025-10-15 14:49:53.564 |     sys.exit(main())
chainlit   | 2025-10-15 14:49:53.564 |              ^^^^^^
chainlit   | 2025-10-15 14:49:53.564 |   File "/usr/local/lib/python3.11/site-packages/prisma/cli/cli.py", line 37, in main
chainlit   | 2025-10-15 14:49:53.564 |     sys.exit(prisma.run(args[1:]))
chainlit   | 2025-10-15 14:49:53.564 |              ^^^^^^^^^^^^^^^^^^^^
chainlit   | 2025-10-15 14:49:53.564 |   File "/usr/local/lib/python3.11/site-packages/prisma/cli/prisma.py", line 35, in run
chainlit   | 2025-10-15 14:49:53.564 |     entrypoint = ensure_cached().entrypoint
chainlit   | 2025-10-15 14:49:53.564 |                  ^^^^^^^^^^^^^^^
chainlit   | 2025-10-15 14:49:53.564 |   File "/usr/local/lib/python3.11/site-packages/prisma/cli/prisma.py", line 99, in ensure_cached
chainlit   | 2025-10-15 14:49:53.564 |     proc.check_returncode()
chainlit   | 2025-10-15 14:49:53.564 |   File "/usr/local/lib/python3.11/subprocess.py", line 502, in check_returncode
chainlit   | 2025-10-15 14:49:53.564 |     raise CalledProcessError(self.returncode, self.args, self.stdout,
chainlit   | 2025-10-15 14:49:53.564 | subprocess.CalledProcessError: Command '['/usr/bin/npm', 'install', 'prisma@5.17.0']' returned non-zero exit status 1.
```

## OpenAI API does not start enabled

- This must be manually enabled after the depends have been satisfied.
```
chainlit   | 2025-10-15 14:50:00.474 | 2025-10-15 21:50:00 - Could not fetch voices from TTS API: HTTPConnectionPool(host='tts-webui', port=7778): Max retries exceeded with url: /v1/audio/voices/chatterbox (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x7bf4135b1ed0>: Failed to establish a new connection: [Errno 111] Connection refused'))
```

## Node errors affect MCP Services

- Npm engine is needed for mmany MCP services
  
```
chainlit   | 2025-10-15 14:50:42.107 | npm WARN EBADENGINE Unsupported engine {
chainlit   | 2025-10-15 14:50:42.107 | npm WARN EBADENGINE   package: '@modelcontextprotocol/sdk@1.18.2',
chainlit   | 2025-10-15 14:50:42.107 | npm WARN EBADENGINE   required: { node: '>=18' },
chainlit   | 2025-10-15 14:50:42.107 | npm WARN EBADENGINE   current: { node: 'v12.22.12', npm: '7.5.2' }
chainlit   | 2025-10-15 14:50:42.107 | npm WARN EBADENGINE }
chainlit   | 2025-10-15 14:50:42.107 | npm WARN EBADENGINE Unsupported engine {
chainlit   | 2025-10-15 14:50:42.107 | npm WARN EBADENGINE   package: 'commander@14.0.1',
chainlit   | 2025-10-15 14:50:42.107 | npm WARN EBADENGINE   required: { node: '>=20' },
chainlit   | 2025-10-15 14:50:42.107 | npm WARN EBADENGINE   current: { node: 'v12.22.12', npm: '7.5.2' }
chainlit   | 2025-10-15 14:50:42.107 | npm WARN EBADENGINE }
chainlit   | 2025-10-15 14:50:42.107 | npm WARN EBADENGINE Unsupported engine {
chainlit   | 2025-10-15 14:50:42.107 | npm WARN EBADENGINE   package: 'express@5.1.0',
chainlit   | 2025-10-15 14:50:42.107 | npm WARN EBADENGINE   required: { node: '>= 18' },
chainlit   | 2025-10-15 14:50:42.107 | npm WARN EBADENGINE   current: { node: 'v12.22.12', npm: '7.5.2' }
chainlit   | 2025-10-15 14:50:42.107 | npm WARN EBADENGINE }
chainlit   | 2025-10-15 14:50:42.107 | npm WARN EBADENGINE Unsupported engine {
chainlit   | 2025-10-15 14:50:42.107 | npm WARN EBADENGINE   package: 'eventsource@3.0.7',
chainlit   | 2025-10-15 14:50:42.107 | npm WARN EBADENGINE   required: { node: '>=18.0.0' },
chainlit   | 2025-10-15 14:50:42.107 | npm WARN EBADENGINE   current: { node: 'v12.22.12', npm: '7.5.2' }
chainlit   | 2025-10-15 14:50:42.107 | npm WARN EBADENGINE }
chainlit   | 2025-10-15 14:50:42.107 | npm WARN EBADENGINE Unsupported engine {
chainlit   | 2025-10-15 14:50:42.107 | npm WARN EBADENGINE   package: 'eventsource-parser@3.0.6',
chainlit   | 2025-10-15 14:50:42.107 | npm WARN EBADENGINE   required: { node: '>=18.0.0' },
chainlit   | 2025-10-15 14:50:42.107 | npm WARN EBADENGINE   current: { node: 'v12.22.12', npm: '7.5.2' }
chainlit   | 2025-10-15 14:50:42.107 | npm WARN EBADENGINE }
chainlit   | 2025-10-15 14:50:42.107 | npm WARN EBADENGINE Unsupported engine {
chainlit   | 2025-10-15 14:50:42.107 | npm WARN EBADENGINE   package: 'express-rate-limit@7.5.1',
chainlit   | 2025-10-15 14:50:42.107 | npm WARN EBADENGINE   required: { node: '>= 16' },
chainlit   | 2025-10-15 14:50:42.107 | npm WARN EBADENGINE   current: { node: 'v12.22.12', npm: '7.5.2' }
chainlit   | 2025-10-15 14:50:42.107 | npm WARN EBADENGINE }
chainlit   | 2025-10-15 14:50:42.107 | npm WARN EBADENGINE Unsupported engine {
chainlit   | 2025-10-15 14:50:42.107 | npm WARN EBADENGINE   package: 'pkce-challenge@5.0.0',
chainlit   | 2025-10-15 14:50:42.107 | npm WARN EBADENGINE   required: { node: '>=16.20.0' },
chainlit   | 2025-10-15 14:50:42.107 | npm WARN EBADENGINE   current: { node: 'v12.22.12', npm: '7.5.2' }
chainlit   | 2025-10-15 14:50:42.107 | npm WARN EBADENGINE }
chainlit   | 2025-10-15 14:50:42.107 | npm WARN EBADENGINE Unsupported engine {
chainlit   | 2025-10-15 14:50:42.107 | npm WARN EBADENGINE   package: 'body-parser@2.2.0',
chainlit   | 2025-10-15 14:50:42.107 | npm WARN EBADENGINE   required: { node: '>=18' },
chainlit   | 2025-10-15 14:50:42.107 | npm WARN EBADENGINE   current: { node: 'v12.22.12', npm: '7.5.2' }
chainlit   | 2025-10-15 14:50:42.107 | npm WARN EBADENGINE }
chainlit   | 2025-10-15 14:50:42.107 | npm WARN EBADENGINE Unsupported engine {
chainlit   | 2025-10-15 14:50:42.107 | npm WARN EBADENGINE   package: 'merge-descriptors@2.0.0',
chainlit   | 2025-10-15 14:50:42.107 | npm WARN EBADENGINE   required: { node: '>=18' },
chainlit   | 2025-10-15 14:50:42.107 | npm WARN EBADENGINE   current: { node: 'v12.22.12', npm: '7.5.2' }
chainlit   | 2025-10-15 14:50:42.107 | npm WARN EBADENGINE }
chainlit   | 2025-10-15 14:50:42.107 | npm WARN EBADENGINE Unsupported engine {
chainlit   | 2025-10-15 14:50:42.107 | npm WARN EBADENGINE   package: 'router@2.2.0',
chainlit   | 2025-10-15 14:50:42.107 | npm WARN EBADENGINE   required: { node: '>= 18' },
chainlit   | 2025-10-15 14:50:42.107 | npm WARN EBADENGINE   current: { node: 'v12.22.12', npm: '7.5.2' }
chainlit   | 2025-10-15 14:50:42.107 | npm WARN EBADENGINE }
chainlit   | 2025-10-15 14:50:42.107 | npm WARN EBADENGINE Unsupported engine {
chainlit   | 2025-10-15 14:50:42.107 | npm WARN EBADENGINE   package: 'send@1.2.0',
chainlit   | 2025-10-15 14:50:42.107 | npm WARN EBADENGINE   required: { node: '>= 18' },
chainlit   | 2025-10-15 14:50:42.107 | npm WARN EBADENGINE   current: { node: 'v12.22.12', npm: '7.5.2' }
chainlit   | 2025-10-15 14:50:42.107 | npm WARN EBADENGINE }
chainlit   | 2025-10-15 14:50:42.107 | npm WARN EBADENGINE Unsupported engine {
chainlit   | 2025-10-15 14:50:42.107 | npm WARN EBADENGINE   package: 'serve-static@2.2.0',
chainlit   | 2025-10-15 14:50:42.107 | npm WARN EBADENGINE   required: { node: '>= 18' },
chainlit   | 2025-10-15 14:50:42.107 | npm WARN EBADENGINE   current: { node: 'v12.22.12', npm: '7.5.2' }
chainlit   | 2025-10-15 14:50:42.107 | npm WARN EBADENGINE }
chainlit   | 2025-10-15 14:50:42.784 | file:///usr/local/lib/node_modules/@brave/brave-search-mcp-server/dist/config.js:28
chainlit   | 2025-10-15 14:50:42.784 |     braveApiKey: process.env.BRAVE_API_KEY ?? '',
chainlit   | 2025-10-15 14:50:42.784 |                                             ^
chainlit   | 2025-10-15 14:50:42.784 | 
chainlit   | 2025-10-15 14:50:42.784 | SyntaxError: Unexpected token '?'
chainlit   | 2025-10-15 14:50:42.784 |     at Loader.moduleStrategy (internal/modules/esm/translators.js:133:18)
chainlit   | 2025-10-15 14:50:42.787 | npm ERR! code 1
chainlit   | 2025-10-15 14:50:42.787 | npm ERR! path /app
chainlit   | 2025-10-15 14:50:42.788 | npm ERR! command failed
chainlit   | 2025-10-15 14:50:42.788 | npm ERR! command sh -c brave-search-mcp-server "stdio"
chainlit   | 2025-10-15 14:50:42.796 | 
chainlit   | 2025-10-15 14:50:42.796 | npm ERR! A complete log of this run can be found in:
chainlit   | 2025-10-15 14:50:42.796 | npm ERR!     /root/.npm/_logs/2025-10-15T21_50_42_789Z-debug.log
chainlit   | 2025-10-15 14:50:42.802 | 2025-10-15 21:50:42 - Failed to setup server brave-search: Connection closed
chainlit   | 2025-10-15 14:50:42.803 | 2025-10-15 21:50:42 - Error cleaning up server brave-search: Attempted to exit a cancel scope that isn't the current tasks's current cancel scope
chainlit   | 2025-10-15 14:50:42.803 | 2025-10-15 21:50:42 - Failed to initialize brave-search: Connection closed
chainlit   | 2025-10-15 14:50:42.803 | 2025-10-15 21:50:42 - Initializing fetch: uvx mcp-server-fetch
chainlit   | 2025-10-15 14:50:43.514 | 2025-10-15 21:50:43 - Discovered 1 tools from fetch: ['fetch']
chainlit   | 2025-10-15 14:50:43.514 | 2025-10-15 21:50:43 - Successfully initialized fetch
chainlit   | 2025-10-15 14:50:43.514 | 2025-10-15 21:50:43 - Initializing git: uvx mcp-server-git
chainlit   | 2025-10-15 14:50:44.108 | 2025-10-15 21:50:44 - Discovered 12 tools from git: ['git_status', 'git_diff_unstaged', 'git_diff_staged', 'git_diff', 'git_commit', 'git_add', 'git_reset', 'git_log', 'git_create_branch', 'git_checkout', 'git_show', 'git_branch']
chainlit   | 2025-10-15 14:50:44.108 | 2025-10-15 21:50:44 - Successfully initialized git
chainlit   | 2025-10-15 14:50:44.108 | 2025-10-15 21:50:44 - Initializing memory: npx -y @modelcontextprotocol/server-memory
chainlit   | 2025-10-15 14:50:44.703 | file:///usr/local/lib/node_modules/@modelcontextprotocol/server-memory/node_modules/zod/v3/types.js:58
chainlit   | 2025-10-15 14:50:44.703 |             return { message: message ?? ctx.defaultError };
chainlit   | 2025-10-15 14:50:44.703 |                                        ^
chainlit   | 2025-10-15 14:50:44.703 | 
chainlit   | 2025-10-15 14:50:44.703 | SyntaxError: Unexpected token '?'
chainlit   | 2025-10-15 14:50:44.703 |     at Loader.moduleStrategy (internal/modules/esm/translators.js:133:18)
chainlit   | 2025-10-15 14:50:44.706 | npm ERR! code 1
chainlit   | 2025-10-15 14:50:44.706 | npm ERR! path /app
chainlit   | 2025-10-15 14:50:44.707 | npm ERR! command failed
chainlit   | 2025-10-15 14:50:44.707 | npm ERR! command sh -c mcp-server-memory
chainlit   | 2025-10-15 14:50:44.712 | 
chainlit   | 2025-10-15 14:50:44.713 | npm ERR! A complete log of this run can be found in:
chainlit   | 2025-10-15 14:50:44.713 | npm ERR!     /root/.npm/_logs/2025-10-15T21_50_44_708Z-debug.log
chainlit   | 2025-10-15 14:50:44.717 | 2025-10-15 21:50:44 - Failed to setup server memory: Connection closed
chainlit   | 2025-10-15 14:50:44.718 | 2025-10-15 21:50:44 - Error cleaning up server memory: Attempted to exit a cancel scope that isn't the current tasks's current cancel scope
chainlit   | 2025-10-15 14:50:44.718 | 2025-10-15 21:50:44 - Failed to initialize memory: Connection closed
chainlit   | 2025-10-15 14:50:44.718 | 2025-10-15 21:50:44 - Initializing sequential-thinking: npx -y @modelcontextprotocol/server-sequential-thinking
chainlit   | 2025-10-15 14:50:45.922 | file:///usr/local/lib/node_modules/@modelcontextprotocol/server-sequential-thinking/node_modules/zod/v3/types.js:58
chainlit   | 2025-10-15 14:50:45.922 |             return { message: message ?? ctx.defaultError };
chainlit   | 2025-10-15 14:50:45.922 |                                        ^
chainlit   | 2025-10-15 14:50:45.922 | 
chainlit   | 2025-10-15 14:50:45.922 | SyntaxError: Unexpected token '?'
chainlit   | 2025-10-15 14:50:45.922 |     at Loader.moduleStrategy (internal/modules/esm/translators.js:133:18)
chainlit   | 2025-10-15 14:50:45.925 | npm ERR! code 1
chainlit   | 2025-10-15 14:50:45.925 | npm ERR! path /app
chainlit   | 2025-10-15 14:50:45.926 | npm ERR! command failed
chainlit   | 2025-10-15 14:50:45.926 | npm ERR! command sh -c mcp-server-sequential-thinking
chainlit   | 2025-10-15 14:50:45.932 | 
chainlit   | 2025-10-15 14:50:45.932 | npm ERR! A complete log of this run can be found in:
chainlit   | 2025-10-15 14:50:45.932 | npm ERR!     /root/.npm/_logs/2025-10-15T21_50_45_926Z-debug.log
chainlit   | 2025-10-15 14:50:45.937 | 2025-10-15 21:50:45 - Failed to setup server sequential-thinking: Connection closed
chainlit   | 2025-10-15 14:50:45.938 | 2025-10-15 21:50:45 - Error cleaning up server sequential-thinking: Attempted to exit a cancel scope that isn't the current tasks's current cancel scope
chainlit   | 2025-10-15 14:50:45.938 | 2025-10-15 21:50:45 - Failed to initialize sequential-thinking: Connection closed
chainlit   | 2025-10-15 14:50:45.938 | 2025-10-15 21:50:45 - Initializing youtube-transcript: npx -y @kimtaeyoon83/mcp-server-youtube-transcript
chainlit   | 2025-10-15 14:50:47.401 | file:///usr/local/lib/node_modules/@kimtaeyoon83/mcp-server-youtube-transcript/dist/index.js:117
chainlit   | 2025-10-15 14:50:47.401 |         this.server.setRequestHandler(CallToolRequestSchema, async (request) => this.handleToolCall(request.params.name, request.params.arguments ?? {}));
chainlit   | 2025-10-15 14:50:47.401 |                                                                                                                                                    ^
chainlit   | 2025-10-15 14:50:47.401 | 
chainlit   | 2025-10-15 14:50:47.401 | SyntaxError: Unexpected token '?'
chainlit   | 2025-10-15 14:50:47.401 |     at Loader.moduleStrategy (internal/modules/esm/translators.js:133:18)
chainlit   | 2025-10-15 14:50:47.401 |     at async link (internal/modules/esm/module_job.js:42:21)
chainlit   | 2025-10-15 14:50:47.404 | npm ERR! code 1
chainlit   | 2025-10-15 14:50:47.404 | npm ERR! path /app
chainlit   | 2025-10-15 14:50:47.405 | npm ERR! command failed
chainlit   | 2025-10-15 14:50:47.405 | npm ERR! command sh -c mcp-server-youtube-transcript
chainlit   | 2025-10-15 14:50:47.410 | 
chainlit   | 2025-10-15 14:50:47.410 | npm ERR! A complete log of this run can be found in:
chainlit   | 2025-10-15 14:50:47.410 | npm ERR!     /root/.npm/_logs/2025-10-15T21_50_47_406Z-debug.log
chainlit   | 2025-10-15 14:50:47.415 | 2025-10-15 21:50:47 - Failed to setup server youtube-transcript: Connection closed
chainlit   | 2025-10-15 14:50:47.417 | 2025-10-15 21:50:47 - Error cleaning up server youtube-transcript: Attempted to exit a cancel scope that isn't the current tasks's current cancel scope
chainlit   | 2025-10-15 14:50:47.417 | 2025-10-15 21:50:47 - Failed to initialize youtube-transcript: Connection closed
```

## Home Assistant MCP fails to load

- This is an httpse mcp, and thusly relies on mcp-proxy


```
chainlit   | 2025-10-15 14:50:48.232 | 2025-10-15 21:50:48 - Initializing Home Assistant: mcp-proxy http://homeassistant.local:8123/mcp_server/sse
chainlit   | 2025-10-15 14:50:48.268 | file:///usr/local/lib/node_modules/mcp-proxy/dist/bin/mcp-proxy.js:4889
chainlit   | 2025-10-15 14:50:48.268 | 		return this._process?.pid ?? null;
chainlit   | 2025-10-15 14:50:48.268 | 		                     ^
chainlit   | 2025-10-15 14:50:48.268 | 
chainlit   | 2025-10-15 14:50:48.268 | SyntaxError: Unexpected token '.'
chainlit   | 2025-10-15 14:50:48.268 |     at Loader.moduleStrategy (internal/modules/esm/translators.js:133:18)
chainlit   | 2025-10-15 14:50:48.268 |     at async link (internal/modules/esm/module_job.js:42:21)
chainlit   | 2025-10-15 14:50:48.269 | 2025-10-15 21:50:48 - Failed to setup server Home Assistant: Connection closed
chainlit   | 2025-10-15 14:50:48.270 | 2025-10-15 21:50:48 - Error cleaning up server Home Assistant: Attempted to exit a cancel scope that isn't the current tasks's current cancel scope
chainlit   | 2025-10-15 14:50:48.270 | 2025-10-15 21:50:48 - Failed to initialize Home Assistant: Connection closed
```


## Unhandled Exception: TTS voices empty

 - The API wasn't able to start, so the voices array is empty

```
chainlit   | 2025-10-15 14:50:48.271 | 2025-10-15 21:50:48 - available_voices is empty. Ensure TTS voices are fetched before starting the chat.
chainlit   | 2025-10-15 14:50:48.271 | Traceback (most recent call last):
chainlit   | 2025-10-15 14:50:48.271 |   File "/usr/local/lib/python3.11/site-packages/chainlit/utils.py", line 57, in wrapper
chainlit   | 2025-10-15 14:50:48.271 |     return await user_function(**params_values)
chainlit   | 2025-10-15 14:50:48.271 |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
chainlit   | 2025-10-15 14:50:48.271 |   File "/usr/local/lib/python3.11/site-packages/chainlit/step.py", line 117, in async_wrapper
chainlit   | 2025-10-15 14:50:48.271 |     result = await func(*args, **kwargs)
chainlit   | 2025-10-15 14:50:48.271 |              ^^^^^^^^^^^^^^^^^^^^^^^^^^^
chainlit   | 2025-10-15 14:50:48.271 |   File "/app/app.py", line 431, in on_chat_start
chainlit   | 2025-10-15 14:50:48.271 |     raise RuntimeError("available_voices is empty. Ensure TTS voices are fetched before starting the chat.")
chainlit   | 2025-10-15 14:50:48.271 | RuntimeError: available_voices is empty. Ensure TTS voices are fetched before starting the chat.
chainlit   | 2025-10-15 14:51:45.628 | The user disconnected!
chainlit   | 2025-10-15 14:51:45.628 | 2025-10-15 21:51:45 - Chat session ended
```

## Chatterbox dependancies install failure

- This is critical, this feature is key 

```

tts-webui  | 2025-10-15 14:52:36.277 | Requirement already satisfied: sniffio>=1.1 in /usr/local/lib/python3.10/dist-packages (from anyio<5.0,>=3.0->gradio==5.5.0) (1.3.1)
postgres   | 2025-10-15 14:54:49.639 | 2025-10-15 21:54:49.638 UTC [27] LOG:  checkpoint starting: time
postgres   | 2025-10-15 14:54:51.683 | 2025-10-15 21:54:51.682 UTC [27] LOG:  checkpoint complete: wrote 23 buffers (0.1%); 0 WAL file(s) added, 0 removed, 0 recycled; write=2.016 s, sync=0.007 s, total=2.045 s; sync files=13, longest=0.002 s, average=0.001 s; distance=15 kB, estimate=15 kB; lsn=0/19FF558, redo lsn=0/19FF520
tts-webui  | 2025-10-15 14:59:43.098 | Traceback (most recent call last):
tts-webui  | 2025-10-15 14:59:43.098 |   File "/usr/local/lib/python3.10/dist-packages/gradio/queueing.py", line 624, in process_events
tts-webui  | 2025-10-15 14:59:43.098 |     response = await route_utils.call_process_api(
tts-webui  | 2025-10-15 14:59:43.098 |   File "/usr/local/lib/python3.10/dist-packages/gradio/route_utils.py", line 323, in call_process_api
tts-webui  | 2025-10-15 14:59:43.098 |     output = await app.get_blocks().process_api(
tts-webui  | 2025-10-15 14:59:43.098 |   File "/usr/local/lib/python3.10/dist-packages/gradio/blocks.py", line 2015, in process_api
tts-webui  | 2025-10-15 14:59:43.098 |     result = await self.call_function(
tts-webui  | 2025-10-15 14:59:43.098 |   File "/usr/local/lib/python3.10/dist-packages/gradio/blocks.py", line 1562, in call_function
tts-webui  | 2025-10-15 14:59:43.098 |     prediction = await anyio.to_thread.run_sync(  # type: ignore
tts-webui  | 2025-10-15 14:59:43.098 |   File "/usr/local/lib/python3.10/dist-packages/anyio/to_thread.py", line 56, in run_sync
tts-webui  | 2025-10-15 14:59:43.098 |     return await get_async_backend().run_sync_in_worker_thread(
tts-webui  | 2025-10-15 14:59:43.098 |   File "/usr/local/lib/python3.10/dist-packages/anyio/_backends/_asyncio.py", line 2476, in run_sync_in_worker_thread
tts-webui  | 2025-10-15 14:59:43.098 |     return await future
tts-webui  | 2025-10-15 14:59:43.098 |   File "/usr/local/lib/python3.10/dist-packages/anyio/_backends/_asyncio.py", line 967, in run
tts-webui  | 2025-10-15 14:59:43.098 |     result = context.run(func, *args)
tts-webui  | 2025-10-15 14:59:43.098 |   File "/usr/local/lib/python3.10/dist-packages/gradio/utils.py", line 865, in wrapper
tts-webui  | 2025-10-15 14:59:43.098 |     response = f(*args, **kwargs)
tts-webui  | 2025-10-15 14:59:43.098 |   File "/app/tts-webui/extensions/builtin/extension_huggingface_cache_manager/main.py", line 38, in scan_cache
tts-webui  | 2025-10-15 14:59:43.098 |     hf_cache_info = scan_cache_dir()
tts-webui  | 2025-10-15 14:59:43.098 |   File "/usr/local/lib/python3.10/dist-packages/huggingface_hub/utils/_cache_manager.py", line 674, in scan_cache_dir
tts-webui  | 2025-10-15 14:59:43.098 |     raise CacheNotFound(
tts-webui  | 2025-10-15 14:59:43.098 | huggingface_hub.errors.CacheNotFound: Cache directory not found: /root/.cache/huggingface/hub. Please use `cache_dir` argument or set `HF_HUB_CACHE` environment variable.

ts-webui  | 2025-10-15 14:59:55.967 | INFO: pip is looking at multiple versions of spacy to determine which version is compatible with other requirements. This could take a while.
tts-webui  | 2025-10-15 14:59:55.967 | Collecting spacy==3.6.* (from russian-text-stresser@ git+https://github.com/Vuizur/add-stress-to-epub->chatterbox-tts@ git+https://github.com/rsxdalv/chatterbox@faster->tts_webui_extension.chatterbox==4.2.0)
tts-webui  | 2025-10-15 14:59:55.967 |   Downloading spacy-3.6.0-cp310-cp310-manylinux_2_17_x86_64.manylinux2014_x86_64.whl.metadata (19 kB)
tts-webui  | 2025-10-15 14:59:55.967 | Collecting gradio==5.5.0
tts-webui  | 2025-10-15 14:59:55.967 |   Downloading gradio-5.5.0-py3-none-any.whl.metadata (16 kB)

tts-webui  | 2025-10-15 14:59:55.967 | ERROR: Cannot install gradio==5.5.0 and russian-text-stresser because these package versions have conflicting dependencies.
tts-webui  | 2025-10-15 14:59:55.967 | 
tts-webui  | 2025-10-15 14:59:55.967 | The conflict is caused by:
tts-webui  | 2025-10-15 14:59:55.967 |     gradio 5.5.0 depends on typer<1.0 and >=0.12; sys_platform != "emscripten"
tts-webui  | 2025-10-15 14:59:55.967 |     spacy 3.6.1 depends on typer<0.10.0 and >=0.3.0
tts-webui  | 2025-10-15 14:59:55.967 |     spacy 3.6.0 depends on typer<0.10.0 and >=0.3.0
tts-webui  | 2025-10-15 14:59:55.967 | 
tts-webui  | 2025-10-15 14:59:55.967 | To fix this you could try to:
tts-webui  | 2025-10-15 14:59:55.967 | 1. loosen the range of package versions you've specified
tts-webui  | 2025-10-15 14:59:55.967 | 2. remove package versions to allow pip to attempt to solve the dependency conflict
tts-webui  | 2025-10-15 14:59:55.967 | 
tts-webui  | 2025-10-15 14:59:55.967 | ERROR: ResolutionImpossible: for help visit https://pip.pypa.io/en/latest/topics/dependency-resolution/#dealing-with-dependency-conflicts
tts-webui  | 2025-10-15 14:59:55.967 | Failed to install Chatterbox dependencies
```

## Kokoro Extension Installation causes exceptions

```
tts-webui  | 2025-10-15 15:03:34.474 | Error generating speech: Kokoro extension is not installed. Please install it to use Kokoro TTS features.
tts-webui  | 2025-10-15 15:03:34.474 | INFO:     127.0.0.1:51048 - "POST /v1/audio/speech HTTP/1.1" 500 Internal Server Error
tts-webui  | 2025-10-15 15:03:34.474 | Traceback (most recent call last):
tts-webui  | 2025-10-15 15:03:34.474 |   File "/usr/local/lib/python3.10/dist-packages/extension_kokoro_tts_api/api.py", line 240, in kokoro_adapter
tts-webui  | 2025-10-15 15:03:34.474 |     from extension_kokoro.main import tts
tts-webui  | 2025-10-15 15:03:34.474 | ModuleNotFoundError: No module named 'extension_kokoro'
tts-webui  | 2025-10-15 15:03:34.474 | 
tts-webui  | 2025-10-15 15:03:34.474 | During handling of the above exception, another exception occurred:
tts-webui  | 2025-10-15 15:03:34.474 | 
tts-webui  | 2025-10-15 15:03:34.474 | Traceback (most recent call last):
tts-webui  | 2025-10-15 15:03:34.474 |   File "/usr/local/lib/python3.10/dist-packages/extension_kokoro_tts_api/api.py", line 476, in create_speech
tts-webui  | 2025-10-15 15:03:34.474 |     audio_data = generate_speech(request)
tts-webui  | 2025-10-15 15:03:34.474 |   File "/usr/local/lib/python3.10/dist-packages/extension_kokoro_tts_api/api.py", line 136, in generate_speech
tts-webui  | 2025-10-15 15:03:34.474 |     result = kokoro_adapter(
tts-webui  | 2025-10-15 15:03:34.474 |   File "/usr/local/lib/python3.10/dist-packages/extension_kokoro_tts_api/api.py", line 232, in wrapper
tts-webui  | 2025-10-15 15:03:34.474 |     return func(*args, **kwargs)
tts-webui  | 2025-10-15 15:03:34.474 |   File "/usr/local/lib/python3.10/dist-packages/extension_kokoro_tts_api/api.py", line 242, in kokoro_adapter
tts-webui  | 2025-10-15 15:03:34.474 |     raise ImportError(
tts-webui  | 2025-10-15 15:03:34.474 | ImportError: Kokoro extension is not installed. Please install it to use Kokoro TTS features.
tts-webui  | 2025-10-15 15:03:34.509 | INFO:     172.21.0.1:44504 - "GET /gradio_api/queue/data?session_hash=03vx3nhlvwp HTTP/1.1" 200 OK
tts-webui  | 2025-10-15 15:03:34.762 | INFO:     172.21.0.1:44504 - "GET /gradio_api/file%3D/tmp/gradio/bd4992587235d9ca472580bfb25bb01ae3777fc6da437a1b6d799442e84ca651/audio HTTP/1.1" 200 OK
tts-webui  | 2025-10-15 15:03:34.791 | INFO:     172.21.0.1:44504 - "GET /gradio_api/file%3D/tmp/gradio/bd4992587235d9ca472580bfb25bb01ae3777fc6da437a1b6d799442e84ca651/audio HTTP/1.1" 200 OK
tts-webui  | 2025-10-15 15:03:56.817 | INFO:     172.21.0.1:44506 - "POST /gradio_api/queue/join HTTP/1.1" 200 OK
tts-webui  | 2025-10-15 15:03:56.915 | INFO:     172.21.0.1:44506 - "GET /gradio_api/queue/data?session_hash=03vx3nhlvwp HTTP/1.1" 200 OK
tts-webui  | 2025-10-15 15:03:57.160 | Traceback (most recent call last):
tts-webui  | 2025-10-15 15:03:57.160 |   File "/usr/local/lib/python3.10/dist-packages/extension_kokoro_tts_api/api.py", line 240, in kokoro_adapter
tts-webui  | 2025-10-15 15:03:57.160 |     from extension_kokoro.main import tts
tts-webui  | 2025-10-15 15:03:57.160 | ModuleNotFoundError: No module named 'extension_kokoro'
tts-webui  | 2025-10-15 15:03:57.160 | 
tts-webui  | 2025-10-15 15:03:57.160 | During handling of the above exception, another exception occurred:
tts-webui  | 2025-10-15 15:03:57.160 | 
tts-webui  | 2025-10-15 15:03:57.160 | Traceback (most recent call last):
tts-webui  | 2025-10-15 15:03:57.160 |   File "/usr/local/lib/python3.10/dist-packages/extension_kokoro_tts_api/api.py", line 476, in create_speech
tts-webui  | 2025-10-15 15:03:57.160 |     audio_data = generate_speech(request)
tts-webui  | 2025-10-15 15:03:57.160 |   File "/usr/local/lib/python3.10/dist-packages/extension_kokoro_tts_api/api.py", line 136, in generate_speech
tts-webui  | 2025-10-15 15:03:57.160 |     result = kokoro_adapter(
tts-webui  | 2025-10-15 15:03:57.160 |   File "/usr/local/lib/python3.10/dist-packages/extension_kokoro_tts_api/api.py", line 232, in wrapper
tts-webui  | 2025-10-15 15:03:57.160 |     return func(*args, **kwargs)
tts-webui  | 2025-10-15 15:03:57.160 |   File "/usr/local/lib/python3.10/dist-packages/extension_kokoro_tts_api/api.py", line 242, in kokoro_adapter
tts-webui  | 2025-10-15 15:03:57.160 |     raise ImportError(
tts-webui  | 2025-10-15 15:03:57.160 | ImportError: Kokoro extension is not installed. Please install it to use Kokoro TTS features.
tts-webui  | 2025-10-15 15:03:57.160 | Using custom TTS parameters: {'use_gpu': True, 'rvc_params': {'pitch_up_key': '0', 'index_path': 'CaitArcane\\added_IVF65_Flat_nprobe_1_CaitArcane_v2', 'pitch_collection_method': 'harvest', 'model_path': 'CaitArcane\\CaitArcane', 'index_rate': 0.66, 'filter_radius': 3, 'resample_sr': 0, 'rms_mix_rate': 1, 'protect': 0.33}}
tts-webui  | 2025-10-15 15:03:57.160 | Using kokoro with params: ('Today is a wonderful day to build something people love!', {'voice': 'af_heart', 'speed': 1.0, 'model_name': 'hexgrad/Kokoro-82M', 'use_gpu': True, 'rvc_params': {'pitch_up_key': '0', 'index_path': 'CaitArcane\\added_IVF65_Flat_nprobe_1_CaitArcane_v2', 'pitch_collection_method': 'harvest', 'model_path': 'CaitArcane\\CaitArcane', 'index_rate': 0.66, 'filter_radius': 3, 'resample_sr': 0, 'rms_mix_rate': 1, 'protect': 0.33}}), {}
tts-webui  | 2025-10-15 15:03:57.160 | Error generating speech: Kokoro extension is not installed. Please install it to use Kokoro TTS features.
tts-webui  | 2025-10-15 15:03:57.160 | INFO:     127.0.0.1:54188 - "POST /v1/audio/speech HTTP/1.1" 500 Internal Server Error
tts-webui  | 2025-10-15 15:03:57.589 | Traceback (most recent call last):
tts-webui  | 2025-10-15 15:03:57.589 |   File "/usr/local/lib/python3.10/dist-packages/extension_kokoro_tts_api/api.py", line 240, in kokoro_adapter
tts-webui  | 2025-10-15 15:03:57.589 |     from extension_kokoro.main import tts
tts-webui  | 2025-10-15 15:03:57.589 | ModuleNotFoundError: No module named 'extension_kokoro'
tts-webui  | 2025-10-15 15:03:57.589 | Using custom TTS parameters: {'use_gpu': True, 'rvc_params': {'pitch_up_key': '0', 'index_path': 'CaitArcane\\added_IVF65_Flat_nprobe_1_CaitArcane_v2', 'pitch_collection_method': 'harvest', 'model_path': 'CaitArcane\\CaitArcane', 'index_rate': 0.66, 'filter_radius': 3, 'resample_sr': 0, 'rms_mix_rate': 1, 'protect': 0.33}}
tts-webui  | 2025-10-15 15:03:57.589 | Using kokoro with params: ('Today is a wonderful day to build something people love!', {'voice': 'af_heart', 'speed': 1.0, 'model_name': 'hexgrad/Kokoro-82M', 'use_gpu': True, 'rvc_params': {'pitch_up_key': '0', 'index_path': 'CaitArcane\\added_IVF65_Flat_nprobe_1_CaitArcane_v2', 'pitch_collection_method': 'harvest', 'model_path': 'CaitArcane\\CaitArcane', 'index_rate': 0.66, 'filter_radius': 3, 'resample_sr': 0, 'rms_mix_rate': 1, 'protect': 0.33}}), {}
tts-webui  | 2025-10-15 15:03:57.589 | Error generating speech: Kokoro extension is not installed. Please install it to use Kokoro TTS features.
tts-webui  | 2025-10-15 15:03:57.589 | INFO:     127.0.0.1:54196 - "POST /v1/audio/speech HTTP/1.1" 500 Internal Server Error
tts-webui  | 2025-10-15 15:03:57.589 | 
tts-webui  | 2025-10-15 15:03:57.589 | During handling of the above exception, another exception occurred:
tts-webui  | 2025-10-15 15:03:57.589 | 
tts-webui  | 2025-10-15 15:03:57.589 | Traceback (most recent call last):
tts-webui  | 2025-10-15 15:03:57.589 |   File "/usr/local/lib/python3.10/dist-packages/extension_kokoro_tts_api/api.py", line 476, in create_speech
tts-webui  | 2025-10-15 15:03:57.589 |     audio_data = generate_speech(request)
tts-webui  | 2025-10-15 15:03:57.589 |   File "/usr/local/lib/python3.10/dist-packages/extension_kokoro_tts_api/api.py", line 136, in generate_speech
tts-webui  | 2025-10-15 15:03:57.589 |     result = kokoro_adapter(
tts-webui  | 2025-10-15 15:03:57.589 |   File "/usr/local/lib/python3.10/dist-packages/extension_kokoro_tts_api/api.py", line 232, in wrapper
tts-webui  | 2025-10-15 15:03:57.589 |     return func(*args, **kwargs)
tts-webui  | 2025-10-15 15:03:57.589 |   File "/usr/local/lib/python3.10/dist-packages/extension_kokoro_tts_api/api.py", line 242, in kokoro_adapter
tts-webui  | 2025-10-15 15:03:57.589 |     raise ImportError(
tts-webui  | 2025-10-15 15:03:57.589 | ImportError: Kokoro extension is not installed. Please install it to use Kokoro TTS features.
tts-webui  | 2025-10-15 15:03:58.543 | Using custom TTS parameters: {'use_gpu': True, 'rvc_params': {'pitch_up_key': '0', 'index_path': 'CaitArcane\\added_IVF65_Flat_nprobe_1_CaitArcane_v2', 'pitch_collection_method': 'harvest', 'model_path': 'CaitArcane\\CaitArcane', 'index_rate': 0.66, 'filter_radius': 3, 'resample_sr': 0, 'rms_mix_rate': 1, 'protect': 0.33}}
tts-webui  | 2025-10-15 15:03:58.543 | Using kokoro with params: ('Today is a wonderful day to build something people love!', {'voice': 'af_heart', 'speed': 1.0, 'model_name': 'hexgrad/Kokoro-82M', 'use_gpu': True, 'rvc_params': {'pitch_up_key': '0', 'index_path': 'CaitArcane\\added_IVF65_Flat_nprobe_1_CaitArcane_v2', 'pitch_collection_method': 'harvest', 'model_path': 'CaitArcane\\CaitArcane', 'index_rate': 0.66, 'filter_radius': 3, 'resample_sr': 0, 'rms_mix_rate': 1, 'protect': 0.33}}), {}
tts-webui  | 2025-10-15 15:03:58.543 | Error generating speech: Kokoro extension is not installed. Please install it to use Kokoro TTS features.
tts-webui  | 2025-10-15 15:03:58.543 | INFO:     127.0.0.1:54204 - "POST /v1/audio/speech HTTP/1.1" 500 Internal Server Error
tts-webui  | 2025-10-15 15:03:58.543 | Traceback (most recent call last):
tts-webui  | 2025-10-15 15:03:58.543 |   File "/usr/local/lib/python3.10/dist-packages/extension_kokoro_tts_api/api.py", line 240, in kokoro_adapter
tts-webui  | 2025-10-15 15:03:58.543 |     from extension_kokoro.main import tts
tts-webui  | 2025-10-15 15:03:58.543 | ModuleNotFoundError: No module named 'extension_kokoro'
tts-webui  | 2025-10-15 15:03:58.543 | 
tts-webui  | 2025-10-15 15:03:58.543 | During handling of the above exception, another exception occurred:
tts-webui  | 2025-10-15 15:03:58.543 | 
tts-webui  | 2025-10-15 15:03:58.543 | Traceback (most recent call last):
tts-webui  | 2025-10-15 15:03:58.543 |   File "/usr/local/lib/python3.10/dist-packages/extension_kokoro_tts_api/api.py", line 476, in create_speech
tts-webui  | 2025-10-15 15:03:58.543 |     audio_data = generate_speech(request)
tts-webui  | 2025-10-15 15:03:58.543 |   File "/usr/local/lib/python3.10/dist-packages/extension_kokoro_tts_api/api.py", line 136, in generate_speech
tts-webui  | 2025-10-15 15:03:58.543 |     result = kokoro_adapter(
tts-webui  | 2025-10-15 15:03:58.543 |   File "/usr/local/lib/python3.10/dist-packages/extension_kokoro_tts_api/api.py", line 232, in wrapper
tts-webui  | 2025-10-15 15:03:58.543 |     return func(*args, **kwargs)
tts-webui  | 2025-10-15 15:03:58.543 |   File "/usr/local/lib/python3.10/dist-packages/extension_kokoro_tts_api/api.py", line 242, in kokoro_adapter
tts-webui  | 2025-10-15 15:03:58.543 |     raise ImportError(
tts-webui  | 2025-10-15 15:03:58.543 | ImportError: Kokoro extension is not installed. Please install it to use Kokoro TTS features.
tts-webui  | 2025-10-15 15:03:58.546 | Traceback (most recent call last):
tts-webui  | 2025-10-15 15:03:58.546 |   File "/usr/local/lib/python3.10/dist-packages/gradio/queueing.py", line 624, in process_events
tts-webui  | 2025-10-15 15:03:58.546 |     response = await route_utils.call_process_api(
tts-webui  | 2025-10-15 15:03:58.546 |   File "/usr/local/lib/python3.10/dist-packages/gradio/route_utils.py", line 323, in call_process_api
tts-webui  | 2025-10-15 15:03:58.546 |     output = await app.get_blocks().process_api(
tts-webui  | 2025-10-15 15:03:58.546 |   File "/usr/local/lib/python3.10/dist-packages/gradio/blocks.py", line 2015, in process_api
tts-webui  | 2025-10-15 15:03:58.546 |     result = await self.call_function(
tts-webui  | 2025-10-15 15:03:58.546 |   File "/usr/local/lib/python3.10/dist-packages/gradio/blocks.py", line 1562, in call_function
tts-webui  | 2025-10-15 15:03:58.546 |     prediction = await anyio.to_thread.run_sync(  # type: ignore
tts-webui  | 2025-10-15 15:03:58.546 |   File "/usr/local/lib/python3.10/dist-packages/anyio/to_thread.py", line 56, in run_sync
tts-webui  | 2025-10-15 15:03:58.546 |     return await get_async_backend().run_sync_in_worker_thread(
tts-webui  | 2025-10-15 15:03:58.546 |   File "/usr/local/lib/python3.10/dist-packages/anyio/_backends/_asyncio.py", line 2476, in run_sync_in_worker_thread
tts-webui  | 2025-10-15 15:03:58.546 |     return await future
tts-webui  | 2025-10-15 15:03:58.546 |   File "/usr/local/lib/python3.10/dist-packages/anyio/_backends/_asyncio.py", line 967, in run
tts-webui  | 2025-10-15 15:03:58.546 |     result = context.run(func, *args)
tts-webui  | 2025-10-15 15:03:58.546 |   File "/usr/local/lib/python3.10/dist-packages/gradio/utils.py", line 865, in wrapper
tts-webui  | 2025-10-15 15:03:58.546 |     response = f(*args, **kwargs)
tts-webui  | 2025-10-15 15:03:58.546 |   File "/usr/local/lib/python3.10/dist-packages/extension_kokoro_tts_api/main.py", line 73, in test_api_with_open_ai
tts-webui  | 2025-10-15 15:03:58.546 |     with client.audio.speech.with_streaming_response.create(
tts-webui  | 2025-10-15 15:03:58.546 |   File "/usr/local/lib/python3.10/dist-packages/openai/_response.py", line 626, in __enter__
tts-webui  | 2025-10-15 15:03:58.546 |     self.__response = self._request_func()
tts-webui  | 2025-10-15 15:03:58.546 |   File "/usr/local/lib/python3.10/dist-packages/openai/resources/audio/speech.py", line 101, in create
tts-webui  | 2025-10-15 15:03:58.546 |     return self._post(
tts-webui  | 2025-10-15 15:03:58.546 |   File "/usr/local/lib/python3.10/dist-packages/openai/_base_client.py", line 1259, in post
tts-webui  | 2025-10-15 15:03:58.546 |     return cast(ResponseT, self.request(cast_to, opts, stream=stream, stream_cls=stream_cls))
tts-webui  | 2025-10-15 15:03:58.546 |   File "/usr/local/lib/python3.10/dist-packages/openai/_base_client.py", line 1047, in request
tts-webui  | 2025-10-15 15:03:58.546 |     raise self._make_status_error_from_response(err.response) from None
tts-webui  | 2025-10-15 15:03:58.546 | openai.InternalServerError: Error code: 500 - {'detail': 'Kokoro extension is not installed. Please install it to use Kokoro TTS features.'}
tts-webui  | 2025-10-15 15:04:12.504 | INFO:     172.21.0.1:34930 - "POST /gradio_api/queue/join HTTP/1.1" 200 OK
```

## No cuda detected on tts-webui container

- Need to ensure all containers can access GPU

```
tts-webui  | 2025-10-15 15:04:28.464 | 
tts-webui  | 2025-10-15 15:04:28.465 | ==========
tts-webui  | 2025-10-15 15:04:28.465 | == CUDA ==
tts-webui  | 2025-10-15 15:04:28.465 | ==========
tts-webui  | 2025-10-15 15:04:28.469 | 
tts-webui  | 2025-10-15 15:04:28.469 | CUDA Version 12.8.0
tts-webui  | 2025-10-15 15:04:28.470 | 
tts-webui  | 2025-10-15 15:04:28.470 | Container image Copyright (c) 2016-2023, NVIDIA CORPORATION & AFFILIATES. All rights reserved.
tts-webui  | 2025-10-15 15:04:28.470 | 
tts-webui  | 2025-10-15 15:04:28.470 | This container image and its contents are governed by the NVIDIA Deep Learning Container License.
tts-webui  | 2025-10-15 15:04:28.470 | By pulling and using the container, you accept the terms and conditions of this license:
tts-webui  | 2025-10-15 15:04:28.470 | https://developer.nvidia.com/ngc/nvidia-deep-learning-container-license
tts-webui  | 2025-10-15 15:04:28.470 | 
tts-webui  | 2025-10-15 15:04:28.470 | A copy of this license is made available in this container at /NGC-DL-CONTAINER-LICENSE for your convenience.
tts-webui  | 2025-10-15 15:04:28.479 | 
tts-webui  | 2025-10-15 15:04:28.479 | WARNING: The NVIDIA Driver was not detected.  GPU functionality will not be available.
tts-webui  | 2025-10-15 15:04:28.479 |    Use the NVIDIA Container Toolkit to start this container with GPU support; see
tts-webui  | 2025-10-15 15:04:28.479 |    https://docs.nvidia.com/datacenter/cloud-native/ .
tts-webui  | 2025-10-15 15:04:28.479 | 
```


## Bark Voices exception

Bark Clone extension is listed as optional but throws exception if it's not installed

```
tts-webui  | 2025-10-15 15:04:32.702 | Loading Bark Voice Clone......................Failed to load Bark Voice Clone tab. Please check your configuration.
tts-webui  | 2025-10-15 15:04:32.702 | Error: No module named 'bark'
tts-webui  | 2025-10-15 15:04:32.702 | Stacktrace: Traceback (most recent call last):
tts-webui  | 2025-10-15 15:04:32.702 |   File "/app/tts-webui/tts_webui/extensions_loader/interface_extensions.py", line 52, in _handle_package
tts-webui  | 2025-10-15 15:04:32.702 |     module = importlib.import_module(f"{package_name}.main")
tts-webui  | 2025-10-15 15:04:32.702 |   File "/usr/lib/python3.10/importlib/__init__.py", line 126, in import_module
tts-webui  | 2025-10-15 15:04:32.702 |     return _bootstrap._gcd_import(name[level:], package, level)
tts-webui  | 2025-10-15 15:04:32.702 |   File "<frozen importlib._bootstrap>", line 1050, in _gcd_import
tts-webui  | 2025-10-15 15:04:32.702 |   File "<frozen importlib._bootstrap>", line 1027, in _find_and_load
tts-webui  | 2025-10-15 15:04:32.702 |   File "<frozen importlib._bootstrap>", line 1006, in _find_and_load_unlocked
tts-webui  | 2025-10-15 15:04:32.702 |   File "<frozen importlib._bootstrap>", line 688, in _load_unlocked
tts-webui  | 2025-10-15 15:04:32.702 |   File "<frozen importlib._bootstrap_external>", line 883, in exec_module
tts-webui  | 2025-10-15 15:04:32.702 |   File "<frozen importlib._bootstrap>", line 241, in _call_with_frames_removed
tts-webui  | 2025-10-15 15:04:32.702 |   File "/usr/local/lib/python3.10/dist-packages/extension_bark_voice_clone/main.py", line 7, in <module>
tts-webui  | 2025-10-15 15:04:32.702 |     from bark.generation import load_codec_model
tts-webui  | 2025-10-15 15:04:32.702 | ModuleNotFoundError: No module named 'bark'
tts-webui  | 2025-10-15 15:04:32.702 | 
tts-webui  | 2025-10-15 15:04:32.702 |    .01 seconds.
tts-webui  | 2025-10-15 15:04:32.702 | Loading Model Location Settings...............   .00 seconds.
tts-webui  | 2025-10-15 15:04:32.702 | Loading GPU Info..............................   .00 seconds.
tts-webui  | 2025-10-15 15:04:32.702 | Loading Installed Packages....................   .00 seconds.
tts-webui  | 2025-10-15 15:04:32.702 | 
tts-webui  | 2025-10-15 15:04:32.702 | 
tts-webui  | 2025-10-15 15:04:32.702 | 
```		
## Bark Extension Exception (harmless)

```
tts-webui  | 2025-10-15 14:52:28.926 | Loading Bark Voice Clone......................Failed to load Bark Voice Clone tab. Please check your configuration.
tts-webui  | 2025-10-15 14:52:28.926 | Error: No module named 'bark'
tts-webui  | 2025-10-15 14:52:28.926 | Stacktrace: Traceback (most recent call last):
tts-webui  | 2025-10-15 14:52:28.926 |   File "/app/tts-webui/tts_webui/extensions_loader/interface_extensions.py", line 52, in _handle_package
tts-webui  | 2025-10-15 14:52:28.926 |     module = importlib.import_module(f"{package_name}.main")
tts-webui  | 2025-10-15 14:52:28.926 |   File "/usr/lib/python3.10/importlib/__init__.py", line 126, in import_module
tts-webui  | 2025-10-15 14:52:28.926 |     return _bootstrap._gcd_import(name[level:], package, level)
tts-webui  | 2025-10-15 14:52:28.926 |   File "<frozen importlib._bootstrap>", line 1050, in _gcd_import
tts-webui  | 2025-10-15 14:52:28.926 |   File "<frozen importlib._bootstrap>", line 1027, in _find_and_load
tts-webui  | 2025-10-15 14:52:28.926 |   File "<frozen importlib._bootstrap>", line 1006, in _find_and_load_unlocked
tts-webui  | 2025-10-15 14:52:28.926 |   File "<frozen importlib._bootstrap>", line 688, in _load_unlocked
tts-webui  | 2025-10-15 14:52:28.926 |   File "<frozen importlib._bootstrap_external>", line 883, in exec_module
tts-webui  | 2025-10-15 14:52:28.926 |   File "<frozen importlib._bootstrap>", line 241, in _call_with_frames_removed
tts-webui  | 2025-10-15 14:52:28.926 |   File "/usr/local/lib/python3.10/dist-packages/extension_bark_voice_clone/main.py", line 7, in <module>
tts-webui  | 2025-10-15 14:52:28.926 |     from bark.generation import load_codec_model
tts-webui  | 2025-10-15 14:52:28.926 | ModuleNotFoundError: No module named 'bark'
```