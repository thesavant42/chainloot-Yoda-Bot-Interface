"""
Database operations for the Prompt Catalog system.

This module provides database connectivity and operations for prompt management,
designed to work with your existing PostgreSQL setup.
"""

import asyncio
import asyncpg
from typing import List, Dict, Optional, Any
from datetime import datetime
import os


class DatabaseConnection:
    """Handles database operations for the prompt catalog."""
    
    def __init__(self):
        self.pool = None
        
    async def initialize(self):
        """Initialize database connection using existing PostgreSQL setup."""
        try:
            # Use the same database URL as your existing Chainlit setup
            database_url = os.getenv("DATABASE_URL", "postgresql://root:root@localhost:5432/chainlit")
            
            # Create connection pool
            self.pool = await asyncpg.create_pool(database_url, min_size=1, max_size=5)
            
            # Test the connection
            async with self.pool.acquire() as conn:
                await conn.fetchval("SELECT 1")
                
        except Exception as e:
            print(f"Warning: Failed to initialize prompt catalog database: {e}")
            print("Make sure PostgreSQL is running and the database schema is created.")
            raise
    
    async def _ensure_tables_exist(self):
        """Ensure prompt catalog tables exist (run schema if needed)."""
        async with self.pool.acquire() as conn:
            # Check if prompts table exists
            exists = await conn.fetchval("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'prompts'
                );
            """)
            
            if not exists:
                # Tables don't exist - need to run schema
                print("Warning: Prompt catalog tables not found.")
                print("Please run the database initialization script first:")
                print("  cd docs/IN_PROGRESS_TASKS/prompt_catalog")
                print("  powershell -ExecutionPolicy Bypass -File init_database.ps1")
                raise Exception("Prompt catalog tables not found in database")
    
    async def list_prompts(self, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """List all available prompts with usage statistics."""
        if not self.pool:
            await self.initialize()
        
        await self._ensure_tables_exist()
        
        async with self.pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT 
                    p.id, p.name, p.description, p.version, p.author, 
                    p.tags, p.created_at, 
                    COALESCE(u.usage_count, 0) as usage_count
                FROM prompts p
                LEFT JOIN (
                    SELECT prompt_id, COUNT(*) as usage_count 
                    FROM prompt_usage_history 
                    GROUP BY prompt_id
                ) u ON p.id = u.prompt_id
                ORDER BY p.created_at DESC 
                LIMIT $1 OFFSET $2
            """, limit, offset)
            
            return [dict(row) for row in rows]
    
    async def get_prompt(self, prompt_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific prompt by ID."""
        if not self.pool:
            await self.initialize()
        
        await self._ensure_tables_exist()
        
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("""
                SELECT id, name, description, version, author, tags,
                       system_prompt, chat_template, toml_content, created_at
                FROM prompts 
                WHERE id = $1
            """, prompt_id)
            
            return dict(row) if row else None
    
    async def search_prompts_by_tag(self, tag: str) -> List[Dict[str, Any]]:
        """Search prompts by tag."""
        if not self.pool:
            await self.initialize()
        
        await self._ensure_tables_exist()
        
        async with self.pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT 
                    p.id, p.name, p.description, p.author, 
                    COALESCE(u.usage_count, 0) as usage_count
                FROM prompts p
                LEFT JOIN (
                    SELECT prompt_id, COUNT(*) as usage_count 
                    FROM prompt_usage_history 
                    GROUP BY prompt_id
                ) u ON p.id = u.prompt_id
                WHERE $1 = ANY(p.tags)
                ORDER BY p.created_at DESC 
                LIMIT 10
            """, tag)
            
            return [dict(row) for row in rows]
    
    async def record_prompt_usage(self, prompt_id: int, model_name: str, session_id: str, 
                                chat_template: Optional[str] = None,
                                variables_used: Optional[Dict] = None):
        """Record usage of a prompt template."""
        if not self.pool:
            await self.initialize()
        
        await self._ensure_tables_exist()
        
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO prompt_usage_history (
                    prompt_id, model_name, chat_template_used, 
                    variables_used, session_id, used_at
                ) VALUES ($1, $2, $3, $4, $5, $6)
            """, 
                prompt_id, 
                model_name,
                chat_template,
                variables_used or {},
                session_id,
                datetime.utcnow()
            )
    
    async def insert_prompt_from_toml(self, toml_content: str, content_hash: str) -> int:
        """
        Insert a new prompt from TOML content.
        
        This method would be used by an upload function to add new prompts.
        For now, it's a placeholder for future functionality.
        """
        if not self.pool:
            await self.initialize()
        
        await self._ensure_tables_exist()
        
        # Parse TOML to extract metadata
        try:
            import toml
            data = toml.loads(toml_content)
        except ImportError:
            raise Exception("toml library not available. Please install: pip install toml")
        
        metadata = data.get('metadata', {})
        system_prompt = data.get('system_prompt', {}).get('content', '')
        chat_template = data.get('chat_template', {}).get('family')
        
        async with self.pool.acquire() as conn:
            prompt_id = await conn.fetchval("""
                INSERT INTO prompts (
                    name, description, version, author, tags,
                    system_prompt, chat_template, content_hash,
                    toml_content, created_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                RETURNING id
            """, 
                metadata.get('name', 'Untitled'),
                metadata.get('description', ''),
                metadata.get('version', '1.0'),
                metadata.get('author', 'unknown'),
                metadata.get('tags', []),
                system_prompt,
                chat_template,
                content_hash,
                toml_content,
                datetime.utcnow()
            )
            
            return prompt_id
    
    async def close(self):
        """Close database connection pool."""
        if self.pool:
            await self.pool.close()


# Fallback function to try using existing database layer
def get_data_layer():
    """
    Try to get the existing data layer from Chainlit app.
    
    This is a fallback that attempts to use your existing database setup.
    If it fails, we'll use our own DatabaseConnection class.
    """
    try:
        # Try to import your existing database setup
        # You might need to adjust this import path based on your structure
        import sys
        import os
        
        # Add the chainlit directory to path
        chainlit_dir = os.path.dirname(os.path.dirname(__file__))
        if chainlit_dir not in sys.path:
            sys.path.append(chainlit_dir)
        
        # Try to import your existing database module
        from database import get_data_layer as existing_data_layer
        return existing_data_layer()
        
    except ImportError:
        # Fallback to our own database connection
        return DatabaseConnection()