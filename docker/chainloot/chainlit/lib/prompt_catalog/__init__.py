"""
Modular Prompt Catalog integration for Chainlit.

This module provides prompt template management functionality that can be
easily integrated into existing Chainlit applications with minimal changes.
"""

import chainlit as cl
import os
import sys
from typing import Optional


class PromptCatalogModule:
    """
    Main entry point for prompt catalog functionality.
    
    Usage in your app.py:
    
    from lib.prompt_catalog import PromptCatalogModule
    prompt_catalog = PromptCatalogModule()
    
    @cl.on_message
    async def main(message: cl.Message):
        # Check for prompt commands first
        if await prompt_catalog.handle_message(message):
            return
        
        # Your existing logic continues here...
    """
    
    def __init__(self):
        self.manager = None
        self._initialized = False
    
    async def initialize(self):
        """Initialize the prompt catalog system."""
        if self._initialized:
            return
        
        try:
            # Lazy import to avoid circular dependencies
            from .prompt_manager import PromptManager
            self.manager = PromptManager()
            await self.manager.initialize()
            self._initialized = True
        except Exception as e:
            print(f"Warning: Prompt catalog initialization failed: {e}")
            self._initialized = False
    
    async def handle_message(self, message: cl.Message) -> bool:
        """
        Handle incoming messages for prompt catalog commands.
        
        Returns:
            True if the message was a prompt command and was handled
            False if the message should be processed by the main app logic
        """
        if not message.content.startswith('/prompts'):
            return False
        
        # Ensure we're initialized
        if not self._initialized:
            await self.initialize()
        
        if not self.manager:
            await cl.Message(
                content="❌ Prompt catalog is not available. Please check configuration."
            ).send()
            return True
        
        try:
            response = await self.manager.handle_command(message.content)
            if response:
                await cl.Message(content=response).send()
        except Exception as e:
            await cl.Message(
                content=f"❌ Error processing prompt command: {str(e)}"
            ).send()
        
        return True
    
    async def get_active_system_prompt(self) -> Optional[str]:
        """
        Get the currently active system prompt with variables substituted.
        
        Returns:
            The active system prompt or None if no prompt is loaded
        """
        if not self._initialized or not self.manager:
            return None
        
        return await self.manager.get_active_system_prompt()
    
    def is_prompt_active(self) -> bool:
        """Check if a custom prompt is currently active."""
        return cl.user_session.get("prompt_catalog_active", False)
    
    async def load_prompt_by_id(self, prompt_id: int) -> bool:
        """
        Programmatically load a prompt by ID.
        
        Args:
            prompt_id: The ID of the prompt to load
            
        Returns:
            True if successful, False otherwise
        """
        if not self._initialized:
            await self.initialize()
        
        if not self.manager:
            return False
        
        try:
            return await self.manager.load_prompt_by_id(prompt_id)
        except Exception:
            return False


# Global instance - import this in your app.py
prompt_catalog = PromptCatalogModule()