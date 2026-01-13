#!/usr/bin/env python3
"""
AWS Cognito authentication module for Meural API.

Handles authentication with AWS Cognito using SRP (Secure Remote Password) protocol.
Provides token management including caching and automatic refresh for Meural API access.
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, Optional
import logging

from pycognito import Cognito
import requests

logger = logging.getLogger(__name__)


class MeuralCognitoAuth:
    """Handle Meural authentication via AWS Cognito"""

    # Cognito configuration from HAR analysis
    USER_POOL_ID = "eu-west-1_eHc7fzKFg"  # Extracted from token issuer
    CLIENT_ID = "487bd4kvb1fnop6mbgk8gu5ibf"  # From HAR ClientId
    REGION = "eu-west-1"

    # Token cache file
    TOKEN_CACHE_FILE = "cognito_tokens.json"

    # Meural OAuth configuration
    MEURAL_CLIENT_ID = "3ui6nklcaqoij8inrkm06gfk4s"
    MEURAL_REDIRECT_URI = "https://my.meural.netgear.com/"
    MEURAL_AUTH_URL = "https://accounts2.netgear.com/api/oauth/authorize"

    def __init__(self, username: str, password: str):
        """Initialize Cognito client with credentials"""
        self.username = username
        self.password = password

        # Initialize Cognito client
        self.cognito = Cognito(
            user_pool_id=self.USER_POOL_ID,
            client_id=self.CLIENT_ID,
            user_pool_region=self.REGION,
            username=username,
        )

        self.tokens = None
        self.token_expiry = None

    def authenticate(self) -> Dict[str, str]:
        """
        Authenticate with Cognito using SRP flow.

        Returns:
            Dict with access_token, id_token, and refresh_token
        """
        # Check for cached valid tokens first
        cached_tokens = self._load_cached_tokens()
        if cached_tokens:
            logger.info("Using cached tokens")
            return cached_tokens

        logger.info(f"Authenticating user: {self.username}")

        # Authenticate using SRP (matches the HAR flow)
        self.cognito.authenticate(password=self.password)

        # Get tokens from the Cognito client
        self.tokens = {
            "access_token": self.cognito.access_token,
            "id_token": self.cognito.id_token,
            "refresh_token": self.cognito.refresh_token,
        }

        # Calculate token expiry (tokens typically valid for 1 hour)
        self.token_expiry = datetime.now() + timedelta(hours=1)

        # Cache the tokens
        self._cache_tokens()

        logger.info("Authentication successful!")
        return self.tokens

    def refresh_access_token(self) -> Dict[str, str]:
        """Refresh the access token using the refresh token.

        Returns:
            Dict with updated access_token, id_token, and refresh_token
        """
        if not self.tokens or "refresh_token" not in self.tokens:
            logger.info("No refresh token available, re-authenticating...")
            return self.authenticate()

        logger.info("Refreshing access token...")

        # Use the refresh token to get new tokens
        self.cognito.refresh_token = self.tokens["refresh_token"]
        self.cognito.renew_access_token()

        # Update tokens
        self.tokens = {
            "access_token": self.cognito.access_token,
            "id_token": self.cognito.id_token,
            "refresh_token": self.tokens[
                "refresh_token"
            ],  # Keep the same refresh token
        }

        # Ensure cognito object has the updated tokens
        self.cognito.access_token = self.tokens["access_token"]
        self.cognito.id_token = self.tokens["id_token"]

        # Update expiry
        self.token_expiry = datetime.now() + timedelta(hours=1)

        # Cache the updated tokens
        self._cache_tokens()

        logger.info("Token refresh successful!")
        return self.tokens

    def get_valid_token(self) -> str:
        """Get a valid access token, refreshing if necessary.

        Returns:
            Valid access token string
        """
        # Load cached tokens if not already loaded
        if not self.tokens:
            cached_tokens = self._load_cached_tokens()
            if cached_tokens:
                self.tokens = cached_tokens

        # If no tokens or expired, authenticate
        if not self.tokens or not self._is_token_valid():
            self.authenticate()

        return self.tokens["access_token"]

    def get_user_attributes(self) -> Dict[str, any]:
        """Get user attributes from Cognito.

        Returns:
            Dict containing username and user attributes
        """
        # Ensure we have a valid token
        access_token = self.get_valid_token()

        # Set the access token on the cognito object
        self.cognito.access_token = access_token

        # Get user info
        user_obj = self.cognito.get_user()

        # Convert UserObj to dict
        user_info = {"username": user_obj.username, "user_attributes": {}}

        # Extract attributes if available
        if hasattr(user_obj, "_metadata") and isinstance(user_obj._metadata, dict):
            if "UserAttributes" in user_obj._metadata:
                for attr in user_obj._metadata["UserAttributes"]:
                    user_info["user_attributes"][attr["Name"]] = attr["Value"]

        return user_info

    def _is_token_valid(self) -> bool:
        """Check if the current token is still valid"""
        if not self.token_expiry:
            return False

        # Add 5 minute buffer for safety
        return datetime.now() < (self.token_expiry - timedelta(minutes=5))

    def _cache_tokens(self) -> None:
        """Cache tokens to file for reuse"""
        if not self.tokens:
            return

        cache_data = {
            "tokens": self.tokens,
            "expiry": self.token_expiry.isoformat() if self.token_expiry else None,
            "username": self.username,
        }

        with open(self.TOKEN_CACHE_FILE, "w") as f:
            json.dump(cache_data, f, indent=2)

        logger.debug(f"Tokens cached to {self.TOKEN_CACHE_FILE}")

    def _load_cached_tokens(self) -> Optional[Dict[str, str]]:
        """Load cached tokens if they exist and are valid.

        Returns:
            Dict with tokens if valid, None otherwise
        """
        if not os.path.exists(self.TOKEN_CACHE_FILE):
            return None

        try:
            with open(self.TOKEN_CACHE_FILE, "r") as f:
                cache_data = json.load(f)

            # Check if cache is for the same user
            if cache_data.get("username") != self.username:
                logger.info("Cached tokens are for a different user")
                return None

            # Check expiry
            if cache_data.get("expiry"):
                expiry = datetime.fromisoformat(cache_data["expiry"])
                self.token_expiry = expiry

                if not self._is_token_valid():
                    logger.info("Cached tokens are expired")
                    # Try to refresh using the refresh token
                    if "refresh_token" in cache_data.get("tokens", {}):
                        self.tokens = cache_data["tokens"]
                        return self.refresh_access_token()
                    return None

            self.tokens = cache_data["tokens"]
            # Set tokens on cognito object
            self.cognito.access_token = self.tokens.get("access_token")
            self.cognito.id_token = self.tokens.get("id_token")
            self.cognito.refresh_token = self.tokens.get("refresh_token")
            return self.tokens

        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.error(f"Failed to load cached tokens: {e}")
            return None


def main() -> int:
    """Test the Cognito authentication.

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    # Load credentials from environment or prompt
    username = os.getenv("MEURAL_USERNAME") or input("Enter Meural username: ")
    password = os.getenv("MEURAL_PASSWORD") or input("Enter Meural password: ")

    # Create auth client
    auth = MeuralCognitoAuth(username, password)

    try:
        # Authenticate
        tokens = auth.authenticate()
        logger.info("Authentication successful!")
        logger.info(f"Access Token: {tokens['access_token'][:50]}...")
        logger.info(f"ID Token: {tokens['id_token'][:50]}...")
        logger.info(f"Refresh Token: {tokens['refresh_token'][:50]}...")

        # Get user attributes
        logger.info("Fetching user attributes...")
        user_info = auth.get_user_attributes()
        logger.info(f"User attributes: {json.dumps(user_info, indent=2)}")

        # Test token refresh
        logger.info("Testing token refresh...")
        refreshed_tokens = auth.refresh_access_token()
        logger.info(f"New Access Token: {refreshed_tokens['access_token'][:50]}...")

    except Exception as e:
        logger.error(f"Error: {e}")
        raise

    return 0


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    exit(main())
