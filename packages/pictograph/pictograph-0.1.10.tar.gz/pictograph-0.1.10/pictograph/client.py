"""
Main Pictograph API client
"""

import logging
from typing import Optional

from .http_client import HTTPClient
from .resources import Datasets, Images, Annotations, APIKeys, Exports

logger = logging.getLogger(__name__)


class Client:
    """
    Pictograph API client.

    Main entry point for interacting with the Pictograph annotation platform.

    Args:
        api_key: Your Pictograph API key (starts with 'pk_live_')
        base_url: API base URL (default: production URL)
        timeout: Request timeout in seconds (default: 30)
        max_retries: Maximum retry attempts for failed requests (default: 3)

    Example:
        >>> from pictograph import Client
        >>>
        >>> # Initialize client
        >>> client = Client(api_key="pk_live_your_key_here")
        >>>
        >>> # List datasets
        >>> datasets = client.datasets.list()
        >>>
        >>> # Download a dataset by name
        >>> client.datasets.download("my-dataset")  # Downloads to ~/.pictograph
        >>>
        >>> # Upload an image
        >>> client.images.upload("dataset-uuid", "/path/to/image.jpg")
        >>>
        >>> # Get annotations
        >>> annotations = client.annotations.get("image-uuid")
        >>>
        >>> # Save annotations
        >>> client.annotations.save("image-uuid", [
        ...     {
        ...         "id": "ann-1",
        ...         "class": "person",
        ...         "type": "bbox",
        ...         "bbox": [100, 200, 50, 80]
        ...     }
        ... ])
        >>>
        >>> # Create an export
        >>> export = client.exports.create("my-dataset", "Export v1")
        >>> path = client.exports.download(export['id'])
        >>>
        >>> # Manage API keys
        >>> keys = client.api_keys.list(org_id)
        >>> new_key = client.api_keys.create(org_id, "CI Pipeline", role="member")
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://pictograph.dev",
        timeout: int = 30,
        max_retries: int = 3
    ):
        """
        Initialize the Pictograph client.
        """
        if not api_key:
            raise ValueError("api_key is required")

        if not api_key.startswith("pk_live_"):
            logger.warning(
                "API key should start with 'pk_live_'. "
                "Make sure you're using the correct API key."
            )

        # Initialize HTTP client
        self._http = HTTPClient(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries
        )

        # Initialize resource modules
        self.datasets = Datasets(self._http)
        self.images = Images(self._http)
        self.annotations = Annotations(self._http)
        self.api_keys = APIKeys(self._http)
        self.exports = Exports(self._http)

    def close(self):
        """
        Close the HTTP session.

        It's recommended to use the client as a context manager to automatically
        close the session when done.
        """
        self._http.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __repr__(self):
        return f"<Pictograph Client>"
