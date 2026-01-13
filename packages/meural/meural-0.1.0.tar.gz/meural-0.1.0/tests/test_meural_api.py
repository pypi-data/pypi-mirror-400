"""
Integration tests for Meural API

These tests run against the real Meural API and require valid credentials.
Set MEURAL_USERNAME and MEURAL_PASSWORD environment variables.

Run with: pytest test_meural_api.py -v
"""
import pytest
import os
import time
import tempfile
import requests
from meural import MeuralAPI


@pytest.fixture(scope="module")
def api():
    """Create API client for all tests in this module"""
    return MeuralAPI.from_env()


@pytest.fixture(scope="module")
def device_id(api):
    """Get the first available device ID for testing"""
    devices = api.get_devices()
    if not devices:
        pytest.skip("No devices available for testing")
    return devices[0]["id"]


@pytest.fixture(scope="module")
def user_item_id(api):
    """Get an existing user item ID for testing"""
    items = api.get_user_items_list(page=1)
    if not items:
        pytest.skip("No user items available for testing")
    return items[0]["id"]


@pytest.fixture(scope="module")
def static_image_item_id(api):
    """Get a static image (not video/gif) item ID for testing"""
    items = api.get_user_items_list(page=1)
    for item in items:
        detail = api.get_item(item_id=item["id"])
        # Check if it's a static image (not video, not gif)
        if detail.get("type") == "image":
            img_url = detail.get("image", "") or ""
            if ".gif" not in img_url.lower():
                return item["id"]
    pytest.skip("No static image items available for testing")


@pytest.fixture(scope="module")
def channel_id(api):
    """Get a channel ID for testing"""
    channels = api.get_channels_list(page=1, count=1)
    if not channels:
        pytest.skip("No channels available")
    return channels[0]["id"]


@pytest.fixture(scope="module")
def artist_id(api):
    """Get an artist ID for testing"""
    artists = api.get_artists_list(page=1, count=1)
    if not artists:
        pytest.skip("No artists available")
    return artists[0]["id"]


@pytest.fixture(scope="module")
def category_id():
    """Use a known category ID"""
    return 990  # Travel and Adventure


def create_test_image():
    """Create a simple test image file using PIL"""
    try:
        from PIL import Image
        # Create a small test image
        img = Image.new('RGB', (100, 100), color='red')
        fd, path = tempfile.mkstemp(suffix='.jpg', prefix='TEST_meural_')
        os.close(fd)
        img.save(path, 'JPEG')
        return path
    except ImportError:
        # Fallback: create minimal JPEG without PIL
        # This is a valid 1x1 red JPEG
        jpeg_data = bytes([
            0xFF, 0xD8, 0xFF, 0xE0, 0x00, 0x10, 0x4A, 0x46, 0x49, 0x46, 0x00, 0x01,
            0x01, 0x00, 0x00, 0x01, 0x00, 0x01, 0x00, 0x00, 0xFF, 0xDB, 0x00, 0x43,
            0x00, 0x08, 0x06, 0x06, 0x07, 0x06, 0x05, 0x08, 0x07, 0x07, 0x07, 0x09,
            0x09, 0x08, 0x0A, 0x0C, 0x14, 0x0D, 0x0C, 0x0B, 0x0B, 0x0C, 0x19, 0x12,
            0x13, 0x0F, 0x14, 0x1D, 0x1A, 0x1F, 0x1E, 0x1D, 0x1A, 0x1C, 0x1C, 0x20,
            0x24, 0x2E, 0x27, 0x20, 0x22, 0x2C, 0x23, 0x1C, 0x1C, 0x28, 0x37, 0x29,
            0x2C, 0x30, 0x31, 0x34, 0x34, 0x34, 0x1F, 0x27, 0x39, 0x3D, 0x38, 0x32,
            0x3C, 0x2E, 0x33, 0x34, 0x32, 0xFF, 0xC0, 0x00, 0x0B, 0x08, 0x00, 0x01,
            0x00, 0x01, 0x01, 0x01, 0x11, 0x00, 0xFF, 0xC4, 0x00, 0x1F, 0x00, 0x00,
            0x01, 0x05, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08,
            0x09, 0x0A, 0x0B, 0xFF, 0xC4, 0x00, 0xB5, 0x10, 0x00, 0x02, 0x01, 0x03,
            0x03, 0x02, 0x04, 0x03, 0x05, 0x05, 0x04, 0x04, 0x00, 0x00, 0x01, 0x7D,
            0x01, 0x02, 0x03, 0x00, 0x04, 0x11, 0x05, 0x12, 0x21, 0x31, 0x41, 0x06,
            0x13, 0x51, 0x61, 0x07, 0x22, 0x71, 0x14, 0x32, 0x81, 0x91, 0xA1, 0x08,
            0x23, 0x42, 0xB1, 0xC1, 0x15, 0x52, 0xD1, 0xF0, 0x24, 0x33, 0x62, 0x72,
            0x82, 0x09, 0x0A, 0x16, 0x17, 0x18, 0x19, 0x1A, 0x25, 0x26, 0x27, 0x28,
            0x29, 0x2A, 0x34, 0x35, 0x36, 0x37, 0x38, 0x39, 0x3A, 0x43, 0x44, 0x45,
            0x46, 0x47, 0x48, 0x49, 0x4A, 0x53, 0x54, 0x55, 0x56, 0x57, 0x58, 0x59,
            0x5A, 0x63, 0x64, 0x65, 0x66, 0x67, 0x68, 0x69, 0x6A, 0x73, 0x74, 0x75,
            0x76, 0x77, 0x78, 0x79, 0x7A, 0x83, 0x84, 0x85, 0x86, 0x87, 0x88, 0x89,
            0x8A, 0x92, 0x93, 0x94, 0x95, 0x96, 0x97, 0x98, 0x99, 0x9A, 0xA2, 0xA3,
            0xA4, 0xA5, 0xA6, 0xA7, 0xA8, 0xA9, 0xAA, 0xB2, 0xB3, 0xB4, 0xB5, 0xB6,
            0xB7, 0xB8, 0xB9, 0xBA, 0xC2, 0xC3, 0xC4, 0xC5, 0xC6, 0xC7, 0xC8, 0xC9,
            0xCA, 0xD2, 0xD3, 0xD4, 0xD5, 0xD6, 0xD7, 0xD8, 0xD9, 0xDA, 0xE1, 0xE2,
            0xE3, 0xE4, 0xE5, 0xE6, 0xE7, 0xE8, 0xE9, 0xEA, 0xF1, 0xF2, 0xF3, 0xF4,
            0xF5, 0xF6, 0xF7, 0xF8, 0xF9, 0xFA, 0xFF, 0xDA, 0x00, 0x08, 0x01, 0x01,
            0x00, 0x00, 0x3F, 0x00, 0xFB, 0xD5, 0xDB, 0x20, 0xA8, 0xF1, 0x85, 0xF5,
            0x47, 0xFF, 0xD9
        ])
        fd, path = tempfile.mkstemp(suffix='.jpg', prefix='TEST_meural_')
        with os.fdopen(fd, 'wb') as f:
            f.write(jpeg_data)
        return path


class TestUserEndpoints:
    """Test user-related endpoints"""

    def test_get_user(self, api):
        """Test getting current user info"""
        user = api.get_user()
        assert user is not None
        assert "id" in user
        assert "email" in user

    def test_get_user_devices(self, api):
        """Test getting user's devices"""
        devices = api.get_devices()
        assert isinstance(devices, list)
        # User should have at least one device
        if devices:
            device = devices[0]
            assert "id" in device
            # Device uses 'alias' for name in the API
            assert "alias" in device or "name" in device

    def test_get_user_items(self, api):
        """Test getting user's uploaded items"""
        items = api.get_user_items_list(page=1)
        assert isinstance(items, list)

    def test_get_user_galleries(self, api):
        """Test getting user's galleries"""
        galleries = api.get_user_galleries()
        assert isinstance(galleries, list)

    def test_get_user_albums(self, api):
        """Test getting user's linked albums"""
        albums = api.get_user_albums(params={"page": 1})
        assert isinstance(albums, list)


class TestDeviceEndpoints:
    """Test device-related endpoints"""

    def test_get_device(self, api, device_id):
        """Test getting device details"""
        device = api.get_device(device_id=device_id)
        assert device is not None
        assert device.get("id") == device_id

    def test_get_device_scheduler(self, api, device_id):
        """Test getting device scheduler"""
        scheduler = api.get_device_scheduler(device_id=device_id)
        assert scheduler is not None

    def test_get_device_galleries(self, api, device_id):
        """Test getting device galleries/playlists"""
        galleries = api.get_device_galleries(
            device_id=device_id, params={"page": 1, "count": 10}
        )
        assert isinstance(galleries, list)

    def test_get_device_albums(self, api, device_id):
        """Test getting device linked albums"""
        albums = api.get_device_albums(
            device_id=device_id, params={"page": 1, "count": 10}
        )
        assert isinstance(albums, list)

    def test_get_display_languages(self, api):
        """Test getting available display languages"""
        languages = api.get_display_languages()
        assert isinstance(languages, list)

    def test_add_and_remove_device_gallery(self, api, device_id):
        """Test adding and removing a gallery from a device (compound test)"""
        import requests

        # First create a gallery to add
        gallery = api.create_gallery(
            name="TEST_device_gallery",
            description="Test gallery for device add/remove",
        )
        assert gallery is not None
        gallery_id = gallery["id"]

        # Get an existing item from user's uploads to add to the gallery
        # (can't add empty playlist to device)
        items = api.get_user_items_list(page=1)
        if not items:
            api.delete_gallery(gallery_id=gallery_id)
            pytest.skip("No user items available for testing")

        item_id = items[0]["id"]

        try:
            # Add item to gallery first (device requires non-empty gallery)
            api.post_gallery_item(gallery_id=gallery_id, item_id=item_id)

            # Add gallery to device
            result = api.post_device_gallery(device_id=device_id, gallery_id=gallery_id)
            assert result is not None

            # Verify the gallery was added
            galleries = api.get_device_galleries(
                device_id=device_id, params={"page": 1, "count": 100}
            )
            gallery_ids = [g.get("id") for g in galleries]
            assert gallery_id in gallery_ids

            # Remove gallery from device
            api.delete_device_gallery(device_id=device_id, gallery_id=gallery_id)

            # Verify the gallery was removed
            galleries = api.get_device_galleries(
                device_id=device_id, params={"page": 1, "count": 100}
            )
            gallery_ids = [g.get("id") for g in galleries]
            assert gallery_id not in gallery_ids
        finally:
            # Cleanup: delete the gallery
            try:
                api.delete_gallery(gallery_id=gallery_id)
            except Exception:
                pass  # Best effort cleanup


class TestGalleryEndpoints:
    """Test gallery-related endpoints"""

    def test_create_and_delete_gallery(self, api):
        """Test creating and deleting a gallery (compound test)"""
        # Create gallery
        gallery = api.create_gallery(
            name="TEST_integration_gallery",
            description="Test gallery created by integration tests",
        )
        assert gallery is not None
        assert gallery.get("id")
        assert gallery.get("name") == "TEST_integration_gallery"

        gallery_id = gallery["id"]

        try:
            # Verify we can get the gallery
            fetched = api.get_gallery(gallery_id=gallery_id)
            assert fetched.get("id") == gallery_id

            # Get gallery items (should be empty)
            items = api.get_gallery_items(gallery_id=gallery_id)
            assert isinstance(items, list)
        finally:
            # Cleanup: delete the gallery
            api.delete_gallery(gallery_id=gallery_id)

    def test_get_user_galleries(self, api):
        """Test listing user galleries"""
        galleries = api.list_galleries()
        assert isinstance(galleries, list)

    def test_update_gallery(self, api):
        """Test updating a gallery (compound test)"""
        # Create gallery
        gallery = api.create_gallery(
            name="TEST_update_gallery",
            description="Original description",
        )
        assert gallery is not None
        gallery_id = gallery["id"]

        try:
            # Update the gallery
            updated = api.put_gallery(
                gallery_id=gallery_id,
                json={"name": "TEST_update_gallery_renamed", "description": "Updated description"},
            )
            assert updated is not None
            assert updated.get("name") == "TEST_update_gallery_renamed"
            assert updated.get("description") == "Updated description"

            # Verify by fetching
            fetched = api.get_gallery(gallery_id=gallery_id)
            assert fetched.get("name") == "TEST_update_gallery_renamed"
        finally:
            # Cleanup: delete the gallery
            api.delete_gallery(gallery_id=gallery_id)


class TestFavoritesEndpoints:
    """Test favorites-related endpoints"""

    def test_get_favorite_galleries(self, api):
        """Test getting favorite galleries"""
        favorites = api.get_favorite_galleries_list(page=1)
        assert isinstance(favorites, list)

    def test_get_favorite_items(self, api):
        """Test getting favorite items"""
        favorites = api.get_favorite_items(params={"page": 1})
        assert isinstance(favorites, list)

    def test_get_favorite_artists(self, api):
        """Test getting favorite artists"""
        favorites = api.get_favorite_artists(params={"page": 1})
        assert isinstance(favorites, list)

    def test_get_favorite_channels(self, api):
        """Test getting favorite channels"""
        favorites = api.get_favorite_channels(params={"page": 1})
        assert isinstance(favorites, list)

    def test_get_favorite_categories(self, api):
        """Test getting favorite categories"""
        favorites = api.get_favorite_categories(params={"page": 1})
        assert isinstance(favorites, list)

    def test_get_favorite_articles(self, api):
        """Test getting favorite articles/editorial"""
        favorites = api.get_favorite_articles(params={"page": 1})
        assert isinstance(favorites, list)


class TestDiscoveryEndpoints:
    """Test discovery/browse-related endpoints"""

    def test_get_channels(self, api):
        """Test getting channels list"""
        channels = api.get_channels_list(page=1, count=6)
        assert isinstance(channels, list)
        if channels:
            channel = channels[0]
            assert "id" in channel
            assert "name" in channel

    def test_get_channel_details(self, api):
        """Test getting individual channel details"""
        # First get channels list
        channels = api.get_channels_list(page=1, count=1)
        if not channels:
            pytest.skip("No channels available")

        channel_id = channels[0]["id"]
        channel = api.get_channel(channel_id=channel_id)
        assert channel is not None
        assert channel.get("id") == channel_id

    def test_get_channel_items(self, api):
        """Test getting channel items"""
        channels = api.get_channels_list(page=1, count=1)
        if not channels:
            pytest.skip("No channels available")

        channel_id = channels[0]["id"]
        items = api.get_channel_items(
            channel_id=channel_id, params={"page": 1, "sort": "date_updated__dsc"}
        )
        assert isinstance(items, list)

    def test_get_artists(self, api):
        """Test getting artists list"""
        artists = api.get_artists_list(page=1, count=6)
        assert isinstance(artists, list)
        if artists:
            artist = artists[0]
            assert "id" in artist
            assert "name" in artist

    def test_get_artist_details(self, api):
        """Test getting individual artist details"""
        artists = api.get_artists_list(page=1, count=1)
        if not artists:
            pytest.skip("No artists available")

        artist_id = artists[0]["id"]
        artist = api.get_artist(artist_id=artist_id)
        assert artist is not None
        assert artist.get("id") == artist_id

    def test_get_artist_items(self, api):
        """Test getting artist items"""
        artists = api.get_artists_list(page=1, count=1)
        if not artists:
            pytest.skip("No artists available")

        artist_id = artists[0]["id"]
        items = api.get_artist_items(
            artist_id=artist_id, params={"page": 1, "sort": "date_updated__dsc"}
        )
        assert isinstance(items, list)

    def test_get_artist_related(self, api):
        """Test getting related artists"""
        artists = api.get_artists_list(page=1, count=1)
        if not artists:
            pytest.skip("No artists available")

        artist_id = artists[0]["id"]
        related = api.get_artist_related(artist_id=artist_id)
        assert isinstance(related, list)

    def test_get_groups(self, api):
        """Test getting groups/collections"""
        groups = api.get_groups_list(page=1, count=10)
        assert isinstance(groups, list)
        if groups:
            group = groups[0]
            assert "id" in group
            assert "name" in group

    def test_get_group_details(self, api):
        """Test getting individual group details"""
        groups = api.get_groups_list(page=1, count=1)
        if not groups:
            pytest.skip("No groups available")

        group_id = groups[0]["id"]
        group = api.get_group(group_id=group_id)
        assert group is not None
        assert group.get("id") == group_id

    def test_get_group_categories(self, api):
        """Test getting categories within a group"""
        # Use group 2 (Movements and Styles) which has 43 categories
        categories = api.get_group_categories(group_id=2, params={"page": 1, "count": 10})
        assert isinstance(categories, list)
        assert len(categories) > 0
        if categories:
            cat = categories[0]
            assert "id" in cat
            assert "name" in cat

    def test_get_categories(self, api):
        """Test getting all categories"""
        categories = api.get_categories(params={"page": 1, "count": 10})
        assert isinstance(categories, list)
        assert len(categories) > 0
        if categories:
            cat = categories[0]
            assert "id" in cat
            assert "name" in cat

    def test_get_category_details(self, api):
        """Test getting individual category details"""
        # Use known category ID to avoid slow /categories call
        category = api.get_category(category_id=21)  # Portrait
        assert category is not None
        assert category.get("id") == 21
        assert category.get("name") == "Portrait"

    def test_get_category_items(self, api):
        """Test getting items in a category"""
        # Use category 990 (Travel and Adventure) which has 349 items
        items = api.get_category_items(category_id=990, params={"page": 1, "count": 5})
        assert isinstance(items, list)
        assert len(items) > 0

    def test_get_feed(self, api):
        """Test getting feed content"""
        feed = api.get_feed_content(page=1)
        assert feed is not None
        assert "data" in feed

    def test_search(self, api):
        """Test search functionality"""
        results = api.search_content(query="landscape", page=1)
        assert results is not None
        assert "data" in results


class TestArticleEndpoints:
    """Test article/editorial endpoints"""

    def test_get_article(self, api):
        """Test getting an article by ID"""
        # Article ID 31 is a known article from the API
        article = api.get_article(article_id="31")
        assert article is not None
        assert article.get("id")


class TestItemEndpoints:
    """Test item-related endpoints"""

    def test_get_item(self, api, user_item_id):
        """Test getting item details"""
        item = api.get_item(item_id=user_item_id)
        assert item is not None
        assert item.get("id") == user_item_id

    def test_upload_and_delete_item(self, api):
        """Test uploading and deleting an item (compound test)"""
        # Create a test image
        image_path = create_test_image()

        try:
            # Upload the image
            result = api.upload_image(
                image_path=image_path,
                title="TEST_upload_item",
                description="Test item for upload/delete test",
            )
            assert result is not None
            assert result.get("id")

            item_id = result["id"]

            # Verify we can get the item
            item = api.get_item(item_id=item_id)
            assert item is not None
            assert item.get("id") == item_id

            # Delete the item
            api.delete_item(item_id=item_id)

        finally:
            # Cleanup: remove temp file
            if os.path.exists(image_path):
                os.remove(image_path)

    def test_put_item(self, api, user_item_id):
        """Test updating item metadata"""
        # Get original item data first
        original = api.get_item(item_id=user_item_id)
        original_name = original.get("name", "")

        try:
            # Update the item
            updated = api.put_item(
                item_id=user_item_id,
                json={"name": "TEST_updated_name"},
            )
            assert updated is not None

            # Verify update
            fetched = api.get_item(item_id=user_item_id)
            assert fetched.get("name") == "TEST_updated_name"

        finally:
            # Restore original name
            api.put_item(item_id=user_item_id, json={"name": original_name})


class TestItemCrop:
    """Test item crop endpoint"""

    def test_put_item_crop(self, api, static_image_item_id):
        """Test cropping a static image item"""
        # Get item details first
        item = api.get_item(item_id=static_image_item_id)

        # Store original crop values to restore later (API uses x1,y1,x2,y2 format)
        orig_x1 = item.get("croppedX1", 0)
        orig_y1 = item.get("croppedY1", 0)
        orig_width = item.get("croppedWidth", 0)
        orig_height = item.get("croppedHeight", 0)
        original_crop = {
            "x1": orig_x1,
            "y1": orig_y1,
            "x2": orig_x1 + orig_width if orig_width else item.get("originalWidth", 1920),
            "y2": orig_y1 + orig_height if orig_height else item.get("originalHeight", 1080),
        }

        # Use small, reasonable crop values (API rejects large values silently)
        # The Canvas has a maximum display resolution, so crop dimensions are limited
        test_x1 = 50
        test_y1 = 50
        test_x2 = 500  # 450px wide
        test_y2 = 350  # 300px tall
        test_crop = {
            "x1": test_x1,
            "y1": test_y1,
            "x2": test_x2,
            "y2": test_y2,
        }

        try:
            # Apply the crop
            result = api.put_item_crop(item_id=static_image_item_id, json=test_crop)
            assert result is not None or result == {}

            # API returns updated item data directly - verify from response
            if isinstance(result, dict) and result.get("croppedX1") is not None:
                assert result.get("croppedX1") == test_x1
                assert result.get("croppedY1") == test_y1
                assert result.get("croppedWidth") == test_x2 - test_x1
                assert result.get("croppedHeight") == test_y2 - test_y1
            else:
                # Give server a moment to process, then verify
                time.sleep(2)
                updated_item = api.get_item(item_id=static_image_item_id)
                assert updated_item.get("croppedX1") == test_x1
                assert updated_item.get("croppedY1") == test_y1
        finally:
            # Restore original crop
            api.put_item_crop(item_id=static_image_item_id, json=original_crop)


class TestGalleryItemOperations:
    """Test gallery item add/remove operations"""

    def test_add_and_remove_gallery_item(self, api, user_item_id):
        """Test adding and removing an item from a gallery"""
        # Create a test gallery
        gallery = api.create_gallery(
            name="TEST_gallery_item_ops",
            description="Test gallery for item operations",
        )
        assert gallery is not None
        gallery_id = gallery["id"]

        try:
            # Add item to gallery
            api.post_gallery_item(gallery_id=gallery_id, item_id=user_item_id)

            # Verify item was added
            items = api.get_gallery_items(gallery_id=gallery_id)
            item_ids = [i.get("id") for i in items]
            assert user_item_id in item_ids

            # Remove item from gallery
            api.delete_gallery_item(gallery_id=gallery_id, item_id=user_item_id)

            # Verify item was removed
            items = api.get_gallery_items(gallery_id=gallery_id)
            item_ids = [i.get("id") for i in items]
            assert user_item_id not in item_ids
        finally:
            # Cleanup
            try:
                api.delete_gallery(gallery_id=gallery_id)
            except Exception:
                pass

    def test_get_gallery_shares(self, api):
        """Test getting gallery shares"""
        # Use user's first gallery
        galleries = api.get_user_galleries()
        if not galleries:
            pytest.skip("No galleries available")

        gallery_id = galleries[0]["id"]
        # This may return empty list, but shouldn't error
        shares = api.get_gallery_shares(gallery_id=gallery_id)
        assert isinstance(shares, list)

    def test_get_gallery_related(self, api):
        """Test getting related galleries"""
        # Find a channel with galleries
        channels = api.get_channels_list(page=1, count=10)
        gallery_id = None
        for ch in channels:
            galleries = api.get_channel_galleries(channel_id=ch["id"], params={"count": 1})
            if galleries:
                gallery_id = galleries[0]["id"]
                break

        if not gallery_id:
            # Fall back to user galleries
            galleries = api.get_user_galleries()
            if galleries:
                gallery_id = galleries[0]["id"]

        if not gallery_id:
            pytest.skip("No galleries available")

        # Endpoint may return empty list - that's OK
        related = api.get_gallery_related(gallery_id=gallery_id)
        assert isinstance(related, list)

    def test_put_gallery_sort(self, api, user_item_id):
        """Test sorting gallery items"""
        # Create a test gallery with items
        gallery = api.create_gallery(
            name="TEST_gallery_sort",
            description="Test gallery for sort test",
        )
        gallery_id = gallery["id"]

        try:
            # Add an item to the gallery
            api.post_gallery_item(gallery_id=gallery_id, item_id=user_item_id)

            # Try to sort (with single item, just verify it doesn't error)
            result = api.put_gallery_sort(
                gallery_id=gallery_id,
                json={"itemIds": [user_item_id]},
            )
            # Result may be empty dict for successful sort
            assert result is not None or result == {}

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 403:
                pytest.skip("403 Forbidden - may only work on owned galleries")
            raise
        finally:
            try:
                api.delete_gallery(gallery_id=gallery_id)
            except Exception:
                pass


class TestNFTEndpoints:
    """Test NFT-related endpoints"""

    def test_post_galleries_nft(self, api):
        """Test getting/creating NFT gallery"""
        result = api.post_galleries_nft()
        assert result is not None
        # Should return gallery data with an ID
        assert result.get("id") or isinstance(result, dict)


class TestFavoritesOperations:
    """Test favorites add/remove operations"""

    def test_add_and_remove_favorite_gallery(self, api):
        """Test adding and removing a gallery from favorites"""
        # Find a channel with galleries
        channels = api.get_channels_list(page=1, count=10)
        gallery_id = None
        for ch in channels:
            galleries = api.get_channel_galleries(channel_id=ch["id"], params={"count": 5})
            if galleries:
                # Pick a gallery that's not already in favorites
                current_favs = api.get_favorite_galleries(params={"page": 1})
                fav_ids = {f.get("id") for f in current_favs}
                for g in galleries:
                    if g["id"] not in fav_ids:
                        gallery_id = g["id"]
                        break
                if gallery_id:
                    break

        if not gallery_id:
            pytest.skip("No non-favorited galleries available")

        try:
            # Add to favorites
            api.post_favorite(json={"model": "Gallery", "id": gallery_id})

            # Verify it's in favorites
            favorites = api.get_favorite_galleries(params={"page": 1})
            fav_ids = [f.get("id") for f in favorites]
            assert gallery_id in fav_ids

            # Remove from favorites
            api.delete_favorite(json={"model": "Gallery", "id": gallery_id})

            # Verify removal
            favorites = api.get_favorite_galleries(params={"page": 1})
            fav_ids = [f.get("id") for f in favorites]
            assert gallery_id not in fav_ids

        except requests.exceptions.HTTPError as e:
            # Some items may have restrictions
            if e.response.status_code not in [400, 409]:
                raise

    def test_add_and_remove_favorite_artist(self, api, artist_id):
        """Test adding and removing an artist from favorites"""
        try:
            # Add to favorites
            api.post_favorite(json={"model": "Artist", "id": artist_id})

            # Remove from favorites
            api.delete_favorite(json={"model": "Artist", "id": artist_id})

        except requests.exceptions.HTTPError as e:
            if e.response.status_code not in [400, 409]:
                raise


class TestDeviceOperations:
    """Test device modification operations"""

    def test_put_device(self, api, device_id):
        """Test updating device settings"""
        # Get original settings
        original = api.get_device(device_id=device_id)
        original_gesture = original.get("gestureFeedback")

        try:
            # Update a safe setting
            updated = api.put_device(
                device_id=device_id,
                json={"gestureFeedback": not original_gesture if original_gesture is not None else True},
            )
            assert updated is not None

        finally:
            # Restore original setting
            if original_gesture is not None:
                api.put_device(device_id=device_id, json={"gestureFeedback": original_gesture})

    def test_post_device_preview(self, api, device_id, static_image_item_id):
        """Test previewing a static image on device"""
        try:
            result = api.post_device_preview(device_id=device_id, item_id=static_image_item_id)
            # Preview should return device data or empty response
            assert result is not None or result == {}
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                pytest.skip("Device may be offline")
            elif e.response.status_code == 400:
                error_text = str(e.response.text).lower()
                if "video" in error_text or "gif" in error_text:
                    pytest.skip(f"Item cannot be previewed: {e.response.text}")
            raise

    def test_post_device_item(self, api, device_id, user_item_id):
        """Test sending an item to device"""
        try:
            result = api.post_device_item(device_id=device_id, item_id=user_item_id)
            assert result is not None or result == {}
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                pytest.skip("Device may be offline")
            raise

    def test_post_device_sync(self, api, device_id):
        """Test syncing device"""
        try:
            result = api.post_device_sync(device_id=device_id)
            # Sync returns device data
            assert result is not None
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                pytest.skip("Device may be offline")
            raise

    def test_get_and_put_device_scheduler(self, api, device_id):
        """Test getting and updating device scheduler"""
        # Get current scheduler
        scheduler = api.get_device_scheduler(device_id=device_id)
        assert scheduler is not None

        # Try to update with same data (safe operation)
        try:
            result = api.put_device_scheduler(
                device_id=device_id,
                json=scheduler,
            )
            assert result is not None or result == {}
        except requests.exceptions.HTTPError as e:
            if e.response.status_code in [400, 403]:
                pytest.skip("Scheduler update may have restrictions")
            raise


class TestChannelDetailEndpoints:
    """Test additional channel detail endpoints"""

    def test_get_channel_artists(self, api, channel_id):
        """Test getting artists in a channel"""
        artists = api.get_channel_artists(channel_id=channel_id, params={"count": 5})
        assert isinstance(artists, list)

    def test_get_channel_galleries(self, api, channel_id):
        """Test getting galleries in a channel"""
        galleries = api.get_channel_galleries(channel_id=channel_id, params={"count": 5})
        assert isinstance(galleries, list)

    def test_get_channel_articles(self, api, channel_id):
        """Test getting articles in a channel"""
        articles = api.get_channel_articles(channel_id=channel_id, params={"count": 5})
        assert isinstance(articles, list)


class TestArtistDetailEndpoints:
    """Test additional artist detail endpoints"""

    def test_get_artist_galleries(self, api, artist_id):
        """Test getting artist galleries"""
        galleries = api.get_artist_galleries(artist_id=artist_id, params={"page": 1, "count": 5})
        assert isinstance(galleries, list)

    def test_get_artist_articles(self, api, artist_id):
        """Test getting artist articles"""
        articles = api.get_artist_articles(artist_id=artist_id, params={"page": 1, "count": 5})
        assert isinstance(articles, list)


class TestCategoryDetailEndpoints:
    """Test additional category detail endpoints"""

    def test_get_category_galleries(self, api, category_id):
        """Test getting category galleries"""
        galleries = api.get_category_galleries(category_id=category_id, params={"page": 1, "count": 5})
        assert isinstance(galleries, list)

    def test_get_category_articles(self, api, category_id):
        """Test getting category articles"""
        articles = api.get_category_articles(category_id=category_id, params={"page": 1, "count": 5})
        assert isinstance(articles, list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
