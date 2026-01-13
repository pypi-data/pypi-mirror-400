# Meural API Client

Python client for the Meural Canvas API (v1). Implements 58+ endpoints with full integration test coverage.

## Quick Start

```python
from meural_api import MeuralAPI

# From environment variables (MEURAL_USERNAME, MEURAL_PASSWORD)
api = MeuralAPI.from_env()

# Or from ~/.meural file
api = MeuralAPI.from_env()

# Get user's devices
devices = api.get_devices()

# Upload an image
item = api.upload_image("/path/to/image.jpg", title="My Art")

# Create a playlist and add the image
gallery = api.create_gallery(name="My Playlist")
api.post_gallery_item(gallery_id=gallery["id"], item_id=item["id"])

# Send playlist to device
api.post_device_gallery(device_id=devices[0]["id"], gallery_id=gallery["id"])
```

## Usage Guidelines

When searching for images to display on a Meural device:
1. Check the device's current orientation first (`device show {id}` returns orientation)
2. When selecting images, prefer ones that match the device orientation (landscape for horizontal, portrait for vertical)
3. Use `item show {id}` to check an image's dimensions and orientation before previewing
4. If multiple search results are found, filter for images matching the device orientation

## Entity Relationships

```
Groups (8 total) - Top-level organizational containers
├── 19: At Home
├── 7: Museums
├── 10: Color
├── 18: Editorial
├── 2: Movements and Styles (43 categories)
├── 4: Types
├── 5: Subject and Content
└── 11: Sampler
    └── Categories (296 total) - Classification tags
          └── Items have categoryIds[] referencing these

Channels - Curated content sources/partners (SuperRare, Magnum Photos, etc.)
├── Items - Artworks in the channel
├── Galleries - Curated playlists
├── Artists - Artists featured in channel
└── Articles - Editorial content about the channel

Artists - Individual artists
├── Items - Their artworks
├── Galleries - Collections of their work
├── Articles - Editorial about the artist
└── Related - Similar artists

Articles - Editorial blog posts
├── type: "gallery" | other
├── object: Reference to a gallery/item
└── body: Rich text content

User Content
├── Items - Uploaded images/videos
├── Galleries - User-created playlists
├── Albums - Linked photo albums (Google Photos, etc.)
├── Devices - Registered Meural Canvases
└── Favorites - Saved galleries/items/artists/channels/categories
```

## API Endpoints

### User Endpoints
| Method | Endpoint | Function | Description |
|--------|----------|----------|-------------|
| GET | `/user` | `get_user()` | Get current user info |
| PUT | `/user` | `put_user()` | Update user profile |
| GET | `/user/devices` | `get_user_devices()` | Get user's devices |
| GET | `/user/items` | `get_user_items()` | Get user's uploaded items |
| GET | `/user/galleries` | `get_user_galleries()` | Get user's playlists |
| GET | `/user/albums` | `get_user_albums()` | Get linked photo albums |
| POST | `/user/feedback` | `post_user_feedback()` | Submit feedback |

### Device Endpoints
| Method | Endpoint | Function | Description |
|--------|----------|----------|-------------|
| POST | `/devices` | `post_device()` | Register device (requires productKey) |
| GET | `/devices/{id}` | `get_device()` | Get device info |
| PUT | `/devices/{id}` | `put_device()` | Update device settings |
| PATCH | `/devices/{id}` | `patch_device()` | Partial update device |
| DELETE | `/devices/{id}` | `delete_device()` | Remove device |
| GET | `/devices/{id}/scheduler` | `get_device_scheduler()` | Get sleep/wake schedule |
| PUT | `/devices/{id}/scheduler` | `put_device_scheduler()` | Update schedule |
| GET | `/devices/{id}/galleries` | `get_device_galleries()` | Get device playlists |
| POST | `/devices/{id}/galleries/{gid}` | `post_device_gallery()` | Add playlist to device |
| DELETE | `/devices/{id}/galleries/{gid}` | `delete_device_gallery()` | Remove playlist from device |
| GET | `/devices/{id}/albums` | `get_device_albums()` | Get linked albums |
| POST | `/devices/{id}/items/{iid}` | `post_device_item()` | Send item to device |
| POST | `/devices/{id}/preview/{iid}` | `post_device_preview()` | Preview item on device |
| POST | `/devices/{id}/sync` | `post_device_sync()` | Sync device |
| GET | `/devices/display_languages` | `get_display_languages()` | Get available languages |

### Item Endpoints
| Method | Endpoint | Function | Description |
|--------|----------|----------|-------------|
| POST | `/items` | `upload_image()` | Upload image (multipart) |
| GET | `/items/{id}` | `get_item()` | Get item details |
| PUT | `/items/{id}` | `put_item()` | Update item metadata |
| PUT | `/items/{id}/crop` | `put_item_crop()` | Crop image (x1,y1,x2,y2 format) |
| DELETE | `/items/{id}` | `delete_item()` | Delete item |

### Gallery Endpoints
| Method | Endpoint | Function | Description |
|--------|----------|----------|-------------|
| POST | `/galleries` | `create_gallery()` | Create playlist |
| GET | `/galleries/{id}` | `get_gallery()` | Get playlist |
| PUT | `/galleries/{id}` | `put_gallery()` | Update playlist |
| DELETE | `/galleries/{id}` | `delete_gallery()` | Delete playlist |
| GET | `/galleries/{id}/items` | `get_gallery_items()` | Get playlist items |
| POST | `/galleries/{id}/items/{iid}` | `post_gallery_item()` | Add item to playlist |
| DELETE | `/galleries/{id}/items/{iid}` | `delete_gallery_item()` | Remove item from playlist |
| PUT | `/galleries/{id}/sort` | `put_gallery_sort()` | Reorder items |
| GET | `/galleries/{id}/shares` | `get_gallery_shares()` | Get share info |
| GET | `/galleries/{id}/related` | `get_gallery_related()` | Get related playlists |
| POST | `/galleries/nft` | `post_galleries_nft()` | Get/create NFT gallery |

### Favorites Endpoints
| Method | Endpoint | Function | Description |
|--------|----------|----------|-------------|
| POST | `/favorites` | `post_favorite()` | Add to favorites `{model, id}` |
| DELETE | `/favorites` | `delete_favorite()` | Remove from favorites |
| GET | `/favorites/items` | `get_favorite_items()` | Get favorite works |
| GET | `/favorites/galleries` | `get_favorite_galleries()` | Get favorite playlists |
| GET | `/favorites/artists` | `get_favorite_artists()` | Get favorite artists |
| GET | `/favorites/channels` | `get_favorite_channels()` | Get favorite channels |
| GET | `/favorites/categories` | `get_favorite_categories()` | Get favorite categories |
| GET | `/favorites/articles` | `get_favorite_articles()` | Get favorite editorial |

### Discovery Endpoints
| Method | Endpoint | Function | Description |
|--------|----------|----------|-------------|
| GET | `/channels` | `get_channels()` | List channels |
| GET | `/channels/{id}` | `get_channel()` | Get channel details |
| GET | `/channels/{id}/items` | `get_channel_items()` | Get channel artworks |
| GET | `/channels/{id}/galleries` | `get_channel_galleries()` | Get channel playlists |
| GET | `/channels/{id}/artists` | `get_channel_artists()` | Get channel artists |
| GET | `/channels/{id}/articles` | `get_channel_articles()` | Get channel editorial |
| GET | `/artists` | `get_artists()` | List artists |
| GET | `/artists/{id}` | `get_artist()` | Get artist details |
| GET | `/artists/{id}/items` | `get_artist_items()` | Get artist artworks |
| GET | `/artists/{id}/galleries` | `get_artist_galleries()` | Get artist playlists |
| GET | `/artists/{id}/articles` | `get_artist_articles()` | Get artist editorial |
| GET | `/artists/{id}/related` | `get_artist_related()` | Get similar artists |
| GET | `/groups` | `get_groups()` | List groups (8 total) |
| GET | `/groups/{id}` | `get_group()` | Get group details |
| GET | `/groups/{id}/categories` | `get_group_categories()` | Get group's categories |
| GET | `/categories` | `get_categories()` | List all categories (296) |
| GET | `/categories/{id}` | `get_category()` | Get category details |
| GET | `/categories/{id}/items` | `get_category_items()` | Get category artworks |
| GET | `/categories/{id}/galleries` | `get_category_galleries()` | Get category playlists |
| GET | `/categories/{id}/articles` | `get_category_articles()` | Get category editorial |
| GET | `/articles/{id}` | `get_article()` | Get article/editorial |
| GET | `/feed` | `get_feed()` | Get feed content |
| GET | `/search` | `search()` | Search content |

## API Conventions

### Authentication
- AWS Cognito with SRP flow → exchange for Meural API token
- Token passed as `Authorization: Token {token}` header
- Headers: `X-Meural-Api-Version: 4`, `X-Meural-Source-Platform: web`

### Pagination
- `page=N` with optional `count=N`
- Response: `{"data": [...], "isLast": bool, "count": N}`

### Sorting
- `sort=date_updated__dsc` - newest first
- `sort=date_added__dsc` - recently added
- `sort=name__asc` - alphabetical
- `sort=order__asc` - curated order

### Timeouts
- GET requests: 5s default
- POST/PUT/DELETE: 60s default (write operations are slower)
- `/categories`, `/favorites/*`: 60s (slow endpoints)

### Crop Format
PUT `/items/{id}/crop` expects `{x1, y1, x2, y2}` coordinates (NOT width/height):
```python
api.put_item_crop(item_id=123, json={"x1": 50, "y1": 50, "x2": 500, "y2": 350})
```

## CLI Usage

The `meural_cli.py` provides a hierarchical command-line interface:

```bash
python meural_cli.py --help
```

### Device Commands
```bash
python meural_cli.py device list                    # List all devices
python meural_cli.py device show 72386              # Show device details
python meural_cli.py device galleries 72386         # List galleries on device
python meural_cli.py device push 72386 599833       # Push gallery to device
python meural_cli.py device remove 72386 599833     # Remove gallery from device
python meural_cli.py device preview 72386 25253268  # Preview item on device
python meural_cli.py device sync 72386              # Sync device
```

### Item Commands
```bash
python meural_cli.py item list                      # List your uploaded items
python meural_cli.py item show 25253268             # Show item details
python meural_cli.py item upload ~/art.jpg -t "My Art"  # Upload image
python meural_cli.py item download 25253268         # Download image
python meural_cli.py item delete 25253268           # Delete item
python meural_cli.py item update 25253268 -t "New Title"  # Update metadata
```

### Gallery Commands
```bash
python meural_cli.py gallery list                   # List your galleries
python meural_cli.py gallery show 599833            # Show gallery with items
python meural_cli.py gallery create "New Playlist"  # Create gallery
python meural_cli.py gallery delete 599833          # Delete gallery
python meural_cli.py gallery add 599833 25253268    # Add item to gallery
python meural_cli.py gallery remove 599833 25253268 # Remove item from gallery
python meural_cli.py gallery rename 599833 "New Name"  # Rename gallery
```

### Browse Commands
```bash
python meural_cli.py browse channels                # List channels
python meural_cli.py browse channel 60              # Show channel details
python meural_cli.py browse artists                 # List artists
python meural_cli.py browse artist 79               # Show artist details
python meural_cli.py browse categories --group 2    # List categories in group
python meural_cli.py browse search "monet"          # Search content
python meural_cli.py browse search "monet" -t items # Search only items
```

### Favorites Commands
```bash
python meural_cli.py favorites list                 # List favorite galleries
python meural_cli.py favorites list -t artists      # List favorite artists
python meural_cli.py favorites add Gallery 599833   # Add to favorites
python meural_cli.py favorites remove Gallery 599833  # Remove from favorites
```

### Auth Commands
```bash
python meural_cli.py auth status                    # Show auth status and user info
```

## Running Tests

```bash
# Set credentials
export MEURAL_USERNAME=your@email.com
export MEURAL_PASSWORD=yourpassword

# Or create ~/.meural file:
# MEURAL_USERNAME=your@email.com
# MEURAL_PASSWORD=yourpassword

# Run all tests
pytest test_meural_api.py -v

# Run specific test
pytest test_meural_api.py::TestItemEndpoints::test_upload_and_delete_item -v
```

## Files

- `meural_api.py` - Main API client
- `auth_cognito.py` - AWS Cognito authentication
- `meural_cli.py` - Command-line interface
- `test_meural_api.py` - Integration tests (59 tests)
- `cognito_tokens.json` - Token cache (auto-generated)
