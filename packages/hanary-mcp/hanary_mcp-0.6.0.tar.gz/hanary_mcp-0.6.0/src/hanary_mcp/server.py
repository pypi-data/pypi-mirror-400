"""Hanary MCP Server implementation."""

import argparse
import os
import sys

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from .client import HanaryClient


def create_server(squad: str | None, client: HanaryClient) -> Server:
    """Create and configure the MCP server."""
    server = Server("hanary")

    # Determine mode description
    if squad:
        task_scope = f"squad '{squad}'"
    else:
        task_scope = "personal tasks (including assigned squad tasks)"

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        tools = [
            Tool(
                name="list_tasks",
                description=f"List tasks for {task_scope}.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "include_completed": {
                            "type": "boolean",
                            "description": "Include completed tasks (default: false)",
                        }
                    },
                },
            ),
            Tool(
                name="create_task",
                description=f"Create a new task in {task_scope}.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "title": {"type": "string", "description": "Task title (required)"},
                        "description": {
                            "type": "string",
                            "description": "Task description (optional)",
                        },
                        "parent_id": {
                            "type": "string",
                            "description": "Parent task ID for subtask (optional)",
                        },
                    },
                    "required": ["title"],
                },
            ),
            Tool(
                name="update_task",
                description="Update an existing task's title or description.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "task_id": {"type": "string", "description": "Task ID (required)"},
                        "title": {"type": "string", "description": "New title (optional)"},
                        "description": {
                            "type": "string",
                            "description": "New description (optional)",
                        },
                    },
                    "required": ["task_id"],
                },
            ),
            Tool(
                name="complete_task",
                description="Mark a task as completed.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "type": "string",
                            "description": "Task ID to complete (required)",
                        }
                    },
                    "required": ["task_id"],
                },
            ),
            Tool(
                name="uncomplete_task",
                description="Mark a completed task as incomplete.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "type": "string",
                            "description": "Task ID to uncomplete (required)",
                        }
                    },
                    "required": ["task_id"],
                },
            ),
            Tool(
                name="delete_task",
                description="Soft delete a task.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "type": "string",
                            "description": "Task ID to delete (required)",
                        }
                    },
                    "required": ["task_id"],
                },
            ),
            Tool(
                name="get_top_task",
                description="Get the highest priority incomplete task. Returns the deepest uncompleted task along with its ancestor chain.",
                inputSchema={"type": "object", "properties": {}},
            ),
            Tool(
                name="start_task",
                description="Start time tracking for a task. Creates a new time session.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "type": "string",
                            "description": "Task ID to start time tracking (required)",
                        }
                    },
                    "required": ["task_id"],
                },
            ),
            Tool(
                name="stop_task",
                description="Stop time tracking for a task. Ends the current time session.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "type": "string",
                            "description": "Task ID to stop time tracking (required)",
                        }
                    },
                    "required": ["task_id"],
                },
            ),
            Tool(
                name="reorder_task",
                description="Change the order of a task among its siblings. Moves the task to the specified rank position.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "type": "string",
                            "description": "Task ID to reorder (required)",
                        },
                        "new_rank": {
                            "type": "integer",
                            "description": "New rank position (0-based index among siblings, required)",
                        },
                    },
                    "required": ["task_id", "new_rank"],
                },
            ),
            # Calibration tools (Self-Calibration feature)
            Tool(
                name="get_weekly_stats",
                description="Get weekly task completion statistics for the past 4 weeks. Returns weekly averages of time spent on tasks.",
                inputSchema={"type": "object", "properties": {}},
            ),
            Tool(
                name="get_estimation_accuracy",
                description="Get estimation accuracy statistics. Returns the ratio of actual time spent vs estimated time. Ratio > 1.0 means underestimating, < 1.0 means overestimating.",
                inputSchema={"type": "object", "properties": {}},
            ),
            Tool(
                name="suggest_duration",
                description="Get suggested duration for a task based on similar completed tasks. Useful for setting realistic time estimates.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "type": "string",
                            "description": "Task ID to get suggestion for (required)",
                        }
                    },
                    "required": ["task_id"],
                },
            ),
            Tool(
                name="detect_overload",
                description="Detect overload signals. Checks for: tasks taking 2x longer than estimated, stale tasks (7+ days incomplete), low completion rate.",
                inputSchema={"type": "object", "properties": {}},
            ),
            Tool(
                name="detect_underload",
                description="Detect underload signals. Checks if tasks are being completed in less than 50% of estimated time.",
                inputSchema={"type": "object", "properties": {}},
            ),
        ]

        # Add squad-only tools when squad is specified
        if squad:
            tools.extend([
                Tool(
                    name="get_squad",
                    description="Get details of the current squad.",
                    inputSchema={"type": "object", "properties": {}},
                ),
                Tool(
                    name="list_squad_members",
                    description="List members of the current squad.",
                    inputSchema={"type": "object", "properties": {}},
                ),
                Tool(
                    name="list_messages",
                    description="List messages in the current squad.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "limit": {
                                "type": "integer",
                                "description": "Number of messages to retrieve (default: 50)",
                            }
                        },
                    },
                ),
                Tool(
                    name="create_message",
                    description="Send a message to the current squad.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "content": {
                                "type": "string",
                                "description": "Message content (required)",
                            }
                        },
                        "required": ["content"],
                    },
                ),
            ])

        return tools

    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[TextContent]:
        try:
            result = await handle_tool_call(name, arguments, squad, client)
            return [TextContent(type="text", text=result)]
        except Exception as e:
            return [TextContent(type="text", text=f"Error: {str(e)}")]

    return server


async def handle_tool_call(
    name: str, arguments: dict, squad: str | None, client: HanaryClient
) -> str:
    """Handle individual tool calls."""
    # Task tools
    if name == "list_tasks":
        return await client.list_tasks(
            squad_slug=squad,
            include_completed=arguments.get("include_completed", False),
        )

    elif name == "create_task":
        return await client.create_task(
            title=arguments["title"],
            squad_slug=squad,
            description=arguments.get("description"),
            parent_id=arguments.get("parent_id"),
        )

    elif name == "update_task":
        return await client.update_task(
            task_id=arguments["task_id"],
            title=arguments.get("title"),
            description=arguments.get("description"),
        )

    elif name == "complete_task":
        return await client.complete_task(task_id=arguments["task_id"])

    elif name == "uncomplete_task":
        return await client.uncomplete_task(task_id=arguments["task_id"])

    elif name == "delete_task":
        return await client.delete_task(task_id=arguments["task_id"])

    elif name == "get_top_task":
        return await client.get_top_task(squad_slug=squad)

    elif name == "start_task":
        return await client.start_task(task_id=arguments["task_id"])

    elif name == "stop_task":
        return await client.stop_task(task_id=arguments["task_id"])

    elif name == "reorder_task":
        return await client.reorder_task(
            task_id=arguments["task_id"],
            new_rank=arguments["new_rank"],
        )

    # Calibration tools
    elif name == "get_weekly_stats":
        return await client.get_weekly_stats()

    elif name == "get_estimation_accuracy":
        return await client.get_estimation_accuracy()

    elif name == "suggest_duration":
        return await client.suggest_duration(task_id=arguments["task_id"])

    elif name == "detect_overload":
        return await client.detect_overload()

    elif name == "detect_underload":
        return await client.detect_underload()

    # Squad tools
    elif name == "get_squad":
        return await client.get_squad(squad_slug=squad)

    elif name == "list_squad_members":
        return await client.list_squad_members(squad_slug=squad)

    # Message tools
    elif name == "list_messages":
        return await client.list_messages(
            squad_slug=squad,
            limit=arguments.get("limit", 50),
        )

    elif name == "create_message":
        return await client.create_message(
            squad_slug=squad,
            content=arguments["content"],
        )

    else:
        raise ValueError(f"Unknown tool: {name}")


async def run_server(squad: str | None, api_token: str, api_url: str):
    """Run the MCP server."""
    client = HanaryClient(api_token=api_token, api_url=api_url)
    server = create_server(squad, client)

    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Hanary MCP Server - Task management for Claude Code"
    )
    parser.add_argument(
        "--squad",
        "-s",
        default=None,
        help="Squad slug to bind to. If not specified, manages personal tasks.",
    )
    parser.add_argument(
        "--token",
        "-t",
        default=os.environ.get("HANARY_API_TOKEN"),
        help="Hanary API token (or set HANARY_API_TOKEN env var)",
    )
    parser.add_argument(
        "--api-url",
        default=os.environ.get("HANARY_API_URL", "https://hanary.org"),
        help="Hanary API URL (default: https://hanary.org)",
    )

    args = parser.parse_args()

    # Get API token from argument or environment
    api_token = args.token
    if not api_token:
        print("Error: --token argument or HANARY_API_TOKEN environment variable is required", file=sys.stderr)
        sys.exit(1)

    import asyncio

    asyncio.run(run_server(args.squad, api_token, args.api_url))


if __name__ == "__main__":
    main()
