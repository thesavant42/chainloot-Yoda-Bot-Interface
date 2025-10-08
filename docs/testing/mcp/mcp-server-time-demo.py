# mcp-time-search.py
#
# demo chainlit 2.8.3 app to use mcp servers. This example shows how
# to use the time server.

import chainlit as cl
from mcp import ClientSession
from dateutil import parser
import string
import json # Import the json library to parse the tool's response

@cl.on_chat_start
async def start_chat():
    """
    This function is called when a new chat session starts.
    It connects to the MCP time server and sends a welcome message.
    """
    await cl.Message(
        content="Welcome! I can tell you the current time in any timezone. \n\n"
                "Try asking me: **What time is it in London?** or **What time is it in America/New_York?**"
    ).send()

@cl.on_mcp_connect
async def on_mcp_connect(connection, session: ClientSession):
    """
    This function is called when an MCP connection is established.
    It prints a success message.
    """
    print(f"MCP connection successful for: {connection.name}")


@cl.on_message
async def main(message: cl.Message):
    """
    This function is called every time a user inputs a message in the UI.
    It parses the user's message to get a timezone, calls the 'get_current_time'
    tool from the mcp-server-time, and sends the result back to the user.
    """
    mcp_connection = cl.context.session.mcp_sessions.get("Time")
    
    if not mcp_connection:
        await cl.Message(
            content="Sorry, I'm not connected to the time server. Please try again later."
        ).send()
        return

    session, _ = mcp_connection

    # --- More robust parsing logic ---
    timezone = None
    display_name = None

    # Clean the message content for map lookup (lowercase, no punctuation)
    translator = str.maketrans('', '', string.punctuation)
    clean_content = message.content.translate(translator).lower()

    if " in " in clean_content:
        try:
            # Get the text after " in "
            location_query = clean_content.split(" in ", 1)[1].strip()

            timezone_map = {
                "london": "Europe/London",
                "paris": "Europe/Paris",
                "tokyo": "Asia/Tokyo",
                "new york": "America/New_York",
                "los angeles": "America/Los_Angeles",
                "la": "America/Los_Angeles",
            }

            # Check for an exact match in our map
            if location_query in timezone_map:
                timezone = timezone_map[location_query]
                display_name = location_query.title()
            else:
                # If no map match, assume user typed a case-sensitive IANA timezone
                original_content = message.content
                # Find the last occurrence of " in " (case-insensitive) to handle complex sentences
                parts = original_content.rsplit(" in ", 1)
                if len(parts) == 2:
                    potential_timezone = parts[1].strip().rstrip(string.punctuation)
                    timezone = potential_timezone
                    display_name = potential_timezone
        except Exception as e:
            print(f"Error parsing timezone: {e}")
            pass # Fallback to default if parsing fails

    tool_params = {}
    if timezone:
        tool_params["timezone"] = timezone

    async with cl.Step(type="tool", name="get_current_time") as step:
        step.input = tool_params
        try:
            result = await session.call_tool("get_current_time", tool_params)
            print(f"Raw tool result: {result}")
            step.output = result

            # --- NEW: Correctly parse the nested response ---
            parsed_result = None
            if result and result.content and len(result.content) > 0 and hasattr(result.content[0], 'text'):
                try:
                    parsed_result = json.loads(result.content[0].text)
                except json.JSONDecodeError:
                    pass # The text was not valid JSON

            if parsed_result and 'datetime' in parsed_result:
                dt_object = parser.isoparse(parsed_result['datetime'])
                formatted_time = dt_object.strftime('%A, %B %d, %Y at %I:%M %p')
                # Use the timezone from the result for accuracy
                response_timezone = parsed_result.get('timezone', display_name)
                await cl.Message(
                    content=f"The current time in **{response_timezone}** is **{formatted_time}**."
                ).send()
            else:
                error_message = None
                if isinstance(parsed_result, dict):
                     error_message = parsed_result.get('error')
                
                location_for_error = display_name or "the location you specified"
                
                if error_message:
                    content = f"The time tool reported an error for **{location_for_error}**: `{error_message}`"
                else:
                    content = f"Sorry, the time tool returned an unexpected or empty response for **{location_for_error}**. Please ensure it's a valid location or IANA timezone (e.g., America/New_York)."
                
                await cl.Message(content=content).send()

        except Exception as e:
            step.output = {"error": str(e)}
            await cl.Message(
                content=f"A critical error occurred while trying to get the time: {e}"
            ).send()

