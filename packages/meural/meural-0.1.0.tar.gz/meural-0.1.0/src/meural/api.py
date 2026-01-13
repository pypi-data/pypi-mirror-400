"""
Meural API Client Library

A Python client for interacting with the Meural digital art frame API.
Provides comprehensive access to device management, gallery operations,
image uploads, and content discovery.
"""
import requests
from typing import Optional, Dict, Any, List, Union, Tuple
import os
import logging
from functools import wraps
from meural.auth import MeuralCognitoAuth

logger = logging.getLogger(__name__)


class MeuralAPI:
    @classmethod
    def from_env(cls) -> "MeuralAPI":
        """Create MeuralAPI instance from environment variables or ~/.meural file.

        Checks in order:
        1. MEURAL_USERNAME and MEURAL_PASSWORD environment variables
        2. ~/.meural file with KEY=VALUE format

        Returns:
            MeuralAPI instance

        Raises:
            ValueError: If credentials are not found
        """
        username = os.getenv("MEURAL_USERNAME")
        password = os.getenv("MEURAL_PASSWORD")

        # If not in env, try ~/.meural file
        if not (username and password):
            meural_file = os.path.expanduser("~/.meural")
            if os.path.exists(meural_file):
                with open(meural_file) as f:
                    for line in f:
                        line = line.strip()
                        if line and "=" in line and not line.startswith("#"):
                            key, value = line.split("=", 1)
                            if key == "MEURAL_USERNAME":
                                username = value
                            elif key == "MEURAL_PASSWORD":
                                password = value

        if username and password:
            return cls(username=username, password=password)
        else:
            raise ValueError(
                "Credentials not found. Set MEURAL_USERNAME/MEURAL_PASSWORD env vars "
                "or create ~/.meural file with KEY=VALUE format"
            )

    DEFAULT_TIMEOUT = 5
    WRITE_TIMEOUT = 60  # POST/PUT/DELETE operations are slower
    UPLOAD_TIMEOUT = 60

    # Endpoints that need longer timeouts (slow server-side processing)
    SLOW_ENDPOINTS = {
        "/categories",  # 296 categories, slow to fetch
        "/favorites",   # All favorites endpoints can be slow
    }

    # API endpoint definitions
    # Format: method_name => (HTTP_METHOD, endpoint_template, optional_params)
    # optional_params is a dict of param_name: description
    API_ENDPOINTS = {
        # Device endpoints
        "get_user_devices": ("GET", "/user/devices", {}),
        "get_device": ("GET", "/devices/{device_id}", {}),
        "put_device": ("PUT", "/devices/{device_id}", {}),
        "patch_device": ("PATCH", "/devices/{device_id}", {}),
        "delete_device": ("DELETE", "/devices/{device_id}", {}),
        "post_device_item": ("POST", "/devices/{device_id}/items/{item_id}", {}),
        "post_device_preview": ("POST", "/devices/{device_id}/preview/{item_id}", {}),
        "post_device_gallery": (
            "POST",
            "/devices/{device_id}/galleries/{gallery_id}",
            {},
        ),
        "get_display_languages": ("GET", "/devices/display_languages", {}),
        "get_device_scheduler": ("GET", "/devices/{device_id}/scheduler", {}),
        "put_device_scheduler": ("PUT", "/devices/{device_id}/scheduler", {}),
        "delete_device_gallery": (
            "DELETE",
            "/devices/{device_id}/galleries/{gallery_id}",
            {},
        ),
        "get_device_galleries": (
            "GET",
            "/devices/{device_id}/galleries",
            {
                "page": "Page number for pagination",
                "count": "Number of items per page",
            },
        ),
        "get_device_albums": (
            "GET",
            "/devices/{device_id}/albums",
            {
                "page": "Page number for pagination",
                "count": "Number of items per page",
            },
        ),
        # Gallery endpoints
        "get_user_galleries": ("GET", "/user/galleries", {}),
        "post_gallery": ("POST", "/galleries", {}),
        "get_gallery": ("GET", "/galleries/{gallery_id}", {}),
        "put_gallery": ("PUT", "/galleries/{gallery_id}", {}),
        "delete_gallery": ("DELETE", "/galleries/{gallery_id}", {}),
        "get_gallery_items": (
            "GET",
            "/galleries/{gallery_id}/items",
            {
                "page": "Page number for pagination",
                "limit": "Number of items per page",
                "offset": "Offset for pagination",
            },
        ),
        "post_gallery_item": ("POST", "/galleries/{gallery_id}/items/{item_id}", {}),
        "delete_gallery_item": (
            "DELETE",
            "/galleries/{gallery_id}/items/{item_id}",
            {},
        ),
        "get_gallery_shares": ("GET", "/galleries/{gallery_id}/shares", {}),
        "get_gallery_related": ("GET", "/galleries/{gallery_id}/related", {}),
        "put_gallery_sort": (
            "PUT",
            "/galleries/{gallery_id}/sort",
            {"itemIds": "Array of item IDs in desired order"},
        ),
        # Item endpoints
        "get_item": ("GET", "/items/{item_id}", {}),
        "put_item": ("PUT", "/items/{item_id}", {}),
        "put_item_crop": ("PUT", "/items/{item_id}/crop", {}),
        "delete_item": ("DELETE", "/items/{item_id}", {}),
        "post_item": ("POST", "/items", {}),
        # Device registration and sync
        "post_device": (
            "POST",
            "/devices",
            {"productKey": "Product key from back of device (required)"},
        ),
        "post_device_sync": ("POST", "/devices/{device_id}/sync", {}),
        # User feedback
        "post_user_feedback": (
            "POST",
            "/user/feedback",
            {
                "rating": "Rating 1-5 (required)",
                "source": "Email address (required)",
                "message": "Feedback message",
            },
        ),
        # NFT gallery
        "post_galleries_nft": ("POST", "/galleries/nft", {}),
        # Favorites endpoints
        "post_favorite": (
            "POST",
            "/favorites",
            {
                "model": "Type of thing to favorite (e.g., 'Gallery', 'Item', 'Group', 'Channel', 'Artist')",
                "id": "ID of the thing to favorite",
            },
        ),
        "delete_favorite": ("DELETE", "/favorites", {}),
        "get_favorite_galleries": (
            "GET",
            "/favorites/galleries",
            {"page": "Page number for pagination"},
        ),
        "get_favorite_items": (
            "GET",
            "/favorites/items",
            {"page": "Page number for pagination"},
        ),
        "get_favorite_artists": (
            "GET",
            "/favorites/artists",
            {"page": "Page number for pagination"},
        ),
        "get_favorite_categories": (
            "GET",
            "/favorites/categories",
            {"page": "Page number for pagination"},
        ),
        "get_favorite_channels": (
            "GET",
            "/favorites/channels",
            {"page": "Page number for pagination"},
        ),
        "get_favorite_articles": (
            "GET",
            "/favorites/articles",
            {"page": "Page number for pagination"},
        ),
        # User endpoints
        "get_user": ("GET", "/user", {}),
        "get_user_items": (
            "GET",
            "/user/items",
            {"page": "Page number for pagination"},
        ),
        "get_groups": (
            "GET",
            "/groups",
            {"page": "Page number for pagination", "count": "Number of items per page"},
        ),
        # Group detail endpoints
        "get_group": ("GET", "/groups/{group_id}", {}),
        "get_group_categories": (
            "GET",
            "/groups/{group_id}/categories",
            {"page": "Page number for pagination", "count": "Number of items per page"},
        ),
        # Category endpoints
        "get_categories": (
            "GET",
            "/categories",
            {"page": "Page number for pagination", "count": "Number of items per page"},
        ),
        "get_category": ("GET", "/categories/{category_id}", {}),
        "get_category_items": (
            "GET",
            "/categories/{category_id}/items",
            {
                "page": "Page number for pagination",
                "count": "Number of items per page",
                "sort": "Sort order (e.g., 'date_updated__dsc')",
            },
        ),
        "get_category_galleries": (
            "GET",
            "/categories/{category_id}/galleries",
            {
                "page": "Page number for pagination",
                "count": "Number of items per page",
            },
        ),
        "get_category_articles": (
            "GET",
            "/categories/{category_id}/articles",
            {"page": "Page number for pagination"},
        ),
        "get_channels": (
            "GET",
            "/channels",
            {
                "page": "Page number for pagination",
                "count": "Number of items per page",
                "sort": "Sort order (e.g., 'order__asc')",
            },
        ),
        "get_artists": (
            "GET",
            "/artists",
            {"page": "Page number for pagination", "count": "Number of items per page"},
        ),
        "get_feed": ("GET", "/feed", {"page": "Page number for pagination"}),
        "search": (
            "GET",
            "/search",
            {"q": "Search query string", "page": "Page number for pagination"},
        ),
        "get_article": ("GET", "/articles/{article_id}", {}),
        # Channel detail endpoints (discovered from browser)
        "get_channel": ("GET", "/channels/{channel_id}", {}),
        "get_channel_items": (
            "GET",
            "/channels/{channel_id}/items",
            {
                "page": "Page number for pagination",
                "sort": "Sort order (e.g., 'date_updated__dsc')",
            },
        ),
        "get_channel_artists": (
            "GET",
            "/channels/{channel_id}/artists",
            {"count": "Number of items to return"},
        ),
        "get_channel_galleries": (
            "GET",
            "/channels/{channel_id}/galleries",
            {"count": "Number of items to return"},
        ),
        "get_channel_articles": (
            "GET",
            "/channels/{channel_id}/articles",
            {"count": "Number of items to return"},
        ),
        # Artist detail endpoints (discovered from browser)
        "get_artist": ("GET", "/artists/{artist_id}", {}),
        "get_artist_items": (
            "GET",
            "/artists/{artist_id}/items",
            {
                "page": "Page number for pagination",
                "sort": "Sort order (e.g., 'date_updated__dsc')",
            },
        ),
        "get_artist_galleries": (
            "GET",
            "/artists/{artist_id}/galleries",
            {
                "page": "Page number for pagination",
                "count": "Number of items to return",
            },
        ),
        "get_artist_articles": (
            "GET",
            "/artists/{artist_id}/articles",
            {
                "page": "Page number for pagination",
                "count": "Number of items to return",
            },
        ),
        "get_artist_related": ("GET", "/artists/{artist_id}/related", {}),
        # User albums endpoint (NEW - not in old API)
        "get_user_albums": (
            "GET",
            "/user/albums",
            {"page": "Page number for pagination"},
        ),
    }

    def __init__(self, username: str, password: str):
        """
        Initialize Meural API client using Cognito authentication.

        Args:
            username: Meural account email
            password: Meural account password
        """
        self.base_url = "https://api.meural.com/v1"
        self.session = requests.Session()

        # Use Cognito authentication
        self.cognito_auth = MeuralCognitoAuth(username, password)

        # Authenticate and get Meural API token (authorization code)
        self.cognito_auth.authenticate()
        self.token = self.cognito_auth.get_valid_token()

        logger.debug(f"Meural API token obtained: {self.token}...")
        self.session.headers.update(self._get_auth_headers())

    def _get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers"""
        return {
            "Authorization": f"Token {self.token}",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
            "X-Meural-Api-Version": "4",
            "X-Meural-Source-Platform": "web",
            "Origin": "https://my.meural.netgear.com",
        }

    def _handle_api_error(self, e: requests.exceptions.RequestException) -> None:
        """Centralized error handling"""
        error_msg = f"API error: {e}"
        logger.error(error_msg)

        if hasattr(e, "response") and e.response is not None:
            response_text = e.response.text
            logger.error(f"Response: {response_text}")

    def _refresh_auth(self) -> None:
        """Clear cached tokens and re-authenticate"""
        logger.info("Refreshing authentication...")

        # Delete token cache file if it exists
        cache_file = self.cognito_auth.TOKEN_CACHE_FILE
        if os.path.exists(cache_file):
            os.remove(cache_file)
            logger.info(f"Deleted token cache: {cache_file}")

        # Clear internal token state
        self.cognito_auth.tokens = None
        self.cognito_auth.token_expiry = None

        # Re-authenticate
        self.cognito_auth.authenticate()
        self.token = self.cognito_auth.get_valid_token()

        # Update session headers with new token
        self.session.headers.update(self._get_auth_headers())
        logger.info("Re-authentication successful")

    def _make_request(
        self,
        method: str,
        endpoint: str,
        timeout: Optional[int] = None,
        _retry_auth: bool = True,
        **kwargs,
    ) -> requests.Response:
        """Make an HTTP request with standard error handling and auto-retry on auth failure"""
        url = f"{self.base_url}{endpoint}"

        # Determine appropriate timeout if not explicitly provided
        if timeout is None:
            if method in ("POST", "PUT", "DELETE", "PATCH"):
                timeout = self.WRITE_TIMEOUT
            elif any(endpoint.startswith(slow) for slow in self.SLOW_ENDPOINTS):
                timeout = self.WRITE_TIMEOUT
            else:
                timeout = self.DEFAULT_TIMEOUT

        try:
            response = self.session.request(
                method=method, url=url, timeout=timeout, **kwargs
            )
            response.raise_for_status()
            return response

        except requests.exceptions.HTTPError as e:
            # Check for 401 Unauthorized - token may be expired
            if e.response is not None and e.response.status_code == 401 and _retry_auth:
                logger.info("Got 401 Unauthorized, attempting to re-authenticate...")
                self._refresh_auth()
                # Retry the request once (with _retry_auth=False to prevent infinite loop)
                return self._make_request(method, endpoint, timeout, _retry_auth=False, **kwargs)

            self._handle_api_error(e)
            raise

        except requests.exceptions.RequestException as e:
            self._handle_api_error(e)
            raise

    def _extract_data(self, response: requests.Response, default: Any = None) -> Any:
        """Extract data from response JSON"""
        try:
            json_data = response.json()
            return json_data.get("data", default)
        except ValueError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            return default

    def _parse_endpoint_info(self, endpoint_info: tuple) -> Tuple[str, str, Dict[str, str]]:
        """Parse endpoint info tuple into its components

        Args:
            endpoint_info: Tuple of (method, endpoint_template) or (method, endpoint_template, optional_params)

        Returns:
            Tuple of (method, endpoint_template, optional_params)
        """
        if len(endpoint_info) == 2:
            method, endpoint_template = endpoint_info
            optional_params = {}
        else:
            method, endpoint_template, optional_params = endpoint_info
        return method, endpoint_template, optional_params

    def __getattr__(self, name: str):
        """Auto-generate API methods based on endpoint definitions"""
        if name not in self.API_ENDPOINTS:
            raise AttributeError(
                f"'{self.__class__.__name__}' object has no attribute '{name}'"
            )

        endpoint_info = self.API_ENDPOINTS[name]
        method, endpoint_template, optional_params = self._parse_endpoint_info(endpoint_info)

        def api_method(**kwargs):
            # Extract required parameters from endpoint template
            import re

            required_params = re.findall(r"\{(\w+)\}", endpoint_template)

            # Validate required parameters
            missing_params = set(required_params) - set(kwargs.keys())
            if missing_params:
                raise ValueError(f"Missing required parameters: {missing_params}")

            # Build endpoint by formatting with path parameters
            path_params = {p: kwargs.pop(p) for p in required_params}
            endpoint = endpoint_template.format(**path_params)

            # All remaining kwargs are passed to the request
            request_kwargs = kwargs

            # Make the request
            response = self._make_request(method, endpoint, **request_kwargs)
            return self._extract_data(response, {} if method != "GET" else [])

        return api_method

    # Special methods that don't fit the pattern

    def test_connection(self) -> bool:
        """Test if the API connection is working"""
        try:
            response = self._make_request("GET", "/user/devices")
            logger.info("API connection is working")
            return True
        except requests.exceptions.RequestException:
            logger.error("API connection test failed")
            return False

    def upload_image(
        self,
        image_path: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Upload an image to Meural"""
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")

        with open(image_path, "rb") as image_file:
            files = {"image": image_file}
            data = {}

            if title:
                data["name"] = title
            if description:
                data["description"] = description

            logger.info(f"Uploading image to /items endpoint: {image_path}")

            # For file uploads, temporarily remove Content-Type from session
            # so requests can set the correct multipart/form-data content type
            original_content_type = self.session.headers.pop("Content-Type", None)

            try:
                response = self._make_request(
                    "POST",
                    "/items",
                    files=files,
                    data=data,
                    timeout=self.UPLOAD_TIMEOUT,
                )

                result = self._extract_data(response, {})
                logger.info(f"Upload successful! Item ID: {result.get('id', 'unknown')}")
                return result
            finally:
                # Restore Content-Type header
                if original_content_type:
                    self.session.headers["Content-Type"] = original_content_type

    def get_devices(self) -> List[Dict[str, Any]]:
        """Get list of Meural devices"""
        response = self._make_request("GET", "/user/devices")
        return self._extract_data(response, [])

    def create_gallery(self, name: str, description: str = "") -> Dict[str, Any]:
        """Create a new gallery/playlist"""
        data = {"name": name, "description": description}
        gallery_data = self.post_gallery(json=data)

        if gallery_data.get("id"):
            logger.info(f"Gallery '{name}' created with ID: {gallery_data['id']}")
        return gallery_data

    def get_all_gallery_items(
        self, gallery_id: str, count: int = 100
    ) -> List[Dict[str, Any]]:
        """Get all items/images in a specific gallery"""
        all_items = []
        page = 1

        while True:
            params = {"page": page, "count": count}
            try:
                response = self._make_request(
                    "GET", f"/galleries/{gallery_id}/items", params=params
                )
                json_data = response.json()
                items = json_data.get("data", [])
                all_items.extend(items)

                # Check if there are more items
                if json_data.get("isLast", True) or not items:
                    break

                page += 1
            except requests.exceptions.RequestException as e:
                logger.error(f"Error fetching gallery items: {e}")
                break

        logger.info(f"Found {len(all_items)} items in gallery {gallery_id}")
        return all_items

    def get_gallery_items_paginated(
        self, gallery_id: str, page: int = 1, per_page: int = 50
    ) -> Dict[str, Any]:
        """Get items from a gallery with pagination (matching API structure)"""
        params = {"page": page}
        if per_page != 50:
            params["per_page"] = per_page

        try:
            response = self._make_request(
                "GET", f"/galleries/{gallery_id}/items", params=params
            )
            return response.json()
        except requests.exceptions.RequestException:
            return {"data": [], "isLast": True}

    def download_gallery_item(self, item_id: str, output_path: str) -> bool:
        """Download an image from a gallery item"""
        # Get item details
        try:
            item_data = self.get_item(item_id=item_id)
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get item details for {item_id}: {e}")
            return False

        image_url = item_data.get("originalImage") or item_data.get("image")

        if not image_url:
            logger.warning(f"No image URL found for item {item_id}")
            return False

        try:
            # Download the image
            image_response = requests.get(image_url, stream=True, timeout=30)
            image_response.raise_for_status()

            with open(output_path, "wb") as f:
                for chunk in image_response.iter_content(chunk_size=8192):
                    f.write(chunk)

            logger.info(f"Downloaded item {item_id} to {output_path}")
            return True

        except (requests.exceptions.RequestException, IOError) as e:
            logger.error(f"Error downloading item {item_id}: {e}")
            return False

    # Convenience methods

    def list_galleries(self) -> List[Dict[str, Any]]:
        """List all available galleries with their IDs for easy reference

        Returns:
            List of gallery dictionaries
        """
        galleries = self.get_user_galleries()
        logger.info(f"Found {len(galleries)} galleries")
        return galleries

    def find_gallery_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Find a gallery by name (case-insensitive)"""
        galleries = self.get_user_galleries()

        for gallery in galleries:
            if gallery.get("name", "").lower() == name.lower():
                return gallery

        return None

    def list_gallery_items(self, gallery_id: str) -> List[Dict[str, Any]]:
        """List all items in a gallery with detailed information

        Returns:
            List of item dictionaries
        """
        items = self.get_all_gallery_items(gallery_id)
        logger.info(f"Found {len(items)} items in gallery {gallery_id}")
        return items

    def search_gallery_items(
        self, gallery_id: str, search_term: str
    ) -> List[Dict[str, Any]]:
        """Search for items in a gallery by name or description"""
        all_items = self.get_all_gallery_items(gallery_id)
        search_term_lower = search_term.lower()

        matching_items = [
            item
            for item in all_items
            if search_term_lower in item.get("name", "").lower()
            or search_term_lower in item.get("description", "").lower()
        ]

        logger.info(
            f"Found {len(matching_items)} items matching '{search_term}' in gallery {gallery_id}"
        )
        return matching_items

    def upload_image_to_gallery(
        self,
        image_path: str,
        gallery_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Upload an image and add it to a specific gallery"""
        # First upload the image
        upload_result = self.upload_image(image_path, title, description)

        # Then add it to the gallery
        if upload_result and gallery_id:
            item_id = upload_result["id"]
            try:
                self.post_gallery_item(gallery_id=gallery_id, item_id=item_id)
                logger.info(f"Image {item_id} added to gallery {gallery_id}")
            except requests.exceptions.RequestException as e:
                logger.warning(f"Image uploaded but failed to add to gallery: {e}")
                raise

        return upload_result

    def list_endpoints(self) -> Dict[str, Dict[str, Any]]:
        """List all available API endpoints with their parameters

        Returns:
            Dictionary mapping endpoint names to their details
        """
        import re

        endpoints = {}
        for name, endpoint_info in self.API_ENDPOINTS.items():
            method, endpoint_template, optional_params = self._parse_endpoint_info(endpoint_info)

            # Extract path parameters
            path_params = re.findall(r"\{(\w+)\}", endpoint_template)

            endpoints[name] = {
                "method": method,
                "endpoint": endpoint_template,
                "path_params": path_params,
                "optional_params": optional_params,
            }

        logger.info(f"Listed {len(endpoints)} API endpoints")
        return endpoints

    def get_endpoint_info(self, method_name: str) -> Dict[str, Any]:
        """Get detailed information about a specific endpoint

        Args:
            method_name: Name of the API method

        Returns:
            Dictionary with endpoint details
        """
        if method_name not in self.API_ENDPOINTS:
            return {"error": f"Unknown method: {method_name}"}

        import re

        endpoint_info = self.API_ENDPOINTS[method_name]
        method, endpoint_template, optional_params = self._parse_endpoint_info(endpoint_info)

        path_params = re.findall(r"\{(\w+)\}", endpoint_template)

        return {
            "method": method,
            "endpoint": endpoint_template,
            "path_params": path_params,
            "optional_params": optional_params,
            "example_usage": self._generate_example_usage(
                method_name, path_params, optional_params
            ),
        }

    def _generate_example_usage(
        self, method_name: str, path_params: List[str], optional_params: Dict[str, str]
    ) -> str:
        """Generate example usage for a method"""
        args = []

        # Add path parameters
        for param in path_params:
            if param == "device_id":
                args.append(f'{param}="your_device_id"')
            elif param == "gallery_id":
                args.append(f'{param}="gallery_123"')
            elif param == "item_id":
                args.append(f'{param}="item_456"')
            elif param == "article_id":
                args.append(f'{param}="31"')
            else:
                args.append(f'{param}="value"')

        # Add example optional parameters
        if optional_params:
            args.append("params={")
            param_examples = []
            for param, desc in optional_params.items():
                if param == "q":
                    param_examples.append(f'    "{param}": "search term"')
                elif param == "page":
                    param_examples.append(f'    "{param}": 1')
                elif param == "count" or param == "limit":
                    param_examples.append(f'    "{param}": 20')
                elif param == "offset":
                    param_examples.append(f'    "{param}": 0')
                elif param == "sort":
                    param_examples.append(f'    "{param}": "order__asc"')
                else:
                    param_examples.append(f'    "{param}": "value"')
            args.append(",\n".join(param_examples))
            args.append("}")

        return f"api.{method_name}({', '.join(args)})"

    def search_content(self, query: str, page: int = 1) -> Dict[str, Any]:
        """Search for content on Meural

        Args:
            query: Search query string
            page: Page number for pagination (default: 1)

        Returns:
            Search results with galleries, items, artists, etc.
        """
        params = {"q": query, "page": page}
        try:
            response = self._make_request("GET", "/search", params=params)
            return response.json()
        except requests.exceptions.RequestException:
            return {"data": {}}

    def get_groups_list(self, page: int = 1, count: int = 64) -> List[Dict[str, Any]]:
        """Get list of groups/collections

        Args:
            page: Page number for pagination (default: 1)
            count: Number of items per page (default: 64)

        Returns:
            List of groups
        """
        params = {"page": page, "count": count}
        return self.get_groups(params=params)

    def get_channels_list(
        self, page: int = 1, count: int = 6, sort: str = "order__asc"
    ) -> List[Dict[str, Any]]:
        """Get list of channels

        Args:
            page: Page number for pagination (default: 1)
            count: Number of items per page (default: 6)
            sort: Sort order (default: "order__asc")

        Returns:
            List of channels
        """
        params = {"page": page, "count": count, "sort": sort}
        return self.get_channels(params=params)

    def get_artists_list(self, page: int = 1, count: int = 6) -> List[Dict[str, Any]]:
        """Get list of artists

        Args:
            page: Page number for pagination (default: 1)
            count: Number of items per page (default: 6)

        Returns:
            List of artists
        """
        params = {"page": page, "count": count}
        return self.get_artists(params=params)

    def get_user_items_list(self, page: int = 1) -> List[Dict[str, Any]]:
        """Get list of items uploaded by the user

        Args:
            page: Page number for pagination (default: 1)

        Returns:
            List of user's uploaded items
        """
        params = {"page": page}
        try:
            response = self._make_request("GET", "/user/items", params=params)
            json_data = response.json()
            return json_data.get("data", [])
        except requests.exceptions.RequestException:
            return []

    def get_favorite_galleries_list(self, page: int = 1) -> List[Dict[str, Any]]:
        """Get list of user's favorite galleries

        Args:
            page: Page number for pagination (default: 1)

        Returns:
            List of favorite galleries
        """
        params = {"page": page}
        return self.get_favorite_galleries(params=params)

    def get_favorite_items_list(self, page: int = 1) -> List[Dict[str, Any]]:
        """Get list of user's favorite items

        Args:
            page: Page number for pagination (default: 1)

        Returns:
            List of favorite items
        """
        params = {"page": page}
        return self.get_favorite_items(params=params)

    def get_feed_content(self, page: int = 1) -> Dict[str, Any]:
        """Get feed content

        Args:
            page: Page number for pagination (default: 1)

        Returns:
            Feed content dictionary
        """
        params = {"page": page}
        try:
            response = self._make_request("GET", "/feed", params=params)
            return response.json()
        except requests.exceptions.RequestException:
            return {"data": []}

    def update_device_settings(
        self, device_id: str, settings: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update device settings

        Args:
            device_id: ID of the device to update
            settings: Dictionary of settings to update (e.g., name, orientation, brightness)

        Returns:
            Updated device data
        """
        return self.put_device(device_id=device_id, json=settings)

    def list_devices(self) -> List[Dict[str, Any]]:
        """List all available devices with their details

        Returns:
            List of device dictionaries
        """
        devices = self.get_devices()
        logger.info(f"Found {len(devices)} devices")
        return devices
