#!/usr/bin/env python3
"""MCP server for controlling Meural Canvas digital art frames."""

import asyncio
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from meural import MeuralAPI

# Lazy-loaded API instance
_api = None


def get_api():
    """Get or create API instance."""
    global _api
    if _api is None:
        _api = MeuralAPI.from_env()
    return _api


# Create MCP server
server = Server("meural")


@server.list_tools()
async def list_tools():
    """List available tools."""
    return [
        Tool(
            name="meural_get_device",
            description="Get Meural device status and info (brightness, current gallery, orientation, etc.)",
            inputSchema={
                "type": "object",
                "properties": {
                    "device_id": {
                        "type": "integer",
                        "description": "Device ID (optional, defaults to first device)"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="meural_list_galleries",
            description="List all user's galleries/playlists with item counts",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="meural_get_gallery",
            description="Get gallery details and list of items in it",
            inputSchema={
                "type": "object",
                "properties": {
                    "gallery_id": {
                        "type": "integer",
                        "description": "Gallery ID"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Max items to return (default: 20)"
                    }
                },
                "required": ["gallery_id"]
            }
        ),
        Tool(
            name="meural_search",
            description="Search for artwork, galleries, artists, or channels on Meural",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query"
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="meural_preview_item",
            description="Temporarily preview an image on the Meural (60 seconds only). Use meural_set_image instead for normal display requests.",
            inputSchema={
                "type": "object",
                "properties": {
                    "item_id": {
                        "type": "integer",
                        "description": "Item ID to display"
                    },
                    "device_id": {
                        "type": "integer",
                        "description": "Device ID (optional, defaults to first device)"
                    }
                },
                "required": ["item_id"]
            }
        ),
        Tool(
            name="meural_push_gallery",
            description="Switch the Meural device to display a gallery/playlist",
            inputSchema={
                "type": "object",
                "properties": {
                    "gallery_id": {
                        "type": "integer",
                        "description": "Gallery ID to display"
                    },
                    "device_id": {
                        "type": "integer",
                        "description": "Device ID (optional, defaults to first device)"
                    }
                },
                "required": ["gallery_id"]
            }
        ),
        Tool(
            name="meural_device_galleries",
            description="List galleries currently on the Meural device",
            inputSchema={
                "type": "object",
                "properties": {
                    "device_id": {
                        "type": "integer",
                        "description": "Device ID (optional, defaults to first device)"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="meural_set_brightness",
            description="Set the brightness level of the Meural device",
            inputSchema={
                "type": "object",
                "properties": {
                    "brightness": {
                        "type": "integer",
                        "description": "Brightness level (0-100)"
                    },
                    "device_id": {
                        "type": "integer",
                        "description": "Device ID (optional, defaults to first device)"
                    }
                },
                "required": ["brightness"]
            }
        ),
        Tool(
            name="meural_set_image",
            description="Set a specific image to display on the Meural. Requires active subscription; falls back to 60-sec preview if inactive.",
            inputSchema={
                "type": "object",
                "properties": {
                    "item_id": {
                        "type": "integer",
                        "description": "Item ID to display"
                    },
                    "device_id": {
                        "type": "integer",
                        "description": "Device ID (optional, defaults to first device)"
                    }
                },
                "required": ["item_id"]
            }
        ),
    ]


def get_default_device_id(api):
    """Get the first device ID if none specified."""
    devices = api.get_devices()
    if not devices:
        return None
    return devices[0].get("id")


@server.call_tool()
async def call_tool(name: str, arguments: dict):
    """Handle tool calls."""
    api = get_api()

    if name == "meural_get_device":
        device_id = arguments.get("device_id") or get_default_device_id(api)
        if not device_id:
            return [TextContent(type="text", text="No devices found")]

        d = api.get_device(device_id=device_id)
        fs = d.get("frameStatus", {})
        model = d.get("frameModel", {})

        lines = [
            f"Device: {d.get('alias', 'Unnamed')}",
            f"  ID: {d.get('id')}",
            f"  Status: {'Online' if d.get('status') == 'online' else 'Offline'}",
            f"  Model: {model.get('name', 'N/A')} ({model.get('sizeInches', '?')}\")",
            f"  Orientation: {d.get('orientation', 'N/A')}",
            f"  Brightness: {fs.get('brightness', 'N/A')}%",
            f"  Current Gallery: {d.get('currentGallery', 'None')}",
            f"  Local IP: {d.get('localIp', 'N/A')}",
            f"  Firmware: {d.get('version', 'N/A')}",
        ]
        return [TextContent(type="text", text="\n".join(lines))]

    elif name == "meural_list_galleries":
        galleries = api.get_user_galleries()
        if not galleries:
            return [TextContent(type="text", text="No galleries found")]

        lines = ["Galleries:"]
        for g in galleries:
            lines.append(f"  {g.get('id')}: {g.get('name', 'Unnamed')} ({g.get('itemCount', 0)} items)")
        return [TextContent(type="text", text="\n".join(lines))]

    elif name == "meural_get_gallery":
        gallery_id = arguments.get("gallery_id")
        limit = arguments.get("limit", 20)

        g = api.get_gallery(gallery_id=gallery_id)
        items = api.get_all_gallery_items(gallery_id=gallery_id)

        lines = [
            f"Gallery: {g.get('name', 'Unnamed')}",
            f"  ID: {g.get('id')}",
            f"  Description: {g.get('description', '')}",
            f"  Total Items: {len(items)}",
            "",
            f"Items (showing {min(limit, len(items))} of {len(items)}):",
        ]
        for item in items[:limit]:
            lines.append(f"  {item.get('id')}: {item.get('name', 'Unnamed')}")

        return [TextContent(type="text", text="\n".join(lines))]

    elif name == "meural_search":
        query = arguments.get("query", "")
        results = api.search(params={"q": query, "page": 1})

        if not results:
            return [TextContent(type="text", text="No results found")]

        lines = [f"Search results for '{query}':"]

        type_map = {
            "items": "Artworks",
            "galleries": "Galleries",
            "artists": "Artists",
            "channels": "Channels",
        }

        for rtype, label in type_map.items():
            items = results.get(rtype, [])
            if items:
                lines.append(f"\n{label}:")
                for r in items[:5]:
                    lines.append(f"  {r.get('id')}: {r.get('name', 'Unnamed')}")

        return [TextContent(type="text", text="\n".join(lines))]

    elif name == "meural_preview_item":
        item_id = arguments.get("item_id")
        device_id = arguments.get("device_id") or get_default_device_id(api)

        if not device_id:
            return [TextContent(type="text", text="No devices found")]

        api.post_device_preview(device_id=device_id, item_id=item_id)
        return [TextContent(type="text", text=f"Now previewing item {item_id} on device {device_id}")]

    elif name == "meural_push_gallery":
        gallery_id = arguments.get("gallery_id")
        device_id = arguments.get("device_id") or get_default_device_id(api)

        if not device_id:
            return [TextContent(type="text", text="No devices found")]

        api.post_device_gallery(device_id=device_id, gallery_id=gallery_id)
        return [TextContent(type="text", text=f"Switched device {device_id} to gallery {gallery_id}")]

    elif name == "meural_device_galleries":
        device_id = arguments.get("device_id") or get_default_device_id(api)

        if not device_id:
            return [TextContent(type="text", text="No devices found")]

        galleries = api.get_device_galleries(device_id=device_id, params={"page": 1, "count": 100})

        if not galleries:
            return [TextContent(type="text", text="No galleries on this device")]

        lines = [f"Galleries on device {device_id}:"]
        for g in galleries:
            owner = "You" if g.get("isOwner") else g.get("ownerName", "")
            lines.append(f"  {g.get('id')}: {g.get('name', 'Unnamed')} ({g.get('itemCount', 0)} items) [{owner}]")

        return [TextContent(type="text", text="\n".join(lines))]

    elif name == "meural_set_brightness":
        brightness = arguments.get("brightness")
        device_id = arguments.get("device_id") or get_default_device_id(api)

        if not device_id:
            return [TextContent(type="text", text="No devices found")]

        # Use local API for brightness control (faster and works when online)
        import requests
        d = api.get_device(device_id=device_id)
        local_ip = d.get("localIp")

        if local_ip:
            try:
                url = f"http://{local_ip}/remote/control_command/set_key/backlight/{brightness}"
                requests.get(url, timeout=5)
                return [TextContent(type="text", text=f"Brightness set to {brightness}% on device {device_id}")]
            except Exception as e:
                return [TextContent(type="text", text=f"Failed to set brightness via local API: {e}")]
        else:
            return [TextContent(type="text", text="Could not find device local IP")]

    elif name == "meural_set_image":
        item_id = arguments.get("item_id")
        device_id = arguments.get("device_id") or get_default_device_id(api)

        if not device_id:
            return [TextContent(type="text", text="No devices found")]

        try:
            api.post_device_item(device_id=device_id, item_id=item_id)
            return [TextContent(type="text", text=f"Set image {item_id} on device {device_id}")]
        except Exception as e:
            if "402" in str(e) or "subscription" in str(e).lower():
                api.post_device_preview(device_id=device_id, item_id=item_id)
                return [TextContent(type="text", text=f"Subscription required to set image. Using preview instead (60 sec).")]
            raise

    else:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]


def main():
    """Run the MCP server."""
    async def run():
        async with stdio_server() as (read_stream, write_stream):
            await server.run(read_stream, write_stream, server.create_initialization_options())

    asyncio.run(run())


if __name__ == "__main__":
    main()
