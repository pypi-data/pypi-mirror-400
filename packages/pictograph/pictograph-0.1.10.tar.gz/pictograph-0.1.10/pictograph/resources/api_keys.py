"""
API Key management operations
"""

import logging
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)


class APIKeys:
    """
    API Key management operations for the Pictograph API.

    Allows managing API keys programmatically using an existing API key
    with admin or owner role.
    """

    def __init__(self, http_client):
        self.http = http_client

    def list(self, organization_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all API keys for the organization.

        Args:
            organization_id: Organization UUID. If not provided, uses the
                           organization associated with the current API key.

        Returns:
            List of API key objects (without the actual key values)

        Example:
            >>> keys = client.api_keys.list()
            >>> for key in keys:
            ...     print(key['name'], key['key_prefix'], key['role'])
        """
        # If organization_id not provided, we need to get it from the auth context
        # The backend will use the API key's organization if not specified
        if not organization_id:
            # Make a request to get the org from current auth
            # The list endpoint requires organization_id as a query param
            raise ValueError(
                "organization_id is required. You can get it from client.datasets.list() "
                "or any dataset's organization_id field."
            )

        response = self.http.get(
            "/api/v1/api-keys/",
            params={"organization_id": organization_id}
        )
        return response.get("api_keys", [])

    def create(
        self,
        organization_id: str,
        name: str,
        role: str = "member",
        rate_limit: Optional[int] = None,
        expires_at: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new API key.

        IMPORTANT: The full API key is only returned once during creation.
        Store it securely as it cannot be retrieved again.

        Args:
            organization_id: Organization UUID
            name: User-friendly name for the API key
            role: Role for the key - "viewer", "member", "admin", or "owner"
                  (default: "member")
            rate_limit: Custom rate limit (requests/hour). Defaults to org tier limit.
            expires_at: Optional expiration timestamp (ISO 8601 format)

        Returns:
            Dict containing:
            - api_key: The full API key (STORE THIS SECURELY)
            - key_id: UUID of the API key
            - key_prefix: First 12 characters (for identification)
            - name: Name of the key
            - role: Role assigned
            - rate_limit: Rate limit in requests/hour
            - warning: Reminder to store the key securely

        Example:
            >>> result = client.api_keys.create(
            ...     organization_id="org-uuid",
            ...     name="CI/CD Pipeline",
            ...     role="member"
            ... )
            >>> print("API Key:", result['api_key'])  # Store this!
            >>> print("Key ID:", result['key_id'])

            >>> # Create with expiration
            >>> result = client.api_keys.create(
            ...     organization_id="org-uuid",
            ...     name="Temporary Access",
            ...     role="viewer",
            ...     expires_at="2025-12-31T23:59:59Z"
            ... )
        """
        data = {
            "organization_id": organization_id,
            "name": name,
            "role": role
        }

        if rate_limit is not None:
            data["rate_limit"] = rate_limit

        if expires_at is not None:
            data["expires_at"] = expires_at

        response = self.http.post("/api/v1/api-keys/", json=data)

        logger.warning(
            f"Created API key '{name}'. The full key is only shown once - store it securely!"
        )

        return response

    def get(self, key_id: str) -> Dict[str, Any]:
        """
        Get details of a specific API key.

        Note: This returns metadata only, not the actual key value.

        Args:
            key_id: UUID of the API key

        Returns:
            API key metadata object

        Example:
            >>> key_info = client.api_keys.get("key-uuid")
            >>> print(key_info['name'], key_info['last_used_at'])
        """
        response = self.http.get(f"/api/v1/api-keys/{key_id}")
        return response.get("api_key")

    def update(
        self,
        key_id: str,
        name: Optional[str] = None,
        rate_limit: Optional[int] = None,
        is_active: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        Update an API key.

        Args:
            key_id: UUID of the API key
            name: New name for the key
            rate_limit: New rate limit
            is_active: Enable/disable the key

        Returns:
            Updated API key metadata

        Example:
            >>> # Rename a key
            >>> client.api_keys.update("key-uuid", name="New Name")

            >>> # Disable a key
            >>> client.api_keys.update("key-uuid", is_active=False)

            >>> # Update rate limit
            >>> client.api_keys.update("key-uuid", rate_limit=10000)
        """
        data = {}

        if name is not None:
            data["name"] = name
        if rate_limit is not None:
            data["rate_limit"] = rate_limit
        if is_active is not None:
            data["is_active"] = is_active

        if not data:
            raise ValueError("At least one field (name, rate_limit, is_active) must be provided")

        response = self.http.patch(f"/api/v1/api-keys/{key_id}", json=data)
        return response.get("api_key")

    def delete(self, key_id: str) -> Dict[str, Any]:
        """
        Delete (revoke) an API key.

        This is permanent and cannot be undone. The key will immediately
        stop working for all requests.

        Args:
            key_id: UUID of the API key

        Returns:
            Success message

        Example:
            >>> client.api_keys.delete("key-uuid")
            >>> print("Key revoked successfully")
        """
        response = self.http.delete(f"/api/v1/api-keys/{key_id}")
        logger.info(f"Deleted API key {key_id}")
        return response
