# Example chainlit app using the mcp time server and Brave Search MCP server
#
import chainlit as cl
from mcp import ClientSession
from dateutil import parser
import string
import json
import os
from dotenv import load_dotenv
import re

# Load environment variables from .env file
load_dotenv()


def clean_html(raw_html):
    """Removes HTML tags from a string."""
    cleanr = re.compile("<.*?>")
    cleantext = re.sub(cleanr, "", raw_html)
    return cleantext


@cl.on_chat_start
async def start_chat():
    """
    This function is called when a new chat session starts.
    It checks for the Brave API key, sends a welcome message,
    and initializes a dictionary to store discovered MCP tools.
    """
    # Initialize a dictionary in the user session to store discovered tools
    cl.user_session.set("mcp_tools", {})

    if not os.environ.get("BRAVE_API_KEY"):
        await cl.Message(
            content="**Brave API Key not found!**\n\n"
        ).send()
    else:
        await cl.Message(
            content="**Welcome! I am a Time and Search Bot.**\n\n"
            "I can get the current time or search the web for information.\n\n"
            "**Try asking me:**\n"
            "- `What time is it in Los Angeles?`\n"
            "- `Search for new movies in Los Angeles`"
        ).send()


@cl.on_mcp_connect
async def on_mcp_connect(connection, session: ClientSession):
    """
    This function is called when an MCP connection is established.
    It discovers the available tools for that server and stores them.
    """
    print(f"MCP connection successful for: {connection.name}")
    try:
        # Query the server for its list of available tools
        tool_list_result = await session.list_tools()
        mcp_tools = cl.user_session.get("mcp_tools")

        # Store each discovered tool and the session it belongs to
        for tool in tool_list_result.tools:
            mcp_tools[tool.name] = {
                "session_name": connection.name,
                "description": tool.description,
            }

        cl.user_session.set("mcp_tools", mcp_tools)
        print(
            f"Discovered tools for {connection.name}: {[t.name for t in tool_list_result.tools]}"
        )
    except Exception as e:
        print(f"Could not list tools for {connection.name}: {e}")


@cl.on_message
async def main(message: cl.Message):
    """
    This function is called for every user message. It decides whether to
    call the time tool or the search tool based on the message content.
    """
    clean_content = message.content.lower()

    if "search" in clean_content or "what is" in clean_content or "who is" in clean_content:
        await handle_search_query(message)
    elif "time" in clean_content and " in " in clean_content:
        await handle_time_query(message)
    else:
        await cl.Message(
            content="Sorry, I didn't understand. Please ask me to `search for...` something or get the `time in...` a location."
        ).send()


def find_mcp_tool(capability: str):
    """
    Finds a tool and its session name by looking for a capability
    (e.g., 'time', 'search') in the tool's name from the discovered tools.
    """
    mcp_tools = cl.user_session.get("mcp_tools", {})
    for tool_name, tool_info in mcp_tools.items():
        if capability in tool_name:
            return tool_info["session_name"], tool_name
    return None, None


def parse_timezone_from_message(message: cl.Message):
    """
    A helper function to parse the timezone from a user's message.
    Returns the IANA timezone and a display name.
    """
    translator = str.maketrans("", "", string.punctuation)
    clean_content = message.content.translate(translator).lower()

    if " in " not in clean_content:
        return None, None

    try:
        location_query = clean_content.split(" in ", 1)[1].strip()
        timezone_map = {
            "london": "Europe/London",
            "paris": "Europe/Paris",
            "tokyo": "Asia/Tokyo",
            "new york": "America/New_York",
            "los angeles": "America/Los_Angeles",
            "la": "America/Los_Angeles",
        }
        if location_query in timezone_map:
            return timezone_map[location_query], location_query.title()
        else:
            original_content = message.content
            parts = original_content.rsplit(" in ", 1)
            if len(parts) == 2:
                potential_timezone = parts[1].strip().rstrip(string.punctuation)
                return potential_timezone, potential_timezone
    except Exception as e:
        print(f"Error parsing timezone: {e}")

    return None, None


async def handle_time_query(message: cl.Message):
    """
    Handles queries related to getting the current time by dynamically finding a time tool.
    """
    session_name, tool_name = find_mcp_tool("time")
    if not session_name or not tool_name:
        await cl.Message(
            content="A 'time' tool could not be found among the connected MCP servers."
        ).send()
        return

    mcp_connection = cl.context.session.mcp_sessions.get(session_name)
    if not mcp_connection:
        await cl.Message(
            content=f"Time server session '{session_name}' is not connected."
        ).send()
        return

    session, _ = mcp_connection
    timezone, display_name = parse_timezone_from_message(message)
    tool_params = {"timezone": timezone} if timezone else {}

    async with cl.Step(type="tool", name=tool_name) as step:
        step.input = tool_params
        try:
            result = await session.call_tool(tool_name, tool_params)
            print(f"Raw time tool result: {result}")
            step.output = result

            parsed_result = None
            if (
                result
                and result.content
                and len(result.content) > 0
                and hasattr(result.content[0], "text")
            ):
                try:
                    if "Error processing" in result.content[0].text:
                        parsed_result = {"error": result.content[0].text}
                    else:
                        parsed_result = json.loads(result.content[0].text)
                except json.JSONDecodeError:
                    pass

            if parsed_result and "datetime" in parsed_result:
                dt_object = parser.isoparse(parsed_result["datetime"])
                formatted_time = dt_object.strftime("%A, %B %d, %Y at %I:%M %p")
                response_timezone = parsed_result.get("timezone", display_name)
                await cl.Message(
                    content=f"The current time in **{response_timezone}** is **{formatted_time}**."
                ).send()
            else:
                error_message = (
                    parsed_result.get("error")
                    if isinstance(parsed_result, dict)
                    else "unexpected or empty response"
                )
                location_for_error = display_name or "the specified location"
                await cl.Message(
                    content=f"Sorry, the time tool returned an error for **{location_for_error}**: `{error_message}`"
                ).send()

        except Exception as e:
            step.output = {"error": str(e)}
            await cl.Message(
                content=f"A critical error occurred with the time tool: {e}"
            ).send()


async def handle_search_query(message: cl.Message):
    """
    Handles queries related to searching the web by dynamically finding a search tool.
    """
    if not os.environ.get("BRAVE_API_KEY"):
        await cl.Message(
            content="Cannot perform search. The Brave API Key is not configured."
        ).send()
        return

    session_name, tool_name = find_mcp_tool("search")
    if not session_name or not tool_name:
        await cl.Message(
            content="A 'search' tool could not be found among the connected MCP servers."
        ).send()
        return

    mcp_connection = cl.context.session.mcp_sessions.get(session_name)
    if not mcp_connection:
        await cl.Message(
            content=f"Search server session '{session_name}' is not connected."
        ).send()
        return

    session, _ = mcp_connection
    query = ""
    triggers = ["search the web for", "search for", "what is", "who is", "search"]
    clean_content = message.content.lower()
    original_content = message.content

    for trigger in triggers:
        if trigger in clean_content:
            start_index = clean_content.find(trigger) + len(trigger)
            query = original_content[start_index:].strip()
            if query:
                break

    if not query:
        await cl.Message(
            content="I'm not sure what you want me to search for. Please be more specific."
        ).send()
        return

    async with cl.Step(type="tool", name=tool_name) as step:
        step.input = {"query": query}
        try:
            result = await session.call_tool(tool_name, {"query": query})
            print(f"Raw search result: {result}")
            step.output = result

            if (
                result
                and result.content
                and len(result.content) > 0
                and hasattr(result.content[0], "text")
                and result.content[0].text
            ):
                search_results_text = result.content[0].text

                # Parse the text response into a structured list and clean HTML
                entries = search_results_text.strip().split("\n\n")
                formatted_results = []
                for entry in entries:
                    lines = entry.strip().split("\n")
                    title = (
                        lines[0].replace("Title: ", "").strip()
                        if len(lines) > 0
                        else "No Title"
                    )
                    description = (
                        lines[1].replace("Description: ", "").strip()
                        if len(lines) > 1
                        else "No Description"
                    )
                    url = (
                        lines[2].replace("URL: ", "").strip() if len(lines) > 2 else None
                    )

                    clean_description = clean_html(description)

                    if url:
                        formatted_results.append(
                            f"**[{title}]({url})**\n   - {clean_description}\n"
                        )
                
                if formatted_results:
                    content = f"Here are the search results for **'{query}'**:\n\n---\n\n" + "\n".join(formatted_results)
                    await cl.Message(content=content).send()
                else:
                    # Fallback if parsing fails but we still have the raw text
                    await cl.Message(content=f"Here are the search results for **'{query}'**:\n\n---\n\n{search_results_text}").send()


            else:
                # This handles cases where the tool returns an error or a truly empty response.
                error_message = "unexpected or empty response"
                await cl.Message(
                    content=f"Sorry, the search tool returned an error for query **'{query}'**: `{error_message}`"
                ).send()

        except Exception as e:
            step.output = {"error": str(e)}
            await cl.Message(
                content=f"A critical error occurred with the search tool: {e}"
            ).send()

