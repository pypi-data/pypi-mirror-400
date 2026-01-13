#!/usr/bin/env python3
"""
DaVinci Resolve MCP Server
Provides MCP tools for controlling DaVinci Resolve via its Python scripting API.
"""

import asyncio
import json
from typing import Any
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from .resolve_api import get_connection, ResolveConnection

# Create the MCP server
server = Server("davinci-resolve-mcp")


def get_resolve() -> ResolveConnection:
    """Get connected Resolve instance."""
    conn = get_connection()
    if not conn.is_connected:
        conn.connect()
    return conn


# ==================== Tool Definitions ====================

@server.list_tools()
async def list_tools() -> list[Tool]:
    """List all available DaVinci Resolve tools."""
    return [
        # Connection & Info
        Tool(
            name="resolve_connect",
            description="Connect to running DaVinci Resolve instance. Must be called before other operations.",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="resolve_get_version",
            description="Get DaVinci Resolve version and product info",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),

        # Project Management
        Tool(
            name="resolve_list_projects",
            description="List all projects in the current database",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="resolve_get_current_project",
            description="Get the name of the currently open project",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="resolve_create_project",
            description="Create a new project",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Name for the new project"}
                },
                "required": ["name"],
            },
        ),
        Tool(
            name="resolve_open_project",
            description="Open an existing project by name",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Name of the project to open"}
                },
                "required": ["name"],
            },
        ),
        Tool(
            name="resolve_save_project",
            description="Save the current project",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="resolve_close_project",
            description="Close the current project",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),

        # Timeline Operations
        Tool(
            name="resolve_list_timelines",
            description="List all timelines in the current project",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="resolve_get_current_timeline",
            description="Get info about the current timeline",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="resolve_create_timeline",
            description="Create a new empty timeline",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Name for the new timeline"}
                },
                "required": ["name"],
            },
        ),
        Tool(
            name="resolve_set_current_timeline",
            description="Switch to a timeline by name",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Name of the timeline to switch to"}
                },
                "required": ["name"],
            },
        ),

        # Media Pool
        Tool(
            name="resolve_import_media",
            description="Import media files into the media pool",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_paths": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of file paths to import"
                    }
                },
                "required": ["file_paths"],
            },
        ),
        Tool(
            name="resolve_list_media_pool",
            description="List items in the media pool root folder",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="resolve_create_bin",
            description="Create a new bin/folder in the media pool",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Name for the new bin"}
                },
                "required": ["name"],
            },
        ),

        # Markers
        Tool(
            name="resolve_add_marker",
            description="Add a marker to the current timeline",
            inputSchema={
                "type": "object",
                "properties": {
                    "frame": {"type": "integer", "description": "Frame number for the marker"},
                    "color": {
                        "type": "string",
                        "description": "Marker color (Blue, Cyan, Green, Yellow, Red, Pink, Purple, Fuchsia, Rose, Lavender, Sky, Mint, Lemon, Sand, Cocoa, Cream)",
                        "default": "Blue"
                    },
                    "name": {"type": "string", "description": "Marker name", "default": ""},
                    "note": {"type": "string", "description": "Marker note/comment", "default": ""},
                    "duration": {"type": "integer", "description": "Marker duration in frames", "default": 1}
                },
                "required": ["frame"],
            },
        ),
        Tool(
            name="resolve_get_markers",
            description="Get all markers from the current timeline",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="resolve_delete_marker",
            description="Delete a marker at the specified frame",
            inputSchema={
                "type": "object",
                "properties": {
                    "frame": {"type": "integer", "description": "Frame number of the marker to delete"}
                },
                "required": ["frame"],
            },
        ),

        # Render
        Tool(
            name="resolve_get_render_presets",
            description="Get list of available render presets",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="resolve_set_render_preset",
            description="Set the render preset",
            inputSchema={
                "type": "object",
                "properties": {
                    "preset_name": {"type": "string", "description": "Name of the render preset"}
                },
                "required": ["preset_name"],
            },
        ),
        Tool(
            name="resolve_add_render_job",
            description="Add current timeline to the render queue",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="resolve_start_render",
            description="Start rendering all jobs in the queue",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="resolve_get_render_status",
            description="Get current render status",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),

        # Page Navigation
        Tool(
            name="resolve_open_page",
            description="Open a specific page in DaVinci Resolve",
            inputSchema={
                "type": "object",
                "properties": {
                    "page": {
                        "type": "string",
                        "description": "Page to open: media, cut, edit, fusion, color, fairlight, deliver",
                        "enum": ["media", "cut", "edit", "fusion", "color", "fairlight", "deliver"]
                    }
                },
                "required": ["page"],
            },
        ),
        Tool(
            name="resolve_get_current_page",
            description="Get the currently open page",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),

        # Playback
        Tool(
            name="resolve_set_playhead",
            description="Set the playhead position to a specific frame",
            inputSchema={
                "type": "object",
                "properties": {
                    "frame": {"type": "integer", "description": "Frame number to move playhead to"}
                },
                "required": ["frame"],
            },
        ),
    ]


# ==================== Tool Handlers ====================

@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Handle tool calls."""
    resolve = get_resolve()

    try:
        result = await handle_tool(name, arguments, resolve)
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    except Exception as e:
        return [TextContent(type="text", text=json.dumps({"error": str(e)}))]


async def handle_tool(name: str, args: dict[str, Any], resolve: ResolveConnection) -> dict:
    """Route tool calls to appropriate handlers."""

    # Connection & Info
    if name == "resolve_connect":
        success = resolve.connect()
        return {
            "connected": success,
            "version": resolve.get_version() if success else None,
            "product": resolve.get_product_name() if success else None,
        }

    if name == "resolve_get_version":
        return {
            "version": resolve.get_version(),
            "product": resolve.get_product_name(),
            "connected": resolve.is_connected,
        }

    # Project Management
    if name == "resolve_list_projects":
        return {"projects": resolve.list_projects()}

    if name == "resolve_get_current_project":
        return {"project": resolve.get_project_name()}

    if name == "resolve_create_project":
        success = resolve.create_project(args["name"])
        return {"success": success, "project": args["name"]}

    if name == "resolve_open_project":
        success = resolve.open_project(args["name"])
        return {"success": success, "project": args["name"]}

    if name == "resolve_save_project":
        success = resolve.save_project()
        return {"success": success}

    if name == "resolve_close_project":
        success = resolve.close_project()
        return {"success": success}

    # Timeline Operations
    if name == "resolve_list_timelines":
        return {"timelines": resolve.list_timelines()}

    if name == "resolve_get_current_timeline":
        info = resolve.get_timeline_info()
        return {"timeline": info}

    if name == "resolve_create_timeline":
        success = resolve.create_timeline(args["name"])
        return {"success": success, "timeline": args["name"]}

    if name == "resolve_set_current_timeline":
        success = resolve.set_current_timeline(args["name"])
        return {"success": success, "timeline": args["name"]}

    # Media Pool
    if name == "resolve_import_media":
        clips = resolve.import_media(args["file_paths"])
        return {"imported": clips, "count": len(clips)}

    if name == "resolve_list_media_pool":
        return {"items": resolve.list_media_pool_items()}

    if name == "resolve_create_bin":
        success = resolve.create_bin(args["name"])
        return {"success": success, "bin": args["name"]}

    # Markers
    if name == "resolve_add_marker":
        success = resolve.add_marker(
            frame=args["frame"],
            color=args.get("color", "Blue"),
            name=args.get("name", ""),
            note=args.get("note", ""),
            duration=args.get("duration", 1),
        )
        return {"success": success, "frame": args["frame"]}

    if name == "resolve_get_markers":
        return {"markers": resolve.get_markers()}

    if name == "resolve_delete_marker":
        success = resolve.delete_marker(args["frame"])
        return {"success": success, "frame": args["frame"]}

    # Render
    if name == "resolve_get_render_presets":
        return {"presets": resolve.get_render_presets()}

    if name == "resolve_set_render_preset":
        success = resolve.set_render_preset(args["preset_name"])
        return {"success": success, "preset": args["preset_name"]}

    if name == "resolve_add_render_job":
        job_id = resolve.add_render_job()
        return {"job_id": job_id, "success": bool(job_id)}

    if name == "resolve_start_render":
        success = resolve.start_render()
        return {"success": success}

    if name == "resolve_get_render_status":
        return resolve.get_render_status()

    # Page Navigation
    if name == "resolve_open_page":
        success = resolve.open_page(args["page"])
        return {"success": success, "page": args["page"]}

    if name == "resolve_get_current_page":
        return {"page": resolve.get_current_page()}

    # Playback
    if name == "resolve_set_playhead":
        success = resolve.set_playhead_position(args["frame"])
        return {"success": success, "frame": args["frame"]}

    return {"error": f"Unknown tool: {name}"}


def main():
    """Main entry point for the MCP server."""
    async def run():
        async with stdio_server() as (read_stream, write_stream):
            await server.run(read_stream, write_stream, server.create_initialization_options())

    asyncio.run(run())


if __name__ == "__main__":
    main()
