# lib/mcp_tool_processor.py

import re
import json
import string
from typing import Dict, Any, Optional, Tuple
from dateutil import parser
from lib.mcp_server_manager import mcp_manager
import os

def get_active_mcp_manager():
    """Get the active MCP manager (dynamic if config exists, otherwise legacy)"""
    if os.path.exists("config/mcp_servers.json"):
        from lib.dynamic_mcp_manager import dynamic_mcp_manager
        return dynamic_mcp_manager
    else:
        return mcp_manager
from chainlit.logger import logger

class MCPToolProcessor:
    """
    Intelligently detects when user messages require MCP tools and executes them.
    """
    
    def __init__(self):
        # Default user location information
        self.default_location = {
            "zip_code": "91327",
            "city": "Newbury Park",
            "state": "CA",
            "timezone": "America/Los_Angeles"
        }
        
        self.timezone_map = {
            "london": "Europe/London",
            "paris": "Europe/Paris", 
            "tokyo": "Asia/Tokyo",
            "new york": "America/New_York",
            "los angeles": "America/Los_Angeles",
            "los angeles, ca": "America/Los_Angeles",
            "la": "America/Los_Angeles",
            "chicago": "America/Chicago",
            "denver": "America/Denver",
            "atlanta": "America/New_York",
            "seattle": "America/Los_Angeles",
            "miami": "America/New_York",
            "hawaii": "Pacific/Honolulu",
            "alaska": "America/Anchorage",
        }
    
    async def should_use_tools(self, message: str) -> bool:
        """Determine if the message requires tool usage"""
        active_manager = get_active_mcp_manager()
        await active_manager.initialize()
        
        message_lower = message.lower()
        
        # Check for time-related queries
        if self._is_time_query(message_lower):
            return True
            
        # Check for search-related queries  
        if self._is_search_query(message_lower):
            return True
        
        # Check for fetch/web content queries
        if self._is_fetch_query(message_lower):
            return True
            
        # Check for git-related queries  
        if self._is_git_query(message_lower):
            return True
            
        # Check for memory-related queries
        if self._is_memory_query(message_lower):
            return True
        
        # Check for YouTube transcript queries
        if self._is_youtube_query(message_lower):
            return True
            
        # Check for Wikipedia queries
        if self._is_wikipedia_query(message_lower):
            return True
            
        return False
    
    def _is_time_query(self, message: str) -> bool:
        """Check if message is asking for time information"""
        time_indicators = [
            "what time is it",
            "current time",
            "time in",
            "what's the time",
            "tell me the time",
            "time now",
            "what time",
        ]
        
        return any(indicator in message for indicator in time_indicators)
    
    def _is_search_query(self, message: str) -> bool:
        """Check if message is asking for web search"""
        search_indicators = [
            "search for",
            "search the web",
            "look up",
            "find information about",
            "what is",
            "who is", 
            "tell me about",
            "find me",
            "search",
        ]
        
        return any(indicator in message for indicator in search_indicators)
    
    def _is_fetch_query(self, message: str) -> bool:
        """Check if message is asking to fetch web content"""
        fetch_indicators = [
            "fetch",
            "get the content",
            "download",
            "retrieve content",
            "fetch webpage",
            "get webpage",
            "scrape",
            "fetch url",
        ]
        
        return any(indicator in message for indicator in fetch_indicators)
    
    def _is_git_query(self, message: str) -> bool:
        """Check if message is asking for git operations"""
        git_indicators = [
            "git",
            "repository",
            "repo",
            "commit",
            "branch",
            "clone",
            "pull",
            "push",
            "merge",
            "git status",
            "git log",
        ]
        
        return any(indicator in message for indicator in git_indicators)
    
    def _is_memory_query(self, message: str) -> bool:
        """Check if message is asking for memory operations"""
        memory_indicators = [
            "remember",
            "save this",
            "store",
            "recall",
            "what did i say",
            "what did we discuss",
            "memory",
            "remind me",
            "note this",
        ]
        
        return any(indicator in message for indicator in memory_indicators)
    
    def _is_youtube_query(self, message: str) -> bool:
        """Check if message is asking for YouTube transcript"""
        youtube_indicators = [
            "youtube",
            "video transcript",
            "transcript",
            "youtube.com",
            "youtu.be",
            "video captions",
            "what does the video say",
            "transcript of",
            "subtitles",
        ]
        
        return any(indicator in message for indicator in youtube_indicators)
    
    def _is_wikipedia_query(self, message: str) -> bool:
        """Check if message is asking for Wikipedia information"""
        wikipedia_indicators = [
            "wikipedia",
            "wiki",
            "what is",
            "who is",
            "tell me about",
            "define",
            "definition of",
            "explain",
            "facts about",
            "information about",
        ]
        
        return any(indicator in message for indicator in wikipedia_indicators)
    
    def _get_ordinal_suffix(self, day: int) -> str:
        """Get ordinal suffix for day (1st, 2nd, 3rd, 4th, etc.)"""
        if 10 <= day % 100 <= 20:  # Special case for 11th, 12th, 13th
            suffix = "th"
        else:
            suffix = {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")
        return suffix
    
    def _get_friendly_location_name(self, display_name: str, timezone: str) -> str:
        """Convert timezone/display name to friendly location for TTS"""
        if display_name and display_name not in ["utc", "gmt"]:
            return display_name
        
        # Convert common timezone names to friendly versions
        timezone_map = {
            "America/Los_Angeles": "Los Angeles",
            "America/New_York": "New York", 
            "America/Chicago": "Chicago",
            "America/Denver": "Denver",
            "Europe/London": "London",
            "UTC": "UTC",
            "GMT": "GMT"
        }
        
        return timezone_map.get(timezone, timezone or "your location")
    
    def get_user_location(self, format_type="full") -> dict:
        """Get user's default location in various formats"""
        if format_type == "zip":
            return self.default_location["zip_code"]
        elif format_type == "city_state":
            return f"{self.default_location['city']}, {self.default_location['state']}"
        elif format_type == "timezone":
            return self.default_location["timezone"]
        else:  # full
            return f"{self.default_location['city']}, {self.default_location['state']} {self.default_location['zip_code']}"
    
    async def process_with_tools(self, message: str) -> Optional[str]:
        """
        Process a message using appropriate MCP tools and return the result.
        Returns None if no tools were used.
        """
        await get_active_mcp_manager().initialize()
        
        message_lower = message.lower()
        
        # Try time query first
        if self._is_time_query(message_lower):
            result = await self._handle_time_query(message)
            if result:
                return result
        
        # Try search query 
        if self._is_search_query(message_lower):
            result = await self._handle_search_query(message)
            if result:
                return result
        
        # Try fetch query
        if self._is_fetch_query(message_lower):
            result = await self._handle_fetch_query(message)
            if result:
                return result
        
        # Try git query
        if self._is_git_query(message_lower):
            result = await self._handle_git_query(message)
            if result:
                return result
        
        # Try memory query
        if self._is_memory_query(message_lower):
            result = await self._handle_memory_query(message)
            if result:
                return result
        
        # Try YouTube transcript query
        if self._is_youtube_query(message_lower):
            result = await self._handle_youtube_query(message)
            if result:
                return result
        
        # Try Wikipedia query
        if self._is_wikipedia_query(message_lower):
            result = await self._handle_wikipedia_query(message)
            if result:
                return result
        
        return None
    
    async def _handle_time_query(self, message: str) -> Optional[str]:
        """Handle time-related queries"""
        time_tool = get_active_mcp_manager().find_tool_by_capability("time")
        if not time_tool:
            return " Sorry, time tools are not available right now."
        
        try:
            # Parse timezone from message, default to Newbury Park, CA if none specified
            timezone, display_name = self._parse_timezone_from_message(message)
            
            # If no timezone specified, default to Newbury Park, CA (91327)
            if not timezone:
                timezone = "America/Los_Angeles"
                display_name = "Newbury Park, CA"
            
            tool_params = {"timezone": timezone} if timezone else {}
            
            logger.info(f"Calling time tool with params: {tool_params}")
            result = await get_active_mcp_manager().call_tool(time_tool, tool_params)
            
            # Parse the result
            if (result and result.content and len(result.content) > 0 
                and hasattr(result.content[0], "text")):
                
                try:
                    if "Error processing" in result.content[0].text:
                        return f" Sorry, I couldn't get the time: {result.content[0].text}"
                    
                    parsed_result = json.loads(result.content[0].text)
                    
                    if "datetime" in parsed_result:
                        dt_object = parser.isoparse(parsed_result["datetime"])
                        
                        # Format for TTS-friendly output
                        day_name = dt_object.strftime("%A")
                        month_day = dt_object.strftime("%B %d").replace(" 0", " ")  # Remove leading zero
                        day_ordinal = self._get_ordinal_suffix(dt_object.day)
                        time_12hr = dt_object.strftime("%I:%M %p").lstrip("0")  # Remove leading zero from hour
                        
                        # Convert timezone to friendly name
                        friendly_location = self._get_friendly_location_name(display_name, parsed_result.get("timezone"))
                        
                        return f" Today is {day_name}, {month_day}{day_ordinal}. The current time in {friendly_location} is {time_12hr}."
                        
                except json.JSONDecodeError:
                    pass
            
            return " Sorry, I couldn't get the time information right now."
            
        except Exception as e:
            logger.error(f"Error in time query: {e}")
            return f" Sorry, there was an error getting the time: {str(e)}"
    
    async def _handle_search_query(self, message: str) -> Optional[str]:
        """Handle search-related queries"""
        search_tool = get_active_mcp_manager().find_tool_by_capability("search")
        if not search_tool:
            return "Sorry, search tools are not available right now."
        
        try:
            # Extract search query from message
            query = self._extract_search_query(message)
            if not query:
                return "I'm not sure what you want me to search for. Please be more specific."
            
            logger.info(f"Calling search tool with query: {query}")
            result = await get_active_mcp_manager().call_tool(search_tool, {"query": query})
            
            # Parse and format the result
            if (result and result.content and len(result.content) > 0 
                and hasattr(result.content[0], "text") and result.content[0].text):
                
                search_results_text = result.content[0].text
                formatted_results = self._format_search_results(search_results_text, query)
                
                return formatted_results
            
            return f"Sorry, I couldn't find any search results for '{query}'."
            
        except Exception as e:
            logger.error(f"Error in search query: {e}")
            return f"Sorry, there was an error searching: {str(e)}"
    
    async def _handle_fetch_query(self, message: str) -> Optional[str]:
        """Handle fetch/web content queries"""
        fetch_tool = get_active_mcp_manager().find_tool_by_capability("fetch")
        if not fetch_tool:
            return "Sorry, fetch tools are not available right now."
        
        try:
            # Extract URL from message
            url = self._extract_url_from_message(message)
            if not url:
                return "I need a URL to fetch content from. Please provide a valid URL."
            
            logger.info(f"Calling fetch tool with URL: {url}")
            result = await get_active_mcp_manager().call_tool(fetch_tool, {"url": url})
            
            if (result and result.content and len(result.content) > 0 
                and hasattr(result.content[0], "text") and result.content[0].text):
                
                content = result.content[0].text
                # Truncate content if too long for TTS
                if len(content) > 1000:
                    content = content[:1000] + "... (content truncated)"
                
                return f"Here's the content from {url}:\n\n{content}"
            
            return f"Sorry, I couldn't fetch content from '{url}'."
            
        except Exception as e:
            logger.error(f"Error in fetch query: {e}")
            return f"Sorry, there was an error fetching content: {str(e)}"
    
    async def _handle_git_query(self, message: str) -> Optional[str]:
        """Handle git-related queries"""
        git_tool = get_active_mcp_manager().find_tool_by_capability("git")
        if not git_tool:
            return "Sorry, git tools are not available right now."
        
        try:
            # Determine git operation from message
            operation = self._extract_git_operation(message)
            if not operation:
                return "I'm not sure which git operation you want to perform."
            
            logger.info(f"Calling git tool with operation: {operation}")
            result = await get_active_mcp_manager().call_tool(git_tool, operation)
            
            if (result and result.content and len(result.content) > 0 
                and hasattr(result.content[0], "text") and result.content[0].text):
                
                return f"Git operation result:\n\n{result.content[0].text}"
            
            return "Git operation completed successfully."
            
        except Exception as e:
            logger.error(f"Error in git query: {e}")
            return f"Sorry, there was an error with the git operation: {str(e)}"
    
    async def _handle_memory_query(self, message: str) -> Optional[str]:
        """Handle memory-related queries"""
        memory_tool = get_active_mcp_manager().find_tool_by_capability("memory")
        if not memory_tool:
            return "Sorry, memory tools are not available right now."
        
        try:
            # Determine if this is a save or recall operation
            if any(word in message.lower() for word in ["remember", "save", "store", "note"]):
                # Save to memory
                content = self._extract_memory_content(message)
                if not content:
                    return "I need content to save to memory."
                
                logger.info(f"Saving to memory: {content}")
                result = await get_active_mcp_manager().call_tool(memory_tool, {"action": "save", "content": content})
                return "I've saved that to memory."
                
            else:
                # Recall from memory
                query = self._extract_memory_query(message)
                logger.info(f"Recalling from memory: {query}")
                result = await get_active_mcp_manager().call_tool(memory_tool, {"action": "recall", "query": query or ""})
                
                if (result and result.content and len(result.content) > 0 
                    and hasattr(result.content[0], "text") and result.content[0].text):
                    
                    return f"From memory:\n\n{result.content[0].text}"
                
                return "I couldn't find anything related to that in my memory."
            
        except Exception as e:
            logger.error(f"Error in memory query: {e}")
            return f"Sorry, there was an error with memory: {str(e)}"
    
    async def _handle_youtube_query(self, message: str) -> Optional[str]:
        """Handle YouTube transcript queries"""
        youtube_tool = get_active_mcp_manager().find_tool_by_capability("transcript")
        if not youtube_tool:
            return "Sorry, YouTube transcript tools are not available right now."
        
        try:
            # Extract YouTube URL from message
            url = self._extract_youtube_url(message)
            if not url:
                return "I need a YouTube URL to get the transcript. Please provide a valid YouTube link."
            
            logger.info(f"Getting YouTube transcript for: {url}")
            result = await get_active_mcp_manager().call_tool(youtube_tool, {"url": url})
            
            if (result and result.content and len(result.content) > 0 
                and hasattr(result.content[0], "text") and result.content[0].text):
                
                transcript = result.content[0].text
                # Truncate if too long for TTS
                if len(transcript) > 2000:
                    transcript = transcript[:2000] + "... (transcript truncated)"
                
                return f"Here's the transcript from the YouTube video:\n\n{transcript}"
            
            return f"Sorry, I couldn't get the transcript from that YouTube video."
            
        except Exception as e:
            logger.error(f"Error in YouTube query: {e}")
            return f"Sorry, there was an error getting the transcript: {str(e)}"
    
    async def _handle_wikipedia_query(self, message: str) -> Optional[str]:
        """Handle Wikipedia queries"""
        wikipedia_tool = get_active_mcp_manager().find_tool_by_capability("wikipedia")
        if not wikipedia_tool:
            return "Sorry, Wikipedia tools are not available right now."
        
        try:
            # Extract search query from message
            query = self._extract_wikipedia_query(message)
            if not query:
                return "I need a topic to search for on Wikipedia."
            
            logger.info(f"Searching Wikipedia for: {query}")
            result = await get_active_mcp_manager().call_tool(wikipedia_tool, {"query": query})
            
            if (result and result.content and len(result.content) > 0 
                and hasattr(result.content[0], "text") and result.content[0].text):
                
                content = result.content[0].text
                # Truncate if too long for TTS
                if len(content) > 1500:
                    content = content[:1500] + "... (content truncated)"
                
                return f"From Wikipedia about '{query}':\n\n{content}"
            
            return f"Sorry, I couldn't find information about '{query}' on Wikipedia."
            
        except Exception as e:
            logger.error(f"Error in Wikipedia query: {e}")
            return f"Sorry, there was an error searching Wikipedia: {str(e)}"
    
    def _parse_timezone_from_message(self, message: str) -> Tuple[Optional[str], Optional[str]]:
        """Parse timezone from a user's message"""
        translator = str.maketrans("", "", string.punctuation)
        clean_content = message.translate(translator).lower()
        
        if " in " not in clean_content:
            return None, None
        
        try:
            location_query = clean_content.split(" in ", 1)[1].strip()
            
            # Remove common trailing phrases that shouldn't be part of timezone
            for suffix in ["using mcp tools", "with mcp", "please", "now", "currently"]:
                if location_query.endswith(suffix):
                    location_query = location_query[:-len(suffix)].strip()
            
            # Check our timezone map first
            if location_query in self.timezone_map:
                return self.timezone_map[location_query], location_query.title()
            
            # Try to extract from original message
            original_parts = message.rsplit(" in ", 1)
            if len(original_parts) == 2:
                potential_timezone = original_parts[1].strip().rstrip(string.punctuation)
                
                # Remove trailing phrases from original timezone too
                for suffix in ["using MCP tools", "with MCP", ", please", " now", " currently"]:
                    if potential_timezone.endswith(suffix):
                        potential_timezone = potential_timezone[:-len(suffix)].strip()
                
                # Check if cleaned timezone is in our map
                potential_lower = potential_timezone.lower()
                if potential_lower in self.timezone_map:
                    return self.timezone_map[potential_lower], potential_timezone
                
                return potential_timezone, potential_timezone
                
        except Exception as e:
            logger.error(f"Error parsing timezone: {e}")
        
        return None, None
    
    def _extract_search_query(self, message: str) -> Optional[str]:
        """Extract the search query from a user message"""
        triggers = [
            "search the web for",
            "search for", 
            "look up",
            "find information about",
            "tell me about",
            "find me",
            "what is",
            "who is",
            "search",
        ]
        
        message_lower = message.lower()
        original_message = message
        
        for trigger in triggers:
            if trigger in message_lower:
                start_index = message_lower.find(trigger) + len(trigger)
                query = original_message[start_index:].strip()
                if query:
                    return query
        
        return None
    
    def _format_search_results(self, search_results_text: str, query: str) -> str:
        """Format search results into a nice readable format"""
        try:
            import json
            
            # Try to parse as JSON first
            try:
                data = json.loads(search_results_text)
                
                # Handle different JSON structures
                if isinstance(data, dict):
                    # Single result format
                    if 'url' in data and 'title' in data:
                        return self._format_single_result(data, query)
                    # Multiple results or different structure
                    else:
                        return self._format_json_results(data, query)
                elif isinstance(data, list):
                    # List of results
                    return self._format_list_results(data, query)
                    
            except json.JSONDecodeError:
                # If not JSON, try to parse as structured text
                return self._format_text_results(search_results_text, query)
                
        except Exception as e:
            logger.error(f"Error formatting search results: {e}")
            # Fallback: just clean up the raw text a bit
            clean_text = search_results_text.replace('{"', '').replace('"}', '').replace(',"', '. ')
            return f"Search results for '{query}':\n\n{clean_text[:500]}..."
    
    def _format_single_result(self, data: dict, query: str) -> str:
        """Format a single search result from JSON"""
        title = data.get('title', 'No Title')
        description = data.get('description', '')
        url = data.get('url', '')
        
        # Clean HTML from description
        clean_description = self._clean_html(description)
        
        # Extract extra snippets if available
        snippets = data.get('extra_snippets', [])
        
        result = f"Based on my search for '{query}', here's what I found:\n\n"
        result += f"**{title}**\n"
        result += f"{clean_description}\n\n"
        
        if snippets:
            result += "Key highlights from critics:\n"
            for snippet in snippets[:3]:  # Limit to first 3 snippets
                clean_snippet = self._clean_html(snippet)
                # Truncate long snippets
                if len(clean_snippet) > 200:
                    clean_snippet = clean_snippet[:200] + "..."
                result += f"- {clean_snippet}\n"
        
        return result
    
    def _format_json_results(self, data: dict, query: str) -> str:
        """Format JSON search results"""
        result = f"Here's what I found searching for '{query}':\n\n"
        
        # Try to extract meaningful information from the JSON
        for key, value in data.items():
            if key in ['title', 'description', 'summary']:
                clean_value = self._clean_html(str(value))
                result += f"**{key.title()}:** {clean_value}\n\n"
            elif key == 'extra_snippets' and isinstance(value, list):
                result += "**Key Points:**\n"
                for snippet in value[:3]:  # Limit snippets
                    clean_snippet = self._clean_html(str(snippet))
                    if len(clean_snippet) > 150:
                        clean_snippet = clean_snippet[:150] + "..."
                    result += f"- {clean_snippet}\n"
        
        return result
    
    def _format_list_results(self, data: list, query: str) -> str:
        """Format a list of search results"""
        result = f"Here are the top search results for '{query}':\n\n"
        
        for i, item in enumerate(data[:3], 1):  # Limit to top 3 results
            if isinstance(item, dict):
                title = item.get('title', f'Result {i}')
                description = item.get('description', '')
                clean_description = self._clean_html(description)
                
                result += f"**{i}. {title}**\n"
                if clean_description:
                    if len(clean_description) > 150:
                        clean_description = clean_description[:150] + "..."
                    result += f"{clean_description}\n\n"
        
        return result
    
    def _format_text_results(self, search_results_text: str, query: str) -> str:
        """Format text-based search results (fallback)"""
        # Parse the text response into structured list
        entries = search_results_text.strip().split("\n\n")
        formatted_results = []
        
        for entry in entries:
            lines = entry.strip().split("\n")
            title = lines[0].replace("Title: ", "").strip() if len(lines) > 0 else "No Title"
            description = lines[1].replace("Description: ", "").strip() if len(lines) > 1 else "No Description"
            
            # Clean HTML from description
            clean_description = self._clean_html(description)
            formatted_results.append(f"**{title}**\n{clean_description}\n")
        
        if formatted_results:
            return f"Here are the search results for '{query}':\n\n" + "\n".join(formatted_results)
        else:
            return f"Search results for '{query}':\n\n{search_results_text}"
    
    def _clean_html(self, raw_html: str) -> str:
        """Remove HTML tags from a string"""
        cleanr = re.compile("<.*?>")
        cleantext = re.sub(cleanr, "", raw_html)
        return cleantext
    
    def _extract_url_from_message(self, message: str) -> Optional[str]:
        """Extract URL from message"""
        import re
        url_pattern = r'https?://[^\s]+'
        match = re.search(url_pattern, message)
        return match.group(0) if match else None
    
    def _extract_git_operation(self, message: str) -> Optional[Dict[str, Any]]:
        """Extract git operation from message"""
        message_lower = message.lower()
        
        if "status" in message_lower:
            return {"operation": "status"}
        elif "log" in message_lower:
            return {"operation": "log", "limit": 5}
        elif "branch" in message_lower:
            return {"operation": "branch"}
        elif "commit" in message_lower:
            # Extract commit message if provided
            if "message" in message_lower:
                # Try to extract message after "message:" or similar
                parts = message.split("message")
                if len(parts) > 1:
                    commit_msg = parts[1].strip().strip(":").strip()
                    return {"operation": "commit", "message": commit_msg}
            return {"operation": "commit", "message": "Auto commit via MCP"}
        
        return None
    
    def _extract_memory_content(self, message: str) -> Optional[str]:
        """Extract content to save to memory"""
        triggers = ["remember", "save", "store", "note"]
        
        for trigger in triggers:
            if trigger in message.lower():
                # Find content after the trigger
                index = message.lower().find(trigger)
                content = message[index + len(trigger):].strip()
                
                # Remove common connecting words
                for word in ["this:", "that:", "this", "that"]:
                    if content.lower().startswith(word):
                        content = content[len(word):].strip()
                
                return content if content else None
        
        return None
    
    def _extract_memory_query(self, message: str) -> Optional[str]:
        """Extract query for memory recall"""
        triggers = ["what did", "recall", "remember", "what was"]
        
        for trigger in triggers:
            if trigger in message.lower():
                # Use everything after the trigger as the query
                index = message.lower().find(trigger)
                query = message[index + len(trigger):].strip()
                return query if query else None
        
        # If no specific trigger, use the whole message as query
        return message
    
    def _extract_youtube_url(self, message: str) -> Optional[str]:
        """Extract YouTube URL from message"""
        import re
        
        # YouTube URL patterns
        patterns = [
            r'https?://(?:www\.)?youtube\.com/watch\?v=([^&\s]+)',
            r'https?://(?:www\.)?youtu\.be/([^&\s]+)',
            r'youtube\.com/watch\?v=([^&\s]+)',
            r'youtu\.be/([^&\s]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, message)
            if match:
                video_id = match.group(1)
                return f"https://www.youtube.com/watch?v={video_id}"
        
        return None
    
    def _extract_wikipedia_query(self, message: str) -> Optional[str]:
        """Extract Wikipedia search query from message"""
        triggers = ["what is", "who is", "tell me about", "define", "explain", "facts about", "information about"]
        
        message_lower = message.lower()
        
        for trigger in triggers:
            if trigger in message_lower:
                # Find content after the trigger
                index = message_lower.find(trigger)
                query = message[index + len(trigger):].strip()
                
                # Remove common question words
                for word in ["the", "a", "an"]:
                    if query.lower().startswith(word + " "):
                        query = query[len(word) + 1:].strip()
                
                # Remove trailing question marks
                query = query.rstrip("?")
                
                return query if query else None
        
        # If no trigger found, use the whole message
        return message.strip("?")

# Global instance
tool_processor = MCPToolProcessor()
