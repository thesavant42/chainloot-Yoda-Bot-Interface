"""
Core prompt management functionality.

This module handles the actual prompt operations - loading, parsing, 
and managing prompt templates within Chainlit sessions.
"""

import chainlit as cl
import toml
import re
from typing import Dict, List, Optional, Any
from datetime import datetime


class PromptManager:
    """Manages prompt templates and their application to Chainlit sessions."""
    
    def __init__(self):
        self.database = None
    
    async def initialize(self):
        """Initialize database connection using existing datalayer."""
        try:
            # Import your existing database module
            from ..database import get_data_layer
            self.database = get_data_layer()
        except ImportError:
            # Fallback - we'll create minimal database functions
            from .database import DatabaseConnection
            self.database = DatabaseConnection()
            await self.database.initialize()
    
    async def handle_command(self, command: str) -> Optional[str]:
        """Handle prompt catalog chat commands."""
        parts = command.split()
        
        if len(parts) < 2:
            return self._get_help_text()
        
        subcommand = parts[1].lower()
        
        if subcommand == 'list':
            return await self._list_prompts()
        elif subcommand == 'load' and len(parts) >= 3:
            try:
                prompt_id = int(parts[2])
                return await self._load_prompt(prompt_id)
            except ValueError:
                return "Invalid prompt ID. Please provide a number."
        elif subcommand == 'info' and len(parts) >= 3:
            try:
                prompt_id = int(parts[2])
                return await self._show_prompt_info(prompt_id)
            except ValueError:
                return "Invalid prompt ID. Please provide a number."
        elif subcommand == 'search' and len(parts) >= 3:
            tag = parts[2]
            return await self._search_prompts(tag)
        elif subcommand == 'active':
            return await self._show_active_prompt()
        elif subcommand == 'clear':
            return await self._clear_active_prompt()
        else:
            return self._get_help_text()
    
    def _get_help_text(self) -> str:
        """Get help text for prompt commands."""
        return """**Prompt Catalog Commands:**

• `/prompts list` - Show all available prompts
• `/prompts load <id>` - Load a specific prompt by ID
• `/prompts info <id>` - Show detailed prompt information
• `/prompts search <tag>` - Search prompts by tag
• `/prompts active` - Show currently loaded prompt
• `/prompts clear` - Clear the active prompt

Example: `/prompts load 1`"""
    
    async def _list_prompts(self) -> str:
        """List available prompts."""
        try:
            prompts = await self.database.list_prompts()
            
            if not prompts:
                return "No prompts found in the catalog.\n\nYou can upload prompts by adding TOML files to the database."
            
            response = "**Available Prompt Templates:**\n\n"
            for prompt in prompts[:10]:  # Limit to 10
                response += f"**{prompt['id']}. {prompt['name']}** (v{prompt['version']})\n"
                response += f"   {prompt['description']}\n"
                response += f"   {prompt['author']}"
                
                if prompt.get('tags'):
                    response += f" | Tags: {', '.join(prompt['tags'])}"
                
                response += f" | Used {prompt.get('usage_count', 0)} times\n\n"
            
            if len(prompts) > 10:
                response += f"... and {len(prompts) - 10} more prompts.\n\n"
            
            response += "Use `/prompts load <id>` to load a specific prompt."
            return response
            
        except Exception as e:
            return f"Error listing prompts: {str(e)}"
    
    async def _load_prompt(self, prompt_id: int) -> str:
        """Load a prompt template into the current session."""
        try:
            prompt_data = await self.database.get_prompt(prompt_id)
            if not prompt_data:
                return f"Prompt with ID {prompt_id} not found."
            
            # Parse TOML content
            toml_data = toml.loads(prompt_data['toml_content'])
            
            # Apply prompt to session
            await self._apply_prompt_to_session(toml_data, prompt_id)
            
            # Record usage
            await self.database.record_prompt_usage(
                prompt_id=prompt_id,
                model_name=cl.user_session.get("selected_model", "unknown"),
                session_id=cl.context.session.id
            )
            
            response = f"**Loaded prompt: {toml_data['metadata']['name']}**\n\n"
            response += f"{toml_data['metadata']['description']}\n"
            response += f"System prompt has been updated for this session.\n\n"
            
            # Show available variables
            variables = toml_data.get('variables', {})
            if variables:
                var_names = list(variables.keys())
                response += f"*Variables available:* {', '.join(var_names)}"
            
            return response
            
        except Exception as e:
            return f"Error loading prompt: {str(e)}"
    
    async def _apply_prompt_to_session(self, toml_data: Dict, prompt_id: int):
        """Apply prompt template to the current Chainlit session."""
        # Store prompt data in session
        cl.user_session.set("prompt_catalog_active", True)
        cl.user_session.set("active_prompt_id", prompt_id)
        cl.user_session.set("active_prompt_data", toml_data)
        
        # Extract and store system prompt
        system_prompt = toml_data['system_prompt']['content']
        cl.user_session.set("system_prompt", system_prompt)
        
        # Store variables for substitution
        variables = toml_data.get('variables', {})
        cl.user_session.set("prompt_variables", variables)
        
        # Store model adaptations
        adaptations = toml_data.get('model_adaptations', {})
        cl.user_session.set("model_adaptations", adaptations)
        
        # Store EOS/stop sequences
        chat_template = toml_data.get('chat_template', {})
        if 'stop_sequences' in chat_template:
            cl.user_session.set("stop_sequences", chat_template['stop_sequences'])
        if 'eos_token' in chat_template:
            cl.user_session.set("eos_token", chat_template['eos_token'])
    
    async def get_active_system_prompt(self) -> Optional[str]:
        """Get the active system prompt with variable substitution."""
        if not cl.user_session.get("prompt_catalog_active", False):
            return None
        
        system_prompt = cl.user_session.get("system_prompt", "")
        variables = cl.user_session.get("prompt_variables", {})
        
        # Apply variable substitution
        return self._substitute_variables(system_prompt, variables)
    
    def _substitute_variables(self, template: str, variables: Dict[str, Any]) -> str:
        """Substitute variables in template string."""
        # Get current variable values from session or use defaults
        current_values = {}
        
        for var_name, var_config in variables.items():
            # Try to get from session first (user may have set values)
            session_value = cl.user_session.get(f"prompt_var_{var_name}")
            if session_value is not None:
                current_values[var_name] = session_value
            elif var_config.get('default_value'):
                current_values[var_name] = var_config['default_value']
            # If no default and required, leave placeholder
        
        # Substitute {{variable}} placeholders
        def replace_var(match):
            var_name = match.group(1)
            return str(current_values.get(var_name, f"{{{{{var_name}}}}}"))
        
        return re.sub(r'\{\{(\w+)\}\}', replace_var, template)
    
    async def _show_prompt_info(self, prompt_id: int) -> str:
        """Show detailed information about a prompt."""
        try:
            prompt_data = await self.database.get_prompt(prompt_id)
            if not prompt_data:
                return f"Prompt with ID {prompt_id} not found."
            
            toml_data = toml.loads(prompt_data['toml_content'])
            meta = toml_data['metadata']
            
            response = f"**Prompt Details: {meta['name']}**\n\n"
            response += f"**Version:** {meta['version']}\n"
            response += f"**Author:** {meta['author']}\n"
            response += f"**Description:** {meta['description']}\n"
            
            if meta.get('tags'):
                response += f"**Tags:** {', '.join(meta['tags'])}\n"
            
            # Show variables
            variables = toml_data.get('variables', {})
            if variables:
                response += f"\n**Variables ({len(variables)}):**\n"
                for var_name, var_config in variables.items():
                    required = "Required" if var_config.get('required', True) else "Optional"
                    default = f" (default: {var_config.get('default_value')})" if var_config.get('default_value') else ""
                    response += f"- **{var_name}** {required}{default}\n"
                    response += f"  {var_config['description']}\n"
            
            # Show model adaptations
            adaptations = toml_data.get('model_adaptations', {})
            if adaptations:
                response += f"\n**Model Adaptations ({len(adaptations)}):**\n"
                for model_name, config in adaptations.items():
                    response += f"- **{model_name}:** {config.get('model_pattern', 'N/A')}\n"
            
            # Show system prompt preview
            system_prompt = toml_data['system_prompt']['content']
            preview = system_prompt[:200] + "..." if len(system_prompt) > 200 else system_prompt
            response += f"\n**System Prompt Preview:**\n```\n{preview}\n```"
            
            response += f"\n\nUse `/prompts load {prompt_id}` to load this prompt."
            return response
            
        except Exception as e:
            return f"Error getting prompt info: {str(e)}"
    
    async def _search_prompts(self, tag: str) -> str:
        """Search prompts by tag."""
        try:
            prompts = await self.database.search_prompts_by_tag(tag)
            
            if not prompts:
                return f"No prompts found with tag '{tag}'."
            
            response = f"**Prompts tagged with '{tag}':**\n\n"
            for prompt in prompts[:5]:  # Limit to 5
                response += f"**{prompt['id']}. {prompt['name']}**\n"
                response += f"   {prompt['description']}\n"
                response += f"   {prompt['author']} | Used {prompt.get('usage_count', 0)} times\n\n"
            
            return response
            
        except Exception as e:
            return f"Error searching prompts: {str(e)}"
    
    async def _show_active_prompt(self) -> str:
        """Show information about the currently active prompt."""
        if not cl.user_session.get("prompt_catalog_active", False):
            return "No custom prompt is currently active. Using default system prompt."
        
        prompt_id = cl.user_session.get("active_prompt_id")
        prompt_data = cl.user_session.get("active_prompt_data", {})
        
        if not prompt_data:
            return "Active prompt data is corrupted. Use `/prompts clear` to reset."
        
        meta = prompt_data.get('metadata', {})
        response = f"**Active Prompt: {meta.get('name', 'Unknown')}** (ID: {prompt_id})\n\n"
        response += f"{meta.get('description', 'No description')}\n"
        response += f"By {meta.get('author', 'Unknown')}\n"
        
        # Show current variable values
        variables = cl.user_session.get("prompt_variables", {})
        if variables:
            response += f"\n**Current Variable Values:**\n"
            for var_name, var_config in variables.items():
                current_value = cl.user_session.get(f"prompt_var_{var_name}")
                if current_value is None:
                    current_value = var_config.get('default_value', 'Not set')
                response += f"- {var_name}: `{current_value}`\n"
        
        response += f"\nUse `/prompts clear` to deactivate this prompt."
        return response
    
    async def _clear_active_prompt(self) -> str:
        """Clear the currently active prompt."""
        if not cl.user_session.get("prompt_catalog_active", False):
            return "No custom prompt is currently active."
        
        # Clear all prompt-related session data
        cl.user_session.set("prompt_catalog_active", False)
        cl.user_session.set("active_prompt_id", None)
        cl.user_session.set("active_prompt_data", None)
        cl.user_session.set("system_prompt", None)
        cl.user_session.set("prompt_variables", {})
        cl.user_session.set("model_adaptations", {})
        cl.user_session.set("stop_sequences", None)
        cl.user_session.set("eos_token", None)
        
        # Clear any variable values
        variables = cl.user_session.get("prompt_variables", {})
        for var_name in variables.keys():
            cl.user_session.set(f"prompt_var_{var_name}", None)
        
        return "Active prompt cleared. Using default system prompt."
    
    async def load_prompt_by_id(self, prompt_id: int) -> bool:
        """Programmatically load a prompt (for external use)."""
        try:
            result = await self._load_prompt(prompt_id)
            return not result.startswith("Error")
        except Exception:
            return False