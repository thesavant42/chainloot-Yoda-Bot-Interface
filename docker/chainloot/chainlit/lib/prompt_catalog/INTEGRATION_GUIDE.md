# Prompt Catalog Integration Guide

## 📋 Quick Setup Steps

### 1. Initialize Database Schema

First, set up the database tables in your existing PostgreSQL:

```powershell
# In PowerShell, from the prompt_catalog directory
cd "c:\Users\jbras\GitHub\chainloot-Yoda-Bot-Interface\docs\IN_PROGRESS_TASKS\prompt_catalog"
powershell -ExecutionPolicy Bypass -File init_database.ps1
```

### 2. Install Dependencies

Add these to your Chainlit requirements:

```bash
# Add to docker/chainloot/chainlit/requirements-chainlit.txt
toml==0.10.2
asyncpg==0.30.0
```

### 3. Minimal App Integration

Add **just 2 lines** to your existing `docker/chainloot/chainlit/app.py`:

```python
# Add this import at the top
from lib.prompt_catalog import prompt_catalog

# Modify your existing @cl.on_message handler
@cl.on_message
async def main(message: cl.Message):
    # Add this one line at the start of your handler
    if await prompt_catalog.handle_message(message):
        return
    
    # Your existing logic continues unchanged...
    # (everything else stays exactly the same)
```

### 4. Optional: Enhanced System Prompt Support

If you want to use loaded prompts as system prompts, add this helper:

```python
# In your message processing logic, replace hardcoded system prompts with:
system_prompt = await prompt_catalog.get_active_system_prompt() or "your default system prompt"
```

## 🎯 Usage

Once integrated, users can use these commands in chat:

- `/prompts list` - Show available prompts  
- `/prompts load 1` - Load prompt by ID
- `/prompts info 1` - Show prompt details
- `/prompts active` - Show current prompt
- `/prompts clear` - Clear active prompt

## 📁 What Gets Created

The integration creates this structure in your existing app:

```
docker/chainloot/chainlit/lib/prompt_catalog/
├── __init__.py           # Main module (import this)
├── prompt_manager.py     # Core prompt logic  
├── database.py          # Database operations
```

## 🗄️ Database Schema

The system adds these tables to your existing `chainloot` database:

- `prompts` - Main prompt templates
- `prompt_variables` - Variable definitions  
- `model_adaptations` - Model-specific settings
- `prompt_usage_history` - Usage tracking
- `model_metadata` - Model information

## 🔧 Configuration

The system uses your existing environment:

- **Database**: Uses `DATABASE_URL` from your `localstack.env`
- **Session**: Integrates with Chainlit's `cl.user_session`
- **Docker**: Runs in your existing Chainlit container

## 🧪 Testing

1. **Start your existing setup**:
   ```bash
   cd docker/chainloot
   docker-compose up -d
   ```

2. **Test prompt commands**:
   - Open your Chainlit app (http://localhost:8100)
   - Type: `/prompts list`
   - Should show available prompts or empty list

3. **Upload sample prompts** (manual for now):
   - Copy TOML files to database using SQL INSERT
   - Or build upload functionality later

## ⚠️ Important Notes

- **Minimal Impact**: Only 2 lines added to your main app
- **Backward Compatible**: Existing functionality unchanged  
- **Modular Design**: Can be disabled by removing the import
- **Session Isolated**: Each user gets their own prompt state
- **Database Safe**: Uses existing PostgreSQL, no conflicts

## 🐛 Troubleshooting

**Import errors**: Install missing dependencies in Docker container
**Database errors**: Ensure schema is initialized  
**No prompts shown**: Database tables empty (expected initially)

This integration is designed to be as non-invasive as possible while providing powerful prompt management capabilities!