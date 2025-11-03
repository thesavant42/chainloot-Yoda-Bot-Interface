# Research Notes - SmolLM3 Model and README Analysis

## SmolLM3-3B-128K-GGUF Model Research

### Model Details from Hugging Face
- **Model**: SmolLM3-3B-128K-GGUF (from unsloth on Hugging Face)
- **Chat Template Type**: Uses Jinja-based chat templates with ChatML format
- **Context Length**: 128K tokens
- **Architecture**: 3B parameter model optimized for reasoning tasks
- **Reasoning Support**: Built-in support for reasoning toggles via `/think` and `/no_think` commands
- **Template Format**: Supports `<think>...</think>` tags for internal reasoning
- **MCP Integration**: Compatible with Model Context Protocol tools

### Key Technical Findings
1. **Jinja Templates**: The model uses Jinja templating system for chat formatting
2. **ChatML Format**: Standard ChatML structure for conversation handling
3. **EOS Token Support**: Can be configured with custom end-of-string tokens
4. **Reasoning Mode**: Designed to show/hide thinking process based on configuration

## README.md Analysis

### What You Communicated Well
Your README clearly explains:

1. **The Core Problem**: Static configuration in `bot_config.py` requires container restarts
2. **Specific Pain Points**: 
   - Manual editing of hardcoded prompts
   - `<think>` tags causing TTS issues
   - Slow iteration during testing
3. **Your Vision**: Dynamic, database-driven prompt catalog system
4. **Current Setup**: Chainlit + SmolLM3 + Docker + PostgreSQL + S3 (Chainlit official datalayer)

### Your Requirements (From README)
- Runtime prompt editing without restarts
- Database-backed prompt storage  
- Multiple personas with flexible templates
- Proper reasoning toggle control
- Integration with existing MCP tools

### Technical Context from Your Codebase
- **Current Structure**: `bot_config.py` with `PROFILE_DEFAULTS` dictionary
- **Three Personas**: Yoda, AI Assistant, Tony Stark
- **Infrastructure**: Docker containerization with persistent data layer
- **Integration**: MCP tools already working

## Chainlit Framework Research

### Data Persistence Options
- **Official Data Layer**: PostgreSQL + asyncpg (you already have PostgreSQL)
- **User Sessions**: Built-in session management for runtime configuration
- **Chat Profiles**: Dynamic profile system that can load from database
- **Configuration Overrides**: Can modify settings per profile at runtime

### Key Chainlit Features for Your Use Case
1. **`@cl.set_chat_profiles`**: Can dynamically load profiles from database
2. **User Session Storage**: Can store prompt configuration per session
3. **Runtime Updates**: Configuration can be changed without restarts
4. **Official Data Layer**: Works with your existing PostgreSQL setup

## Bottom Line Assessment

**Your README communicates the problem very clearly.** You have a well-defined issue (static config) and a clear vision (dynamic database-driven system). 

**Technical Feasibility**: This is definitely achievable with Chainlit's built-in features + your existing infrastructure.

**Next Steps** (if you want them): The core would be moving your `PROFILE_DEFAULTS` from hardcoded dictionary to database tables, then using Chainlit's dynamic profile loading to read from there instead.

Q: What feature do you mean, Chainlits dynamic profile loading? Can you provide a link?
A: By "dynamic profile loading" I'm referring to Chainlit's `@cl.set_chat_profiles` decorator function that allows you to programmatically generate chat profiles at runtime instead of having them hardcoded. This function can return different chat profiles based on conditions like user authentication, database queries, or other dynamic factors. Instead of having static profiles defined in your code, you can load profile configurations from a database, API, or other data source when the chat session starts. This is what would allow you to move your `PROFILE_DEFAULTS` from hardcoded dictionaries to database-driven configuration that can be updated without restarting the application.

Sources: 
- Chainlit Chat Profiles API Reference: https://github.com/Chainlit/docs/blob/main/api-reference/chat-profiles.mdx
- Chainlit Advanced Features - Chat Profiles: https://github.com/Chainlit/docs/blob/main/advanced-features/chat-profiles.mdx


---

*These are just my research findings and analysis - no implementation assumptions made.*