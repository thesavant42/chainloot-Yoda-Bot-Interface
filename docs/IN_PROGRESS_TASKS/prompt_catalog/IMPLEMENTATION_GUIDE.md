# Dynamic Prompt Catalog System - Implementation Guide

## Executive Summary

This document provides a comprehensive implementation guide for transitioning from the current static prompt configuration system to a dynamic, database-driven prompt catalog system for the Chainlit-based Yoda Bot Interface.

## Table of Contents

1. [Current System Analysis](#current-system-analysis)
2. [Problem Statement](#problem-statement)
3. [Proposed Solution Architecture](#proposed-solution-architecture)
4. [Technical Implementation](#technical-implementation)
5. [Database Schema](#database-schema)
6. [Code Implementation](#code-implementation)
7. [Migration Strategy](#migration-strategy)
8. [Testing Strategy](#testing-strategy)
9. [Deployment Considerations](#deployment-considerations)

---

## Current System Analysis

### Existing Architecture
- **Framework**: Chainlit chat interface with SmolLM3-3B-128K-GGUF model
- **Configuration**: Static `bot_config.py` with hardcoded PROFILE_DEFAULTS
- **Personas**: Three predefined profiles (Yoda, AI Assistant, Tony Stark)
- **Infrastructure**: Docker containerization with PostgreSQL + LocalStack S3
- **Integration**: MCP (Model Context Protocol) tools support

### Current bot_config.py Structure
```python
PROFILE_DEFAULTS = {
    "Yoda": {
        "system_prompt": "You are Yoda, the wise Jedi Master...",
        "default_voice": "Yoda_voice"
    },
    "AI": {
        "system_prompt": "You are a helpful AI assistant...", 
        "default_voice": "default_voice"
    },
    "Stark": {
        "system_prompt": "You are Tony Stark...",
        "default_voice": "stark_voice"
    }
}
```

---

## Problem Statement

### Critical Issues Identified

1. **Container Restart Requirement**
   - Any prompt modification requires container restart
   - Disrupts active user sessions
   - Slows development and testing cycles

2. **EOS Token Recognition Failure**
   - `<think>` tags not recognized as end-of-string tokens
   - Causes text-to-speech system to vocalize reasoning content
   - Breaks intended reasoning toggle functionality

3. **Manual Configuration Overhead**
   - Editing hardcoded dictionaries is error-prone
   - No version control for prompt changes
   - Difficult to A/B test different prompts

4. **Scalability Limitations**
   - Static configuration doesn't scale with user growth
   - No per-user or per-session customization capability
   - Limited prompt template flexibility

---

## Proposed Solution Architecture

### Core Components

```mermaid
graph TB
    A[Chainlit Interface] --> B[Dynamic Prompt Manager]
    B --> C[PostgreSQL Database]
    B --> D[Redis Cache Layer]
    C --> E[prompt_templates table]
    C --> F[prompt_history table]
    A --> G[User Session Manager]
    G --> H[Profile Configuration]
    I[Admin Interface] --> B
```

### Key Features

1. **Runtime Configuration Updates**: Modify prompts without service interruption
2. **Database-Driven Persistence**: Store prompt templates in PostgreSQL
3. **Intelligent Caching**: Redis layer for performance optimization
4. **Version Control**: Track prompt template changes and enable rollbacks
5. **EOS Token Management**: Proper configuration of reasoning toggles
6. **Admin Interface**: Web-based prompt template management

---

## Technical Implementation

### Technology Stack

- **Backend**: Chainlit with official data layer (PostgreSQL + asyncpg)
- **Database**: PostgreSQL for prompt templates and configuration
- **Caching**: Redis for performance optimization
- **Storage**: LocalStack S3 for file persistence
- **Integration**: Existing MCP tools and SmolLM3 model

### Architecture Principles

1. **Backward Compatibility**: Maintain existing chat profile functionality
2. **Performance**: Sub-100ms prompt retrieval with caching
3. **Reliability**: Graceful fallback to default prompts
4. **Maintainability**: Clear separation of concerns
5. **Extensibility**: Easy addition of new profile types

---

## Database Schema

### Primary Tables

```sql
-- Core prompt template storage
CREATE TABLE prompt_templates (
    id SERIAL PRIMARY KEY,
    profile_name VARCHAR(50) UNIQUE NOT NULL,
    display_name VARCHAR(100) NOT NULL,
    description TEXT,
    system_prompt TEXT NOT NULL,
    reasoning_enabled BOOLEAN DEFAULT true,
    default_voice VARCHAR(50),
    eos_tokens JSONB DEFAULT '["<think>", "</think>"]',
    icon_url VARCHAR(255),
    is_default BOOLEAN DEFAULT false,
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    created_by VARCHAR(100),
    version INTEGER DEFAULT 1
);

-- Prompt template version history
CREATE TABLE prompt_history (
    id SERIAL PRIMARY KEY,
    template_id INTEGER REFERENCES prompt_templates(id),
    version INTEGER NOT NULL,
    system_prompt TEXT NOT NULL,
    reasoning_enabled BOOLEAN,
    eos_tokens JSONB,
    change_reason TEXT,
    changed_by VARCHAR(100),
    changed_at TIMESTAMP DEFAULT NOW()
);

-- User-specific prompt overrides (future enhancement)
CREATE TABLE user_prompt_overrides (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(100) NOT NULL,
    template_id INTEGER REFERENCES prompt_templates(id),
    custom_prompt TEXT,
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Prompt performance analytics (future enhancement)
CREATE TABLE prompt_analytics (
    id SERIAL PRIMARY KEY,
    template_id INTEGER REFERENCES prompt_templates(id),
    session_id VARCHAR(100),
    message_count INTEGER,
    avg_response_time FLOAT,
    user_satisfaction INTEGER CHECK (user_satisfaction >= 1 AND user_satisfaction <= 5),
    recorded_at TIMESTAMP DEFAULT NOW()
);
```

### Initial Data Migration

```sql
-- Insert existing profiles from bot_config.py
INSERT INTO prompt_templates (
    profile_name, display_name, description, system_prompt, 
    reasoning_enabled, default_voice, is_default, active
) VALUES
(
    'Yoda', 
    'Yoda - Wise Jedi Master', 
    'Wise and ancient Jedi Master with unique speech patterns and deep Force knowledge',
    'You are Yoda, the wise and ancient Jedi Master. Speak with Yoda''s distinctive syntax and vocabulary. Share wisdom about the Force, patience, and the path of the Jedi. Keep responses helpful but maintain the character''s unique speaking style.',
    true, 
    'Yoda_voice', 
    true, 
    true
),
(
    'AI', 
    'AI Assistant', 
    'Helpful AI assistant for general queries and technical support',
    'You are a helpful, knowledgeable, and friendly AI assistant. Provide clear, accurate, and useful responses to user questions. Be concise but thorough, and always aim to be helpful.',
    true, 
    'default_voice', 
    false, 
    true
),
(
    'Stark', 
    'Tony Stark - Iron Man', 
    'Genius billionaire playboy philanthropist with cutting-edge technology insights',
    'You are Tony Stark, also known as Iron Man. You''re a genius inventor, billionaire industrialist, and superhero. Respond with confidence, wit, and technical expertise. Reference your advanced technology and Stark Industries innovations when relevant.',
    true, 
    'stark_voice', 
    false, 
    true
);
```

---

## Code Implementation

### 1. Dynamic Prompt Manager

```python
# lib/dynamic_prompt_manager.py
import asyncio
import asyncpg
import redis
import json
from typing import Dict, Optional, List
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class DynamicPromptManager:
    def __init__(self, database_url: str, redis_url: str = None):
        self.db_url = database_url
        self.redis_client = redis.from_url(redis_url) if redis_url else None
        self._cache = {}
        self.cache_ttl = 300  # 5 minutes
    
    async def get_prompt_template(self, profile_name: str) -> Optional[Dict]:
        """
        Retrieve prompt template from cache or database
        
        Args:
            profile_name: Name of the chat profile
            
        Returns:
            Dict containing prompt template configuration or None
        """
        # Try cache first
        cache_key = f"prompt_template:{profile_name}"
        
        if self.redis_client:
            try:
                cached_data = self.redis_client.get(cache_key)
                if cached_data:
                    return json.loads(cached_data)
            except Exception as e:
                logger.warning(f"Redis cache error: {e}")
        
        # Check in-memory cache
        if profile_name in self._cache:
            cache_entry = self._cache[profile_name]
            if datetime.now() - cache_entry['timestamp'] < timedelta(seconds=self.cache_ttl):
                return cache_entry['data']
        
        # Query database
        try:
            async with asyncpg.connect(self.db_url) as conn:
                result = await conn.fetchrow(
                    """SELECT * FROM prompt_templates 
                       WHERE profile_name = $1 AND active = true""",
                    profile_name
                )
                
                if result:
                    template_data = dict(result)
                    
                    # Update caches
                    self._cache[profile_name] = {
                        'data': template_data,
                        'timestamp': datetime.now()
                    }
                    
                    if self.redis_client:
                        try:
                            self.redis_client.setex(
                                cache_key, 
                                self.cache_ttl, 
                                json.dumps(template_data, default=str)
                            )
                        except Exception as e:
                            logger.warning(f"Redis set error: {e}")
                    
                    return template_data
        except Exception as e:
            logger.error(f"Database error retrieving prompt template: {e}")
            return None
        
        return None
    
    async def update_prompt_template(
        self, 
        profile_name: str, 
        template_data: Dict, 
        changed_by: str = "system",
        change_reason: str = None
    ) -> bool:
        """
        Update prompt template and invalidate caches
        
        Args:
            profile_name: Name of the profile to update
            template_data: New template configuration
            changed_by: User who made the change
            change_reason: Reason for the change
            
        Returns:
            bool: Success status
        """
        try:
            async with asyncpg.connect(self.db_url) as conn:
                # Begin transaction
                async with conn.transaction():
                    # Get current version for history
                    current = await conn.fetchrow(
                        "SELECT * FROM prompt_templates WHERE profile_name = $1",
                        profile_name
                    )
                    
                    if current:
                        # Save to history
                        await conn.execute(
                            """INSERT INTO prompt_history 
                               (template_id, version, system_prompt, reasoning_enabled, 
                                eos_tokens, change_reason, changed_by)
                               VALUES ($1, $2, $3, $4, $5, $6, $7)""",
                            current['id'], current['version'], current['system_prompt'],
                            current['reasoning_enabled'], current['eos_tokens'],
                            change_reason, changed_by
                        )
                        
                        # Update template with new version
                        await conn.execute(
                            """UPDATE prompt_templates SET 
                               system_prompt = $2, reasoning_enabled = $3, 
                               default_voice = $4, eos_tokens = $5, 
                               updated_at = NOW(), version = version + 1
                               WHERE profile_name = $1""",
                            profile_name, template_data['system_prompt'],
                            template_data.get('reasoning_enabled', True),
                            template_data.get('default_voice', 'default_voice'),
                            json.dumps(template_data.get('eos_tokens', ["<think>", "</think>"]))
                        )
                    else:
                        # Insert new template
                        await conn.execute(
                            """INSERT INTO prompt_templates 
                               (profile_name, display_name, description, system_prompt, 
                                reasoning_enabled, default_voice, eos_tokens, created_by)
                               VALUES ($1, $2, $3, $4, $5, $6, $7, $8)""",
                            profile_name, template_data.get('display_name', profile_name),
                            template_data.get('description', ''), template_data['system_prompt'],
                            template_data.get('reasoning_enabled', True),
                            template_data.get('default_voice', 'default_voice'),
                            json.dumps(template_data.get('eos_tokens', ["<think>", "</think>"])),
                            changed_by
                        )
            
            # Invalidate caches
            await self._invalidate_cache(profile_name)
            
            logger.info(f"Updated prompt template for {profile_name} by {changed_by}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating prompt template: {e}")
            return False
    
    async def get_all_active_profiles(self) -> List[Dict]:
        """Get all active chat profiles for profile selection"""
        try:
            async with asyncpg.connect(self.db_url) as conn:
                results = await conn.fetch(
                    """SELECT profile_name, display_name, description, icon_url, is_default 
                       FROM prompt_templates WHERE active = true ORDER BY is_default DESC, display_name"""
                )
                return [dict(row) for row in results]
        except Exception as e:
            logger.error(f"Error retrieving active profiles: {e}")
            return []
    
    async def _invalidate_cache(self, profile_name: str):
        """Invalidate both Redis and in-memory caches"""
        # Clear in-memory cache
        self._cache.pop(profile_name, None)
        
        # Clear Redis cache
        if self.redis_client:
            try:
                cache_key = f"prompt_template:{profile_name}"
                self.redis_client.delete(cache_key)
            except Exception as e:
                logger.warning(f"Redis delete error: {e}")
```

### 2. Enhanced Chainlit Configuration

```python
# Enhanced bot_config.py
import chainlit as cl
import os
import json
import logging
from typing import Optional
from lib.dynamic_prompt_manager import DynamicPromptManager

logger = logging.getLogger(__name__)

# Initialize dynamic prompt manager
prompt_manager = DynamicPromptManager(
    database_url=os.getenv("DATABASE_URL"),
    redis_url=os.getenv("REDIS_URL")
)

@cl.set_chat_profiles
async def chat_profile():
    """
    Dynamic chat profiles loaded from database
    
    Returns:
        List[cl.ChatProfile]: Available chat profiles
    """
    try:
        profiles_data = await prompt_manager.get_all_active_profiles()
        
        chat_profiles = []
        for profile in profiles_data:
            chat_profiles.append(
                cl.ChatProfile(
                    name=profile['profile_name'],
                    markdown_description=profile['description'] or f"Chat with {profile['display_name']}",
                    icon=profile.get('icon_url'),
                    default=profile['is_default']
                )
            )
        
        if not chat_profiles:
            # Fallback to default profile if database is empty
            logger.warning("No active profiles found, using fallback")
            chat_profiles = [
                cl.ChatProfile(
                    name="AI",
                    markdown_description="Default AI Assistant",
                    default=True
                )
            ]
        
        return chat_profiles
        
    except Exception as e:
        logger.error(f"Error loading chat profiles: {e}")
        # Return fallback profile
        return [
            cl.ChatProfile(
                name="AI",
                markdown_description="AI Assistant (Fallback Mode)",
                default=True
            )
        ]

@cl.on_chat_start
async def on_chat_start():
    """
    Initialize chat session with dynamic prompt configuration
    """
    try:
        chat_profile = cl.user_session.get("chat_profile", "AI")
        
        # Load profile configuration from database
        profile_config = await prompt_manager.get_prompt_template(chat_profile)
        
        if profile_config:
            # Set session configuration
            cl.user_session.set("reasoning_enabled", profile_config['reasoning_enabled'])
            cl.user_session.set("system_prompt", profile_config['system_prompt'])
            cl.user_session.set("eos_tokens", profile_config['eos_tokens'])
            cl.user_session.set("default_voice", profile_config['default_voice'])
            cl.user_session.set("reasoning_mode", profile_config['reasoning_enabled'])
            
            # Welcome message
            reasoning_status = "enabled" if profile_config['reasoning_enabled'] else "disabled"
            await cl.Message(
                content=f"🤖 **{profile_config['display_name']}** initialized successfully!\n\n"
                       f"💭 Reasoning mode: **{reasoning_status}**\n"
                       f"🎤 Voice: **{profile_config['default_voice']}**\n\n"
                       f"Type `/help` for available commands or just start chatting!"
            ).send()
        else:
            logger.error(f"Could not load configuration for profile: {chat_profile}")
            await cl.Message(
                content=f"⚠️ Configuration error for profile '{chat_profile}'. Using default settings."
            ).send()
            
            # Set fallback configuration
            cl.user_session.set("reasoning_enabled", True)
            cl.user_session.set("system_prompt", "You are a helpful AI assistant.")
            cl.user_session.set("eos_tokens", ["<think>", "</think>"])
            cl.user_session.set("default_voice", "default_voice")
            cl.user_session.set("reasoning_mode", True)
            
    except Exception as e:
        logger.error(f"Error in chat start: {e}")
        await cl.Message(
            content="⚠️ System initialization error. Please refresh the page."
        ).send()

@cl.on_message
async def on_message(message: cl.Message):
    """
    Handle incoming messages with dynamic prompt awareness
    
    Args:
        message: User message object
    """
    try:
        content = message.content.strip()
        
        # Handle system commands
        if content.startswith('/'):
            await handle_system_command(content)
            return
        
        # Get current session configuration
        system_prompt = cl.user_session.get("system_prompt", "You are a helpful AI assistant.")
        reasoning_mode = cl.user_session.get("reasoning_mode", True)
        eos_tokens = cl.user_session.get("eos_tokens", ["<think>", "</think>"])
        
        # Process message with SmolLM3
        response = await process_with_smollm3(
            user_message=content,
            system_prompt=system_prompt,
            reasoning_enabled=reasoning_mode,
            eos_tokens=eos_tokens
        )
        
        await cl.Message(content=response).send()
        
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        await cl.Message(
            content="⚠️ Sorry, I encountered an error processing your message. Please try again."
        ).send()

async def handle_system_command(command: str):
    """
    Handle system commands for runtime configuration
    
    Args:
        command: Command string starting with '/'
    """
    parts = command.lower().split()
    cmd = parts[0]
    
    if cmd == '/think':
        cl.user_session.set("reasoning_mode", True)
        await cl.Message(content="🧠 **Reasoning mode enabled** - I'll show my thinking process").send()
        
    elif cmd == '/no_think':
        cl.user_session.set("reasoning_mode", False)
        await cl.Message(content="⚡ **Direct response mode enabled** - I'll give quick answers").send()
        
    elif cmd == '/status':
        profile = cl.user_session.get("chat_profile", "Unknown")
        reasoning = cl.user_session.get("reasoning_mode", False)
        voice = cl.user_session.get("default_voice", "default")
        
        await cl.Message(
            content=f"📊 **Current Status**\n\n"
                   f"👤 Profile: **{profile}**\n"
                   f"💭 Reasoning: **{'On' if reasoning else 'Off'}**\n"
                   f"🎤 Voice: **{voice}**"
        ).send()
        
    elif cmd == '/help':
        await cl.Message(
            content="🆘 **Available Commands**\n\n"
                   f"• `/think` - Enable reasoning mode\n"
                   f"• `/no_think` - Disable reasoning mode\n"
                   f"• `/status` - Show current configuration\n"
                   f"• `/help` - Show this help message\n\n"
                   f"💡 **Tip**: Reasoning mode shows my thought process, "
                   f"while direct mode gives quick responses."
        ).send()
        
    elif cmd == '/reload_config' and await is_admin_user():
        # Admin command to reload configuration
        chat_profile = cl.user_session.get("chat_profile")
        await prompt_manager._invalidate_cache(chat_profile)
        await cl.Message(content="🔄 **Configuration reloaded** from database").send()
        
    else:
        await cl.Message(
            content=f"❓ Unknown command: `{cmd}`\n\nType `/help` for available commands."
        ).send()

async def is_admin_user() -> bool:
    """
    Check if current user has admin privileges
    
    Returns:
        bool: True if user is admin
    """
    user = cl.user_session.get("user")
    return user and user.metadata.get("role") == "ADMIN"

async def process_with_smollm3(
    user_message: str, 
    system_prompt: str, 
    reasoning_enabled: bool,
    eos_tokens: list
) -> str:
    """
    Process message with SmolLM3 using dynamic configuration
    
    Args:
        user_message: User's input message
        system_prompt: Dynamic system prompt from database
        reasoning_enabled: Whether to use reasoning mode
        eos_tokens: End-of-string tokens for proper parsing
        
    Returns:
        str: Model response
    """
    try:
        # Configure model generation parameters
        generation_config = configure_model_eos_tokens(eos_tokens)
        
        # Build prompt based on reasoning mode
        if reasoning_enabled:
            full_prompt = f"{system_prompt}\n\nUser: {user_message}\n\nAssistant: <think>\nLet me think about this...\n</think>\n\n"
        else:
            full_prompt = f"{system_prompt}\n\nUser: {user_message}\n\nAssistant: "
        
        # Generate response with SmolLM3
        # TODO: Integrate with your existing SmolLM3 pipeline
        response = await generate_smollm3_response(full_prompt, generation_config)
        
        # Clean up response if needed
        if reasoning_enabled:
            # Remove <think> tags from final response for TTS
            response = remove_thinking_tags(response)
        
        return response
        
    except Exception as e:
        logger.error(f"Error in SmolLM3 processing: {e}")
        return "I apologize, but I'm having trouble generating a response right now. Please try again."

def configure_model_eos_tokens(eos_tokens: list) -> dict:
    """
    Configure EOS tokens for SmolLM3 to handle reasoning tags properly
    
    Args:
        eos_tokens: List of tokens that should end generation
        
    Returns:
        dict: Generation configuration
    """
    # TODO: Integrate with your tokenizer
    generation_config = {
        "eos_token_id": None,  # Will be set based on eos_tokens
        "pad_token_id": None,  # Set from tokenizer
        "do_sample": True,
        "temperature": 0.7,
        "max_new_tokens": 2048,
        "top_p": 0.9,
        "repetition_penalty": 1.1
    }
    
    return generation_config

def remove_thinking_tags(response: str) -> str:
    """
    Remove <think>...</think> tags from response for TTS
    
    Args:
        response: Raw model response
        
    Returns:
        str: Cleaned response without thinking tags
    """
    import re
    
    # Remove thinking blocks
    cleaned = re.sub(r'<think>.*?</think>', '', response, flags=re.DOTALL)
    
    # Clean up extra whitespace
    cleaned = re.sub(r'\n\s*\n', '\n\n', cleaned)
    cleaned = cleaned.strip()
    
    return cleaned

async def generate_smollm3_response(prompt: str, config: dict) -> str:
    """
    Generate response using SmolLM3 model
    
    Args:
        prompt: Full prompt to send to model
        config: Generation configuration
        
    Returns:
        str: Generated response
    """
    # TODO: Implement your SmolLM3 integration here
    # This should connect to your existing model pipeline
    
    # Placeholder implementation
    return "This is a placeholder response. Please integrate with your SmolLM3 model."
```

### 3. Admin Interface (Optional Enhancement)

```python
# admin/prompt_admin.py
import chainlit as cl
from lib.dynamic_prompt_manager import DynamicPromptManager
import json

@cl.action_callback("edit_prompt")
async def edit_prompt_callback(action: cl.Action):
    """Handle prompt editing requests"""
    
    if not await is_admin_user():
        await cl.Message(content="❌ Admin access required").send()
        return
    
    profile_name = action.value
    current_config = await prompt_manager.get_prompt_template(profile_name)
    
    if current_config:
        # Create form for editing
        await show_prompt_edit_form(profile_name, current_config)
    else:
        await cl.Message(content=f"❌ Profile '{profile_name}' not found").send()

async def show_prompt_edit_form(profile_name: str, config: dict):
    """Show interactive form for prompt editing"""
    
    elements = [
        cl.Text(
            name="system_prompt",
            label="System Prompt",
            value=config['system_prompt'],
            multiline=True
        ),
        cl.Switch(
            name="reasoning_enabled",
            label="Enable Reasoning Mode",
            initial=config['reasoning_enabled']
        ),
        cl.Select(
            name="default_voice",
            label="Default Voice",
            values=["default_voice", "Yoda_voice", "stark_voice"],
            initial_index=0
        ),
        cl.Text(
            name="eos_tokens",
            label="EOS Tokens (JSON)",
            value=json.dumps(config['eos_tokens'])
        )
    ]
    
    await cl.AskUserMessage(
        content=f"Edit configuration for **{profile_name}**:",
        elements=elements
    ).send()
```

---

## Migration Strategy

### Phase 1: Database Setup (Week 1)
1. Create database tables using provided schema
2. Migrate existing PROFILE_DEFAULTS to database
3. Verify data integrity and relationships

### Phase 2: Core Implementation (Week 2-3)
1. Implement DynamicPromptManager class
2. Update bot_config.py with database integration
3. Add caching layer for performance
4. Test basic functionality with existing profiles

### Phase 3: Enhanced Features (Week 4)
1. Add system commands (/think, /no_think, /status)
2. Implement proper EOS token handling
3. Add error handling and fallbacks
4. Performance optimization and testing

### Phase 4: Admin Interface (Week 5)
1. Create prompt management interface
2. Add version control and history tracking
3. Implement user access controls
4. Add monitoring and analytics

### Phase 5: Production Deployment (Week 6)
1. Load testing and performance validation
2. Production deployment with monitoring
3. User training and documentation
4. Post-deployment monitoring and optimization

---

## Testing Strategy

### Unit Tests

```python
# tests/test_dynamic_prompt_manager.py
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from lib.dynamic_prompt_manager import DynamicPromptManager

@pytest.fixture
async def prompt_manager():
    """Create test prompt manager instance"""
    return DynamicPromptManager(
        database_url="postgresql://test:test@localhost/test_db",
        redis_url=None  # Disable Redis for tests
    )

@pytest.mark.asyncio
async def test_get_prompt_template_success(prompt_manager):
    """Test successful prompt template retrieval"""
    # Mock database connection
    prompt_manager._db_connect = AsyncMock()
    
    mock_result = {
        'id': 1,
        'profile_name': 'test_profile',
        'system_prompt': 'Test prompt',
        'reasoning_enabled': True,
        'eos_tokens': ['<think>', '</think>'],
        'default_voice': 'test_voice'
    }
    
    # Setup mock
    mock_conn = AsyncMock()
    mock_conn.fetchrow.return_value = mock_result
    prompt_manager._db_connect.return_value.__aenter__.return_value = mock_conn
    
    # Test
    result = await prompt_manager.get_prompt_template('test_profile')
    
    # Assertions
    assert result is not None
    assert result['profile_name'] == 'test_profile'
    assert result['system_prompt'] == 'Test prompt'

@pytest.mark.asyncio
async def test_get_prompt_template_not_found(prompt_manager):
    """Test prompt template not found scenario"""
    # Mock database connection returning None
    mock_conn = AsyncMock()
    mock_conn.fetchrow.return_value = None
    prompt_manager._db_connect = AsyncMock()
    prompt_manager._db_connect.return_value.__aenter__.return_value = mock_conn
    
    # Test
    result = await prompt_manager.get_prompt_template('nonexistent_profile')
    
    # Assertions
    assert result is None

@pytest.mark.asyncio
async def test_update_prompt_template_success(prompt_manager):
    """Test successful prompt template update"""
    # Mock database operations
    mock_conn = AsyncMock()
    mock_conn.fetchrow.return_value = {
        'id': 1, 'version': 1, 'system_prompt': 'Old prompt',
        'reasoning_enabled': True, 'eos_tokens': ['<think>', '</think>']
    }
    mock_conn.execute.return_value = None
    mock_conn.transaction.return_value.__aenter__.return_value = AsyncMock()
    
    prompt_manager._db_connect = AsyncMock()
    prompt_manager._db_connect.return_value.__aenter__.return_value = mock_conn
    
    # Test data
    new_template = {
        'system_prompt': 'Updated prompt',
        'reasoning_enabled': False,
        'default_voice': 'new_voice',
        'eos_tokens': ['<start>', '<end>']
    }
    
    # Test
    result = await prompt_manager.update_prompt_template(
        'test_profile', new_template, 'test_user', 'Testing update'
    )
    
    # Assertions
    assert result is True
    assert mock_conn.execute.call_count == 2  # History insert + template update
```

### Integration Tests

```python
# tests/test_chainlit_integration.py
import pytest
import chainlit as cl
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_chat_profile_loading():
    """Test dynamic chat profile loading"""
    
    mock_profiles = [
        {
            'profile_name': 'Yoda',
            'display_name': 'Yoda - Jedi Master',
            'description': 'Wise Jedi Master',
            'icon_url': None,
            'is_default': True
        }
    ]
    
    with patch('bot_config.prompt_manager.get_all_active_profiles') as mock_get:
        mock_get.return_value = mock_profiles
        
        # Import and call the function
        from bot_config import chat_profile
        profiles = await chat_profile()
        
        # Assertions
        assert len(profiles) == 1
        assert profiles[0].name == 'Yoda'
        assert profiles[0].default is True

@pytest.mark.asyncio
async def test_system_command_handling():
    """Test system command processing"""
    
    # Mock user session
    mock_session = {
        'reasoning_mode': True,
        'chat_profile': 'Yoda'
    }
    
    with patch('chainlit.user_session.get') as mock_get:
        with patch('chainlit.user_session.set') as mock_set:
            with patch('chainlit.Message.send') as mock_send:
                mock_get.side_effect = lambda key, default=None: mock_session.get(key, default)
                
                from bot_config import handle_system_command
                
                # Test /think command
                await handle_system_command('/think')
                
                # Verify reasoning mode was enabled
                mock_set.assert_called_with('reasoning_mode', True)
                mock_send.assert_called_once()
```

### Performance Tests

```python
# tests/test_performance.py
import pytest
import time
import asyncio
from lib.dynamic_prompt_manager import DynamicPromptManager

@pytest.mark.asyncio
async def test_prompt_retrieval_performance():
    """Test prompt retrieval performance under load"""
    
    prompt_manager = DynamicPromptManager("postgresql://test:test@localhost/test_db")
    
    # Mock fast database response
    prompt_manager.get_prompt_template = AsyncMock(return_value={
        'profile_name': 'test',
        'system_prompt': 'Test prompt'
    })
    
    # Test concurrent requests
    start_time = time.time()
    
    tasks = [
        prompt_manager.get_prompt_template('test_profile') 
        for _ in range(100)
    ]
    
    results = await asyncio.gather(*tasks)
    
    end_time = time.time()
    elapsed = end_time - start_time
    
    # Assert performance criteria
    assert elapsed < 1.0  # Should complete 100 requests in under 1 second
    assert all(result is not None for result in results)
    
    # Calculate average response time
    avg_response_time = elapsed / len(tasks) * 1000  # Convert to milliseconds
    assert avg_response_time < 10  # Each request should average under 10ms
```

---

## Deployment Considerations

### Environment Configuration

```bash
# .env additions for dynamic prompt system
DATABASE_URL=postgresql://user:password@localhost:5432/chainloot_db
REDIS_URL=redis://localhost:6379/0
PROMPT_CACHE_TTL=300
ENABLE_PROMPT_ANALYTICS=true
ADMIN_USERS=admin@example.com,superuser@example.com
```

### Docker Compose Updates

```yaml
# docker-compose.yml additions
version: '3.8'

services:
  chainlit-app:
    # ... existing configuration ...
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
      - PROMPT_CACHE_TTL=${PROMPT_CACHE_TTL}
    depends_on:
      - postgres
      - redis
      
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes

volumes:
  redis_data:
```

### Monitoring and Logging

```python
# monitoring/prompt_metrics.py
import logging
import time
from functools import wraps
from prometheus_client import Counter, Histogram, Gauge

# Metrics
prompt_requests_total = Counter(
    'prompt_requests_total', 
    'Total prompt template requests',
    ['profile_name', 'status']
)

prompt_request_duration = Histogram(
    'prompt_request_duration_seconds',
    'Time spent retrieving prompt templates',
    ['profile_name']
)

active_profiles_gauge = Gauge(
    'active_profiles_total',
    'Number of active chat profiles'
)

def monitor_prompt_request(func):
    """Decorator to monitor prompt request metrics"""
    
    @wraps(func)
    async def wrapper(*args, **kwargs):
        profile_name = args[1] if len(args) > 1 else 'unknown'
        
        start_time = time.time()
        
        try:
            result = await func(*args, **kwargs)
            
            # Record success metrics
            prompt_requests_total.labels(
                profile_name=profile_name, 
                status='success'
            ).inc()
            
            return result
            
        except Exception as e:
            # Record error metrics
            prompt_requests_total.labels(
                profile_name=profile_name, 
                status='error'
            ).inc()
            
            logging.error(f"Prompt request failed: {e}")
            raise
            
        finally:
            # Record duration
            duration = time.time() - start_time
            prompt_request_duration.labels(
                profile_name=profile_name
            ).observe(duration)
    
    return wrapper
```

### Security Considerations

1. **Database Security**
   - Use connection pooling with appropriate limits
   - Implement row-level security for multi-tenant scenarios
   - Regular security updates and patches

2. **Input Validation**
   - Sanitize all prompt template inputs
   - Validate JSON structure for eos_tokens
   - Implement rate limiting for admin operations

3. **Access Control**
   - Implement proper authentication for admin functions
   - Use role-based access control (RBAC)
   - Audit trail for all prompt modifications

4. **Data Protection**
   - Encrypt sensitive prompt data at rest
   - Use SSL/TLS for all database connections
   - Implement backup and recovery procedures

---

## Success Metrics

### Technical Metrics
- **Response Time**: < 100ms for cached prompt retrieval
- **Availability**: > 99.9% uptime for prompt service
- **Cache Hit Rate**: > 95% for frequently used profiles
- **Database Performance**: < 50ms average query time

### Business Metrics
- **Development Velocity**: 50% faster prompt iteration cycles
- **User Experience**: Zero downtime deployments for prompt updates
- **Operational Efficiency**: 80% reduction in manual configuration tasks
- **System Reliability**: < 0.1% error rate for prompt loading

### Monitoring Dashboard

Create monitoring dashboards with:
- Real-time prompt request metrics
- Cache performance statistics
- Database query performance
- Error rates and types
- User session analytics

---

## Conclusion

This implementation provides a robust, scalable solution for dynamic prompt management while maintaining backward compatibility with existing systems. The architecture supports future enhancements like user-specific customizations, A/B testing capabilities, and advanced analytics.

The phased approach ensures minimal disruption to current operations while delivering immediate benefits in development velocity and system flexibility.

## Next Steps

1. **Review and Approval**: Technical review of implementation plan
2. **Environment Setup**: Prepare development and testing environments
3. **Database Migration**: Execute schema changes and data migration
4. **Implementation**: Begin Phase 1 development
5. **Testing**: Comprehensive testing of all components
6. **Deployment**: Production rollout with monitoring

---

*Document Version: 1.0*  
*Last Updated: November 2, 2025*  
*Author: AI Implementation Assistant*