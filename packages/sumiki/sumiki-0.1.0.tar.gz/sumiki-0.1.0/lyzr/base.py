"""
Base module class for all Lyzr Agent SDK modules
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lyzr.http import HTTPClient


class BaseModule:
    """Base class for all SDK modules"""

    def __init__(self, http_client: 'HTTPClient'):
        """
        Initialize module with HTTP client

        Args:
            http_client: Configured HTTP client instance
        """
        self._http = http_client
