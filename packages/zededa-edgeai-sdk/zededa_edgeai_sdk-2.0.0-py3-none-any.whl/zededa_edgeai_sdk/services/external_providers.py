"""External provider management service for CRUD operations.

Provides functionality to create, read, update, delete external model
providers and test their connectivity. All operations use provider name
as the unique identifier.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

import requests

from .http import HTTPService

__all__ = ["ExternalProviderService"]


class ExternalProviderService:
    """Service for managing external model provider configurations.
    
    Handles CRUD operations for external providers including creation,
    retrieval, updates, deletion, connection testing, and browsing
    provider contents.
    """

    def __init__(self, backend_url: str, http: HTTPService) -> None:
        """Initialize external provider service with backend URL and HTTP client.
        
        Sets up the service to communicate with external provider management
        endpoints using the provided HTTP service for consistent request
        handling and debug logging.
        """
        self.backend_url = backend_url.rstrip("/")
        self.http = http

    def list_external_providers(
        self,
        backend_jwt: str,
        *,
        limit: int = 50,
        page: int = 1,
        search: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List external providers accessible to the user with pagination.
        
        Queries the external providers endpoint to get a paginated list of
        configured providers, optionally filtering by search term.
        """
        url = f"{self.backend_url}/api/v1/external-providers"
        headers = {"Authorization": f"Bearer {backend_jwt}"}
        params: Dict[str, Any] = {"limit": limit, "page": page}
        if search:
            params["search"] = search

        try:
            response = self.http.request("GET", url, headers=headers, params=params)
        except requests.RequestException as exc:
            print(f"[ERROR] Unable to list external providers: {exc}")
            return {}

        if response.status_code != 200:
            print(
                f"[ERROR] Failed to list external providers: {response.status_code} {response.text}"
            )
            return {}

        try:
            return response.json() or {}
        except ValueError:
            print("[ERROR] Invalid JSON response from list external providers")
            return {}

    def create_external_provider(
        self, backend_jwt: str, payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a new external provider configuration.
        
        Submits provider details including name, type, URL, credentials,
        and configuration to create a new provider entry.
        """
        url = f"{self.backend_url}/api/v1/external-providers"
        headers = {
            "Authorization": f"Bearer {backend_jwt}",
            "Content-Type": "application/json",
        }

        try:
            response = self.http.request("POST", url, headers=headers, json=payload)
        except requests.RequestException as exc:
            raise ValueError(f"Failed to create external provider: {exc}") from exc

        if response.status_code != 201:
            error_text = response.text
            raise ValueError(
                f"Failed to create external provider: {response.status_code} {error_text}"
            )

        try:
            return response.json()
        except ValueError as exc:
            raise ValueError("Invalid JSON response from create external provider") from exc

    def get_external_provider(
        self, backend_jwt: str, provider_id: str
    ) -> Dict[str, Any]:
        """Retrieve details of a specific external provider.
        
        Fetches complete provider information including configuration,
        status, and metadata for the specified provider ID.
        Returns empty dict if provider not found or on error.
        """
        url = f"{self.backend_url}/api/v1/external-providers/id/{provider_id}"
        headers = {"Authorization": f"Bearer {backend_jwt}"}

        try:
            response = self.http.request("GET", url, headers=headers)
        except requests.RequestException as exc:
            print(f"[ERROR] Unable to get external provider: {exc}")
            return {}

        if response.status_code == 404:
            return {}
        
        if response.status_code != 200:
            print(f"[ERROR] Failed to get external provider: {response.status_code} {response.text}")
            return {}

        try:
            return response.json() or {}
        except ValueError:
            print("[ERROR] Invalid JSON response from get external provider")
            return {}

    def get_external_provider_by_name(
        self, backend_jwt: str, provider_name: str
    ) -> Dict[str, Any]:
        """Retrieve details of a specific external provider by name.
        
        Fetches complete provider information including configuration,
        status, and metadata for the specified provider name.
        """
        url = f"{self.backend_url}/api/v1/external-providers/name/{provider_name}"
        headers = {"Authorization": f"Bearer {backend_jwt}"}

        try:
            response = self.http.request("GET", url, headers=headers)
        except requests.RequestException as exc:
            print(f"[ERROR] Unable to get external provider by name: {exc}")
            return {}

        if response.status_code == 404:
            return {}
        
        if response.status_code != 200:
            raise ValueError(
                f"Failed to get external provider by name: {response.status_code} {response.text}"
            )

        try:
            return response.json() or {}
        except ValueError:
            print("[ERROR] Invalid JSON response from get external provider by name")
            return {}

    def update_external_provider(
        self, backend_jwt: str, provider_name: str, payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update an existing external provider configuration by name.
        
        Modifies provider details such as name, description, credentials,
        or configuration settings for the specified provider.
        """
        url = f"{self.backend_url}/api/v1/external-providers/name/{provider_name}"
        headers = {
            "Authorization": f"Bearer {backend_jwt}",
            "Content-Type": "application/json",
        }

        try:
            response = self.http.request("PUT", url, headers=headers, json=payload)
        except requests.RequestException as exc:
            raise ValueError(f"Failed to update external provider: {exc}") from exc

        if response.status_code != 200:
            error_text = response.text
            raise ValueError(
                f"Failed to update external provider: {response.status_code} {error_text}"
            )

        try:
            return response.json()
        except ValueError as exc:
            raise ValueError("Invalid JSON response from update external provider") from exc

    def delete_external_provider(self, backend_jwt: str, provider_name: str) -> bool:
        """Delete an external provider configuration by name.
        
        Removes the specified provider from the system. Returns True if
        deletion was successful, False if provider not found.
        """
        url = f"{self.backend_url}/api/v1/external-providers/name/{provider_name}"
        headers = {"Authorization": f"Bearer {backend_jwt}"}

        try:
            response = self.http.request("DELETE", url, headers=headers)
        except requests.RequestException as exc:
            raise ValueError(f"Failed to delete external provider: {exc}") from exc

        if response.status_code == 204:
            return True
        
        if response.status_code == 404:
            return False
        
        raise ValueError(
            f"Failed to delete external provider: {response.status_code} {response.text}"
        )

    def test_connection(
        self,
        backend_jwt: str,
        provider_name: str,
        overrides: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Test connectivity to an external provider by name.
        
        Validates that the provider configuration is correct and the
        service can connect to the external provider endpoint.
        """
        url = f"{self.backend_url}/api/v1/external-providers/name/{provider_name}/test-connection"
        headers = {
            "Authorization": f"Bearer {backend_jwt}",
            "Content-Type": "application/json",
        }
        payload = overrides or {}

        try:
            response = self.http.request("POST", url, headers=headers, json=payload)
        except requests.RequestException as exc:
            raise ValueError(f"Failed to test connection: {exc}") from exc

        if response.status_code != 200:
            error_text = response.text
            raise ValueError(f"Failed to test connection: {response.status_code} {error_text}")

        try:
            return response.json()
        except ValueError as exc:
            raise ValueError("Invalid JSON response from test connection") from exc

    def browse_provider(
        self,
        backend_jwt: str,
        provider_name: str,
        path: Optional[str] = None,
        search: Optional[str] = None,
        cursor: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Browse contents of an external provider by name.
        
        Lists models or directories available in the external provider,
        supporting pagination and search where applicable.
        """
        url = f"{self.backend_url}/api/v1/external-providers/name/{provider_name}/browse"
        headers = {"Authorization": f"Bearer {backend_jwt}"}
        params: Dict[str, Any] = {}
        if path:
            params["path"] = path
        if search:
            params["search"] = search
        if cursor:
            params["cursor"] = cursor

        try:
            response = self.http.request("GET", url, headers=headers, params=params)
        except requests.RequestException as exc:
            raise ValueError(f"Failed to browse provider: {exc}") from exc

        if response.status_code != 200:
            error_text = response.text
            # Try to extract a user-friendly error message from the response
            try:
                import json
                error_json = json.loads(error_text)
                detail = error_json.get("detail", "")
                # For SageMaker validation errors, provide a cleaner message
                if "ValidationException" in detail and "modelPackageGroupName" in detail:
                    raise ValueError(
                        f"Invalid path format for SageMaker. The path should be a valid model group name "
                        f"(alphanumeric and hyphens only, 1-63 characters). Got: '{path}'"
                    )
                # For other errors with detail, show just the detail
                if detail:
                    raise ValueError(f"Browse failed: {detail}")
            except json.JSONDecodeError:
                # If the response is not valid JSON, fall through to raise a generic error below
                pass
            raise ValueError(f"Failed to browse provider: {response.status_code} {error_text}")

        try:
            return response.json()
        except ValueError as exc:
            raise ValueError("Invalid JSON response from browse provider") from exc
