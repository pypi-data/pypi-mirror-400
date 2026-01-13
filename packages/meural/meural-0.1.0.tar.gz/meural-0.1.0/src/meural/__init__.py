"""Meural API client library for controlling Meural Canvas digital art frames."""

from meural.api import MeuralAPI
from meural.auth import MeuralCognitoAuth

__all__ = ["MeuralAPI", "MeuralCognitoAuth"]
__version__ = "0.1.0"
