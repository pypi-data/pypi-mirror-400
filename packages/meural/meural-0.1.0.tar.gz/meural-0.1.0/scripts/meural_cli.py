#!/usr/bin/env python3
"""
Meural CLI - Command line interface for Meural Canvas API

Usage:
    python meural_cli.py device list
    python meural_cli.py item upload ~/photos/art.jpg --title "My Art"
    python meural_cli.py gallery create "Favorites" --description "My favorite pieces"
    python meural_cli.py device push 72386 12345

Run `python meural_cli.py --help` for full command list.
"""
import click
import os
import sys
import json
from pathlib import Path
from tabulate import tabulate
from meural import MeuralAPI


# Global API instance (lazy loaded)
_api = None


def get_api():
    """Get or create API instance"""
    global _api
    if _api is None:
        try:
            _api = MeuralAPI.from_env()
        except ValueError as e:
            click.echo(f"Error: {e}", err=True)
            click.echo("Set MEURAL_USERNAME/MEURAL_PASSWORD or create ~/.meural file", err=True)
            sys.exit(1)
    return _api


def format_table(data, headers, keys=None):
    """Format data as a table"""
    if not data:
        return "No results"

    if keys:
        rows = [[item.get(k, "") for k in keys] for item in data]
    else:
        rows = data

    return tabulate(rows, headers=headers, tablefmt="simple")


def truncate(text, length=40):
    """Truncate text to specified length"""
    if not text:
        return ""
    text = str(text)
    return text[:length-3] + "..." if len(text) > length else text


# =============================================================================
# Main CLI Group
# =============================================================================

@click.group()
@click.version_option(version="1.0.0", prog_name="meural")
def cli():
    """Meural Canvas CLI - Manage your Meural devices and content"""
    pass


# =============================================================================
# Auth Commands
# =============================================================================

@cli.group()
def auth():
    """Authentication commands"""
    pass


@auth.command("status")
def auth_status():
    """Show authentication status and user info"""
    api = get_api()
    user = api.get_user()

    click.echo(f"Authenticated as: {user.get('email')}")
    click.echo(f"User ID: {user.get('id')}")
    click.echo(f"Name: {user.get('firstName', '')} {user.get('lastName', '')}")

    devices = api.get_devices()
    click.echo(f"Devices: {len(devices)}")


# =============================================================================
# Device Commands
# =============================================================================

@cli.group()
def device():
    """Device management commands"""
    pass


@device.command("list")
def device_list():
    """List all devices"""
    api = get_api()
    devices = api.get_devices()

    if not devices:
        click.echo("No devices found")
        return

    headers = ["ID", "Name", "Status", "Orientation", "Brightness"]
    rows = []
    for d in devices:
        rows.append([
            d.get("id"),
            d.get("alias") or d.get("name", "Unnamed"),
            "Online" if d.get("status") == "online" else "Offline",
            d.get("orientation", ""),
            f"{d.get('brightness', '')}%",
        ])

    click.echo(format_table(rows, headers))


@device.command("show")
@click.argument("device_id", type=int)
def device_show(device_id):
    """Show device details"""
    api = get_api()
    d = api.get_device(device_id=device_id)

    # Get nested frameStatus data
    fs = d.get('frameStatus', {})
    model = d.get('frameModel', {})

    click.echo(f"Device: {d.get('alias') or d.get('name', 'Unnamed')}")
    click.echo(f"  ID: {d.get('id')}")
    click.echo(f"  Status: {'Online' if d.get('status') == 'online' else 'Offline'}")
    click.echo(f"  Model: {model.get('name', 'N/A')} ({model.get('sizeInches', '?')}\")")
    click.echo(f"  Orientation: {d.get('orientation', 'N/A')}")
    click.echo(f"  Brightness: {fs.get('brightness', 'N/A')}%")
    click.echo(f"  Firmware: {d.get('version', 'N/A')}")
    click.echo(f"  Serial: {d.get('serialNumber', 'N/A')}")
    click.echo(f"  Local IP: {d.get('localIp', 'N/A')}")
    click.echo(f"  Current Gallery: {d.get('currentGallery', 'None')}")
    click.echo(f"  Last Seen: {fs.get('lastSeen', 'N/A')}")


@device.command("galleries")
@click.argument("device_id", type=int)
def device_galleries(device_id):
    """List galleries on a device"""
    api = get_api()
    galleries = api.get_device_galleries(device_id=device_id, params={"page": 1, "count": 100})

    if not galleries:
        click.echo("No galleries on this device")
        return

    headers = ["ID", "Name", "Items", "Owner"]
    rows = []
    for g in galleries:
        rows.append([
            g.get("id"),
            truncate(g.get("name", "Unnamed"), 30),
            g.get("itemCount", 0),
            "You" if g.get("isOwner") else g.get("ownerName", ""),
        ])

    click.echo(format_table(rows, headers))


@device.command("push")
@click.argument("device_id", type=int)
@click.argument("gallery_id", type=int)
def device_push(device_id, gallery_id):
    """Push a gallery to device"""
    api = get_api()
    result = api.post_device_gallery(device_id=device_id, gallery_id=gallery_id)
    click.echo(f"Gallery {gallery_id} pushed to device {device_id}")


@device.command("remove")
@click.argument("device_id", type=int)
@click.argument("gallery_id", type=int)
def device_remove(device_id, gallery_id):
    """Remove a gallery from device"""
    api = get_api()
    api.delete_device_gallery(device_id=device_id, gallery_id=gallery_id)
    click.echo(f"Gallery {gallery_id} removed from device {device_id}")


@device.command("preview")
@click.argument("device_id", type=int)
@click.argument("item_id", type=int)
def device_preview(device_id, item_id):
    """Preview an item on device"""
    api = get_api()
    api.post_device_preview(device_id=device_id, item_id=item_id)
    click.echo(f"Previewing item {item_id} on device {device_id}")


@device.command("sync")
@click.argument("device_id", type=int)
def device_sync(device_id):
    """Sync device"""
    api = get_api()
    api.post_device_sync(device_id=device_id)
    click.echo(f"Device {device_id} synced")


# =============================================================================
# Item Commands
# =============================================================================

@cli.group()
def item():
    """Item (artwork) management commands"""
    pass


@item.command("list")
@click.option("--page", default=1, help="Page number")
@click.option("--count", default=20, help="Items per page")
def item_list(page, count):
    """List your uploaded items"""
    api = get_api()
    items = api.get_user_items(params={"page": page, "count": count})

    if not items:
        click.echo("No items found")
        return

    headers = ["ID", "Name", "Type", "Dimensions"]
    rows = []
    for i in items:
        dims = f"{i.get('originalWidth', '?')}x{i.get('originalHeight', '?')}"
        rows.append([
            i.get("id"),
            truncate(i.get("name", "Unnamed"), 35),
            i.get("type", "image"),
            dims,
        ])

    click.echo(format_table(rows, headers))


@item.command("show")
@click.argument("item_id", type=int)
def item_show(item_id):
    """Show item details"""
    api = get_api()
    i = api.get_item(item_id=item_id)

    click.echo(f"Item: {i.get('name', 'Unnamed')}")
    click.echo(f"  ID: {i.get('id')}")
    click.echo(f"  Type: {i.get('type', 'image')}")
    click.echo(f"  Dimensions: {i.get('originalWidth', '?')}x{i.get('originalHeight', '?')}")
    click.echo(f"  Orientation: {i.get('orientation', 'N/A')}")
    if i.get("description"):
        click.echo(f"  Description: {i.get('description')}")
    if i.get("artistName"):
        click.echo(f"  Artist: {i.get('artistName')}")
    click.echo(f"  Created: {i.get('createdAt', 'N/A')}")


@item.command("upload")
@click.argument("path", type=click.Path(exists=True))
@click.option("--title", "-t", help="Item title (defaults to filename)")
@click.option("--description", "-d", help="Item description")
def item_upload(path, title, description):
    """Upload an image"""
    api = get_api()

    path = Path(path)
    if not title:
        title = path.stem

    click.echo(f"Uploading {path.name}...")
    result = api.upload_image(str(path), title=title, description=description)

    click.echo(f"Uploaded! Item ID: {result.get('id')}")
    click.echo(f"  Name: {result.get('name')}")


@item.command("download")
@click.argument("item_id", type=int)
@click.option("--output", "-o", type=click.Path(), help="Output path (defaults to item name)")
@click.option("--original", is_flag=True, help="Download original (not cropped)")
def item_download(item_id, output, original):
    """Download an item image"""
    api = get_api()
    i = api.get_item(item_id=item_id)

    # Get the appropriate URL
    if original:
        url = i.get("originalImage") or i.get("image")
    else:
        url = i.get("image") or i.get("originalImage")

    if not url:
        click.echo("Error: No image URL found for this item", err=True)
        return

    # Determine output path
    if not output:
        ext = ".jpg"  # Default extension
        if ".png" in url.lower():
            ext = ".png"
        elif ".gif" in url.lower():
            ext = ".gif"
        name = i.get("name", f"item_{item_id}").replace("/", "_")
        output = f"{name}{ext}"

    import requests
    click.echo(f"Downloading to {output}...")
    response = requests.get(url, stream=True, timeout=60)
    response.raise_for_status()

    with open(output, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    click.echo(f"Downloaded: {output}")


@item.command("delete")
@click.argument("item_id", type=int)
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation")
def item_delete(item_id, yes):
    """Delete an item"""
    api = get_api()

    if not yes:
        i = api.get_item(item_id=item_id)
        if not click.confirm(f"Delete item '{i.get('name', item_id)}'?"):
            return

    api.delete_item(item_id=item_id)
    click.echo(f"Item {item_id} deleted")


@item.command("update")
@click.argument("item_id", type=int)
@click.option("--title", "-t", help="New title")
@click.option("--description", "-d", help="New description")
def item_update(item_id, title, description):
    """Update item metadata"""
    api = get_api()

    updates = {}
    if title:
        updates["name"] = title
    if description:
        updates["description"] = description

    if not updates:
        click.echo("No updates specified. Use --title or --description")
        return

    api.put_item(item_id=item_id, json=updates)
    click.echo(f"Item {item_id} updated")


# =============================================================================
# Gallery Commands
# =============================================================================

@cli.group()
def gallery():
    """Gallery (playlist) management commands"""
    pass


@gallery.command("list")
def gallery_list():
    """List your galleries"""
    api = get_api()
    galleries = api.get_user_galleries()

    if not galleries:
        click.echo("No galleries found")
        return

    headers = ["ID", "Name", "Items", "Description"]
    rows = []
    for g in galleries:
        rows.append([
            g.get("id"),
            truncate(g.get("name", "Unnamed"), 25),
            g.get("itemCount", 0),
            truncate(g.get("description", ""), 30),
        ])

    click.echo(format_table(rows, headers))


@gallery.command("show")
@click.argument("gallery_id", type=int)
@click.option("--limit", "-l", default=None, type=int, help="Limit number of items shown (default: all)")
def gallery_show(gallery_id, limit):
    """Show gallery details and items"""
    api = get_api()
    g = api.get_gallery(gallery_id=gallery_id)
    items = api.get_all_gallery_items(gallery_id=gallery_id)

    click.echo(f"Gallery: {g.get('name', 'Unnamed')}")
    click.echo(f"  ID: {g.get('id')}")
    if g.get("description"):
        click.echo(f"  Description: {g.get('description')}")
    click.echo(f"  Items: {len(items)}")
    click.echo(f"  Created: {g.get('createdAt', 'N/A')}")

    if items:
        display_items = items[:limit] if limit else items
        click.echo(f"\nItems ({len(display_items)} of {len(items)} shown):")
        headers = ["ID", "Name", "Type"]
        rows = [[i.get("id"), truncate(i.get("name", ""), 40), i.get("type", "image")] for i in display_items]
        click.echo(format_table(rows, headers))


@gallery.command("create")
@click.argument("name")
@click.option("--description", "-d", default="", help="Gallery description")
def gallery_create(name, description):
    """Create a new gallery"""
    api = get_api()
    g = api.create_gallery(name=name, description=description)
    click.echo(f"Gallery created! ID: {g.get('id')}")


@gallery.command("delete")
@click.argument("gallery_id", type=int)
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation")
def gallery_delete(gallery_id, yes):
    """Delete a gallery"""
    api = get_api()

    if not yes:
        g = api.get_gallery(gallery_id=gallery_id)
        if not click.confirm(f"Delete gallery '{g.get('name', gallery_id)}'?"):
            return

    api.delete_gallery(gallery_id=gallery_id)
    click.echo(f"Gallery {gallery_id} deleted")


@gallery.command("add")
@click.argument("gallery_id", type=int)
@click.argument("item_id", type=int)
def gallery_add(gallery_id, item_id):
    """Add an item to a gallery"""
    api = get_api()
    api.post_gallery_item(gallery_id=gallery_id, item_id=item_id)
    click.echo(f"Item {item_id} added to gallery {gallery_id}")


@gallery.command("remove")
@click.argument("gallery_id", type=int)
@click.argument("item_id", type=int)
def gallery_remove_item(gallery_id, item_id):
    """Remove an item from a gallery"""
    api = get_api()
    api.delete_gallery_item(gallery_id=gallery_id, item_id=item_id)
    click.echo(f"Item {item_id} removed from gallery {gallery_id}")


@gallery.command("rename")
@click.argument("gallery_id", type=int)
@click.argument("name")
def gallery_rename(gallery_id, name):
    """Rename a gallery"""
    api = get_api()
    api.put_gallery(gallery_id=gallery_id, json={"name": name})
    click.echo(f"Gallery {gallery_id} renamed to '{name}'")


# =============================================================================
# Browse Commands
# =============================================================================

@cli.group()
def browse():
    """Browse Meural content catalog"""
    pass


@browse.command("channels")
@click.option("--page", default=1, help="Page number")
@click.option("--count", default=20, help="Items per page")
def browse_channels(page, count):
    """List available channels"""
    api = get_api()
    channels = api.get_channels(params={"page": page, "count": count})

    headers = ["ID", "Name", "Description"]
    rows = []
    for c in channels:
        rows.append([
            c.get("id"),
            truncate(c.get("name", ""), 25),
            truncate(c.get("description", ""), 40),
        ])

    click.echo(format_table(rows, headers))


@browse.command("channel")
@click.argument("channel_id", type=int)
def browse_channel(channel_id):
    """Show channel details"""
    api = get_api()
    c = api.get_channel(channel_id=channel_id)
    items = api.get_channel_items(channel_id=channel_id, params={"count": 10})

    click.echo(f"Channel: {c.get('name')}")
    click.echo(f"  ID: {c.get('id')}")
    if c.get("description"):
        click.echo(f"  Description: {c.get('description')}")

    if items:
        click.echo(f"\nRecent Items ({len(items)} shown):")
        headers = ["ID", "Name", "Artist"]
        rows = [[i.get("id"), truncate(i.get("name", ""), 30), i.get("artistName", "")] for i in items]
        click.echo(format_table(rows, headers))


@browse.command("artists")
@click.option("--page", default=1, help="Page number")
@click.option("--count", default=20, help="Items per page")
def browse_artists(page, count):
    """List artists"""
    api = get_api()
    artists = api.get_artists(params={"page": page, "count": count})

    headers = ["ID", "Name", "Items"]
    rows = []
    for a in artists:
        rows.append([
            a.get("id"),
            truncate(a.get("name", ""), 35),
            a.get("itemCount", ""),
        ])

    click.echo(format_table(rows, headers))


@browse.command("artist")
@click.argument("artist_id", type=int)
def browse_artist(artist_id):
    """Show artist details"""
    api = get_api()
    a = api.get_artist(artist_id=artist_id)
    items = api.get_artist_items(artist_id=artist_id, params={"count": 10})

    click.echo(f"Artist: {a.get('name')}")
    click.echo(f"  ID: {a.get('id')}")
    if a.get("bio"):
        click.echo(f"  Bio: {truncate(a.get('bio'), 100)}")

    if items:
        click.echo(f"\nRecent Works ({len(items)} shown):")
        headers = ["ID", "Name"]
        rows = [[i.get("id"), truncate(i.get("name", ""), 50)] for i in items]
        click.echo(format_table(rows, headers))


@browse.command("categories")
@click.option("--group", "-g", type=int, help="Filter by group ID")
def browse_categories(group):
    """List categories"""
    api = get_api()

    if group:
        categories = api.get_group_categories(group_id=group, params={"count": 50})
    else:
        # Show groups first
        groups = api.get_groups(params={"count": 20})
        click.echo("Groups:")
        headers = ["ID", "Name"]
        rows = [[g.get("id"), g.get("name", "")] for g in groups]
        click.echo(format_table(rows, headers))
        click.echo("\nUse --group <id> to see categories in a group")
        return

    headers = ["ID", "Name", "Items"]
    rows = []
    for c in categories:
        rows.append([
            c.get("id"),
            truncate(c.get("name", ""), 35),
            c.get("itemCount", ""),
        ])

    click.echo(format_table(rows, headers))


@browse.command("search")
@click.argument("query")
@click.option("--type", "-t", "result_type",
              type=click.Choice(["all", "items", "galleries", "artists", "channels"]),
              default="all",
              help="Filter by result type")
def browse_search(query, result_type):
    """Search for content"""
    api = get_api()
    results = api.search(params={"q": query, "page": 1})

    if not results:
        click.echo("No results found")
        return

    # Results are grouped by type
    headers = ["Type", "ID", "Name"]
    rows = []

    type_map = {
        "items": "Item",
        "galleries": "Gallery",
        "artists": "Artist",
        "channels": "Channel",
        "categories": "Category",
    }

    for rtype, label in type_map.items():
        if result_type != "all" and rtype != result_type:
            continue
        items = results.get(rtype, [])
        for r in items[:10]:  # Limit to 10 per type
            rows.append([
                label,
                r.get("id"),
                truncate(r.get("name", ""), 40),
            ])

    if not rows:
        click.echo("No results found")
        return

    click.echo(format_table(rows, headers))


# =============================================================================
# Favorites Commands
# =============================================================================

@cli.group()
def favorites():
    """Manage favorites"""
    pass


@favorites.command("list")
@click.option("--type", "-t", "fav_type",
              type=click.Choice(["galleries", "items", "artists", "channels", "categories"]),
              default="galleries",
              help="Type of favorites to list")
def favorites_list(fav_type):
    """List your favorites"""
    api = get_api()

    method_map = {
        "galleries": api.get_favorite_galleries,
        "items": api.get_favorite_items,
        "artists": api.get_favorite_artists,
        "channels": api.get_favorite_channels,
        "categories": api.get_favorite_categories,
    }

    results = method_map[fav_type](params={"page": 1})

    if not results:
        click.echo(f"No favorite {fav_type}")
        return

    headers = ["ID", "Name"]
    rows = [[r.get("id"), truncate(r.get("name", ""), 50)] for r in results]
    click.echo(format_table(rows, headers))


@favorites.command("add")
@click.argument("model", type=click.Choice(["Gallery", "Item", "Artist", "Channel", "Category"]))
@click.argument("item_id", type=int)
def favorites_add(model, item_id):
    """Add to favorites"""
    api = get_api()
    api.post_favorite(json={"model": model, "id": item_id})
    click.echo(f"{model} {item_id} added to favorites")


@favorites.command("remove")
@click.argument("model", type=click.Choice(["Gallery", "Item", "Artist", "Channel", "Category"]))
@click.argument("item_id", type=int)
def favorites_remove(model, item_id):
    """Remove from favorites"""
    api = get_api()
    api.delete_favorite(json={"model": model, "id": item_id})
    click.echo(f"{model} {item_id} removed from favorites")


# =============================================================================
# Main entry point
# =============================================================================

def main():
    """Main entry point"""
    cli()


if __name__ == "__main__":
    main()
