"""High-level client interface for EdgeAI authentication.

Provides a simplified Python API for authentication workflows,
wrapping the underlying command system in a user-friendly interface.
"""

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

from .commands.login import execute_login
from .config import get_service_url
from .zededa_edgeai_sdk import ZededaEdgeAISDK
from .exceptions import AuthenticationError
from .environment import get_access_token


class ZededaEdgeAIClient:
    """High-level Python client interface for EdgeAI authentication.
    
    Provides a simplified, user-friendly API for authentication workflows
    including both browser-based and programmatic login methods. Wraps
    the underlying SDK and command system in an easy-to-use interface.
    """

    def __init__(
        self,
        service_url: Optional[str] = None,
        *,
        debug: bool = False,
    ) -> None:
        """Initialize the EdgeAI client with service configuration.
        
        Sets up the client with the backend service URL and debug settings,
        creating an internal SDK instance for handling authentication
        operations and service communication.
        """
        default_service_url = get_service_url()
        self.service_url = (service_url or default_service_url).rstrip("/")
        self.debug = debug
        self._sdk = ZededaEdgeAISDK(self.service_url, ui_url=self.service_url,
                                   debug=debug)

    def login(
        self,
        catalog_id: Optional[str] = None,
        *,
        email: Optional[str] = None,
        password: Optional[str] = None,
        prompt_password: bool = False,
    ) -> Dict[str, str]:
        """Authenticate and configure environment variables for the specified catalog.
        
        Performs authentication using either browser OAuth (when no email/password
        provided) or credential-based login. Automatically sets up environment
        variables for MLflow and storage access upon successful authentication.
        """
        try:
            credentials = execute_login(
                catalog_id,
                email=email,
                password=password,
                prompt_password=prompt_password,
                service_url=self.service_url,
                prompt_on_multiple=True,
                debug=self.debug,
                sdk=self._sdk,
            )
            print("\nLogin completed successfully.\n")
            return credentials
        except ValueError as exc:
            print(f"Error: {exc}")
            return {}
        except AuthenticationError as exc:
            print(f"Authentication failed: {exc}")
            return {}
        except Exception as exc:
            print(f"Unexpected error during login: {exc}")
            return {}

    def logout(self) -> Dict[str, Any]:
        """Terminate authenticated session locally and on the backend."""

        try:
            from .commands.logout import execute_logout

            result = execute_logout(
                service_url=self.service_url,
                sdk=self._sdk,
                debug=self.debug,
            )

            print(result.get("message", ""))

            backend = result.get("backend", {})
            if backend.get("attempted") and not backend.get("success"):
                detail = backend.get("message")
                if detail:
                    print(f"Warning: {detail}")

            return result
        except Exception as exc:  # pragma: no cover - defensive
            print(f"Logout failed: {exc}")
            return {
                "status": "error",
                "message": str(exc),
                "backend": {
                    "attempted": False,
                    "success": False,
                    "status_code": None,
                    "message": "Logout raised exception",
                },
            }

    def browser_login(
        self,
        catalog_id: Optional[str] = None,
        *,
        prompt_on_multiple: bool = True,
    ) -> Dict[str, str]:
        """Authenticate using browser-based OAuth flow with catalog selection.
        
        Opens the user's browser for OAuth authentication, handles catalog
        selection when multiple catalogs are available, and configures
        environment variables for successful authentication.
        """

        try:
            return execute_login(
                catalog_id,
                service_url=self.service_url,
                prompt_on_multiple=prompt_on_multiple,
                debug=self.debug,
                sdk=self._sdk,
            )
        except AuthenticationError as exc:
            print(f"Authentication failed: {exc}")
            return {}
        except Exception as exc:
            print(f"Unexpected error during browser login: {exc}")
            return {}

    def list_catalogs(self, formatted: bool = True) -> Optional[Dict[str, Any]]:
        """List all available catalogs for the authenticated user.
        
        Retrieves and returns information about all catalogs that the user
        has access to, including the currently selected catalog.
        
        Parameters
        ----------
        formatted : bool, optional
            If True, prints formatted output to console and returns None.
            If False, returns raw dictionary with catalog data.
            Default is True.
        
        Returns
        -------
        Optional[Dict[str, Any]]
            None when formatted=True.
            Dictionary containing available catalogs list and user info
            when formatted=False.
            
        Raises
        ------
        AuthenticationError
            If user is not logged in or catalog listing fails
        """
        try:
            from .commands.catalogs import execute_catalog_list
            result = execute_catalog_list(
                service_url=self.service_url,
                debug=self.debug,
                sdk=self._sdk,
            )
            
            if formatted:
                self._print_catalog_list(result)
                return None
            return result
        except AuthenticationError as exc:
            print(f"Failed to list catalogs: {exc}")
            return None if formatted else {}
        except Exception as exc:
            print(f"Unexpected error during catalog listing: {exc}")
            return None if formatted else {}
    
    def _print_catalog_list(self, result: Dict[str, Any]) -> None:
        """Print catalog list in a formatted way."""
        available_catalogs = result.get("available_catalogs", [])
        current_catalog = result.get("current_catalog")
        user_info = result.get("user_info", {})
        total_count = result.get("total_count", 0)
        
        print("Available Catalogs:")
        print("==================")
        
        if not available_catalogs:
            print("No catalogs available for this user.")
            return
            
        for i, catalog in enumerate(available_catalogs, 1):
            marker = " (current)" if catalog == current_catalog else ""
            print(f" {i}. {catalog}{marker}")
        
        print(f"\nTotal: {total_count} catalog{'s' if total_count != 1 else ''}")
        
        if current_catalog:
            print(f"Current catalog: {current_catalog}")
        else:
            print("No catalog currently selected")
            
        # Show user context if available
        if user_info.get("email"):
            print(f"User: {user_info['email']}")

    def switch_catalog(self, catalog_id: str) -> Dict[str, str]:
        """Switch to a different catalog and update environment variables.
        
        Switches the current catalog context while maintaining the existing
        authentication session. Updates environment variables with catalog-
        specific credentials for MLflow and storage access.
        
        Parameters
        ----------
        catalog_id : str
            The ID of the catalog to switch to
            
        Returns
        -------
        Dict[str, str]
            Sanitized credentials and environment information
            
        Raises
        ------
        AuthenticationError
            If user is not logged in or catalog switching fails
        ValueError
            If catalog_id is invalid or missing
        """
        try:
            from .commands.catalogs import execute_catalog_switch
            credentials = execute_catalog_switch(
                catalog_id,
                service_url=self.service_url,
                debug=self.debug,
                sdk=self._sdk,
            )
            print(f"\nSuccessfully switched to catalog: {catalog_id}")
            return credentials
        except ValueError as exc:
            print(f"Error: {exc}")
            return {}
        except AuthenticationError as exc:
            print(f"Catalog switch failed: {exc}")
            return {}
        except Exception as exc:
            print(f"Unexpected error during catalog switch: {exc}")
            return {}

    # External Providers
    def list_external_providers(
        self, limit: int = 50, page: int = 1, search: Optional[str] = None
    ) -> Dict[str, Any]:
        """List external model providers with pagination and search."""
        try:
            jwt = get_access_token()
            return self._sdk.external_providers.list_external_providers(
                jwt, limit=limit, page=page, search=search
            )
        except AuthenticationError:
            raise
        except Exception as exc:
            print(f"Error listing external providers: {exc}")
            return {}

    def create_external_provider(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new external provider configuration.
        
        Args:
            payload: Dictionary with keys:
                - name: Provider name (required)
                - type: Provider type (required)
                - url: Connection URL (optional)
                - description: Description (optional)
                - config: Dict with auth and connection settings (optional)
                - is_private: Boolean (optional, default True)
                - is_readonly: Boolean (optional, default False)
        
        The SDK will transform these to backend format:
        - name -> provider_name
        - type -> provider_type
        - config[token/password/api_key/etc] -> auth_credentials
        - config[other] -> connection_config
        """
        try:
            from .commands.external_providers import _get_auth_fields_for_provider
            jwt = get_access_token()
            
            # Transform payload to backend format
            backend_payload: Dict[str, Any] = {}
            if "name" in payload:
                backend_payload["provider_name"] = payload["name"]
            if "type" in payload:
                backend_payload["provider_type"] = payload["type"]
            if "url" in payload:
                backend_payload["url"] = payload["url"]
            if "description" in payload:
                backend_payload["description"] = payload["description"]
            
            # Handle visibility
            if "is_private" in payload:
                backend_payload["is_private"] = payload["is_private"]
            else:
                backend_payload["is_private"] = True  # Default to private

            if "is_readonly" in payload:
                backend_payload["is_readonly"] = payload["is_readonly"]
            
            # Split config into auth_credentials and connection_config based on provider type
            if "config" in payload:
                config = payload["config"]
                provider_type = payload.get("type", "")
                auth_fields = _get_auth_fields_for_provider(provider_type)
                auth_creds = {k: v for k, v in config.items() if k in auth_fields}
                conn_config = {k: v for k, v in config.items() if k not in auth_fields}
                
                if auth_creds:
                    backend_payload["auth_credentials"] = auth_creds
                if conn_config:
                    backend_payload["connection_config"] = conn_config
            
            return self._sdk.external_providers.create_external_provider(jwt, backend_payload)
        except AuthenticationError:
            raise
        except Exception as exc:
            print(f"Error creating external provider: {exc}")
            return {}

    def get_external_provider(self, provider_id: str) -> Dict[str, Any]:
        """Get details of a specific external provider by ID."""
        try:
            jwt = get_access_token()
            return self._sdk.external_providers.get_external_provider(jwt, provider_id)
        except AuthenticationError:
            raise
        except Exception as exc:
            print(f"Error getting external provider: {exc}")
            return {}

    def get_external_provider_by_name(self, provider_name: str) -> Dict[str, Any]:
        """Get details of a specific external provider by name."""
        try:
            jwt = get_access_token()
            return self._sdk.external_providers.get_external_provider_by_name(jwt, provider_name)
        except AuthenticationError:
            raise
        except Exception as exc:
            print(f"Error getting external provider by name: {exc}")
            return {}

    def update_external_provider(
        self, provider_id: str, payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update an existing external provider configuration.
        
        Args:
            provider_id: ID of the provider to update
            payload: Dictionary with keys to update:
                - name: Provider name (optional)
                - url: Connection URL (optional)
                - description: Description (optional)
                - config: Dict with auth and connection settings (optional)
                - is_private: Boolean (optional)
                - is_readonly: Boolean (optional)
        
        The SDK will transform these to backend format.
        """
        try:
            from .commands.external_providers import _get_auth_fields_for_provider
            jwt = get_access_token()
            
            # Transform payload to backend format
            backend_payload: Dict[str, Any] = {}
            if "name" in payload:
                backend_payload["provider_name"] = payload["name"]
            if "url" in payload:
                backend_payload["url"] = payload["url"]
            if "description" in payload:
                backend_payload["description"] = payload["description"]
            
            # Handle visibility
            if "is_private" in payload:
                backend_payload["is_private"] = payload["is_private"]

            if "is_readonly" in payload:
                backend_payload["is_readonly"] = payload["is_readonly"]
            
            # Split config into auth_credentials and connection_config based on provider type
            if "config" in payload:
                config = payload["config"]
                # Get provider to determine its type for correct field mapping
                existing = self._sdk.external_providers.get_external_provider_by_name(jwt, provider_id)
                provider_type = existing.get("provider_type", "")
                auth_fields = _get_auth_fields_for_provider(provider_type)
                auth_creds = {k: v for k, v in config.items() if k in auth_fields}
                conn_config = {k: v for k, v in config.items() if k not in auth_fields}
                
                if auth_creds:
                    backend_payload["auth_credentials"] = auth_creds
                if conn_config:
                    backend_payload["connection_config"] = conn_config
            
            return self._sdk.external_providers.update_external_provider(
                jwt, provider_id, backend_payload
            )
        except AuthenticationError:
            raise
        except Exception as exc:
            print(f"Error updating external provider: {exc}")
            return {}

    def delete_external_provider(self, provider_id: str) -> bool:
        """Delete an external provider configuration."""
        try:
            jwt = get_access_token()
            return self._sdk.external_providers.delete_external_provider(
                jwt, provider_id
            )
        except AuthenticationError:
            raise
        except Exception as exc:
            print(f"Error deleting external provider: {exc}")
            return False

    def test_provider_connection(
        self, provider_id: str, overrides: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Test connectivity to an external provider."""
        try:
            jwt = get_access_token()
            return self._sdk.external_providers.test_connection(
                jwt, provider_id, overrides
            )
        except AuthenticationError:
            raise
        except Exception as exc:
            print(f"Error testing provider connection: {exc}")
            return {}

    def browse_provider(
        self,
        provider_id: str,
        path: Optional[str] = None,
        search: Optional[str] = None,
        cursor: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Browse contents of an external provider."""
        try:
            jwt = get_access_token()
            return self._sdk.external_providers.browse_provider(
                jwt, provider_id, path, search, cursor
            )
        except AuthenticationError:
            raise
        except Exception as exc:
            print(f"Error browsing provider: {exc}")
            return {}

    # Import Jobs
    def import_model_from_external_provider(
        self, payload: Dict[str, Any], wait: bool = False
    ) -> Dict[str, Any]:
        """Import a model from an external provider to a catalog.
        
        Args:
            payload: Dictionary with keys:
                - provider_name: Name of the external provider (required)
                - model_identifier: Provider-specific model identifier (required)
                - catalog_id: Target catalog ID (optional, uses current catalog)
                - model_name: Name for the imported model (optional)
                - model_version: Version string (optional)
                - metadata: Additional metadata dict (optional)
            wait: If True, block until import completes
            
        Returns:
            Dict containing job details
        """
        try:
            jwt = get_access_token()
            
            # Build the backend payload
            backend_payload: Dict[str, Any] = {}
            
            # Resolve provider_name to provider_id
            provider_name = payload.get("provider_name")
            if provider_name:
                provider = self._sdk.external_providers.get_external_provider_by_name(jwt, provider_name)
                if not provider:
                    raise ValueError(f"No external provider found with name '{provider_name}'")
                backend_payload["provider_id"] = provider["id"]
            elif "provider_id" in payload:
                backend_payload["provider_id"] = payload["provider_id"]
            else:
                raise ValueError("Either provider_name or provider_id is required")
            
            # Required field
            if "model_identifier" in payload:
                backend_payload["model_identifier"] = payload["model_identifier"]
            else:
                raise ValueError("model_identifier is required")
            
            # Catalog ID - use current catalog if not specified
            if "catalog_id" in payload:
                backend_payload["catalog_id"] = payload["catalog_id"]
            else:
                catalog_id = os.environ.get("EDGEAI_CURRENT_CATALOG")
                if not catalog_id:
                    raise ValueError("No catalog specified and no current catalog in environment.")
                backend_payload["catalog_id"] = catalog_id
            
            # Build import_config with optional fields
            import_config: Dict[str, Any] = {}
            if "model_name" in payload:
                import_config["model_name"] = payload["model_name"]
            if "model_version" in payload:
                import_config["model_version"] = payload["model_version"]
            if "metadata" in payload:
                import_config["metadata"] = payload["metadata"]
            
            if import_config:
                backend_payload["import_config"] = import_config
            
            job = self._sdk.import_jobs.create_import_job(jwt, backend_payload)
            if not job:
                return {}
            
            if wait:
                job_id = job.get("job_id")
                if job_id:
                    print(f"Import job {job_id} created. Waiting for completion...")
                    job = self._sdk.import_jobs.wait_for_import_job(jwt, job_id)
                    print(f"Import job {job_id} completed with status: {job.get('status')}")
            
            return job
        except AuthenticationError:
            raise
        except Exception as exc:
            print(f"Error importing model: {exc}")
            return {}

    def list_import_jobs(
        self,
        limit: int = 20,
        page: int = 1,
        catalog_id: Optional[str] = None,
        status: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List import jobs with optional filtering."""
        try:
            jwt = get_access_token()
            return self._sdk.import_jobs.list_import_jobs(
                jwt, limit=limit, page=page, catalog_id=catalog_id, status=status
            )
        except AuthenticationError:
            raise
        except Exception as exc:
            print(f"Error listing import jobs: {exc}")
            return {}

    def get_import_job(self, job_id: str) -> Dict[str, Any]:
        """Get status and details of a specific import job."""
        try:
            jwt = get_access_token()
            return self._sdk.import_jobs.get_import_job(jwt, job_id)
        except AuthenticationError:
            raise
        except Exception as exc:
            print(f"Error getting import job: {exc}")
            return {}

    def cancel_import_job(self, job_id: str) -> Dict[str, Any]:
        """Cancel a pending or running import job."""
        try:
            jwt = get_access_token()
            return self._sdk.import_jobs.cancel_import_job(jwt, job_id)
        except AuthenticationError:
            raise
        except Exception as exc:
            print(f"Error cancelling import job: {exc}")
            return {}

    def retry_import_job(self, job_id: str) -> Dict[str, Any]:
        """Retry a failed import job."""
        try:
            jwt = get_access_token()
            return self._sdk.import_jobs.retry_import_job(jwt, job_id)
        except AuthenticationError:
            raise
        except Exception as exc:
            print(f"Error retrying import job: {exc}")
            return {}

    def delete_import_job(self, job_id: str) -> Dict[str, Any]:
        """Delete an import job record."""
        try:
            jwt = get_access_token()
            return self._sdk.import_jobs.delete_import_job(jwt, job_id)
        except AuthenticationError:
            raise
        except Exception as exc:
            print(f"Error deleting import job: {exc}")
            return {}

    def upload_model_from_local_files(
        self,
        model_name: str,
        file_paths: Any,
        *,
        provider_name: Optional[str] = None,
        provider_id: Optional[str] = None,
        catalog_id: Optional[str] = None,
        import_config: Optional[Dict[str, Any]] = None,
        wait: bool = False,
    ) -> Dict[str, Any]:
        """Upload model files from local filesystem and create import job.
        
        This is the recommended method for importing models from your local machine.
        Files are uploaded directly to the backend and processed by the import worker.
        Supports both individual files and directories (which are uploaded recursively).
        
        Args:
            model_name: Name for the imported model
            file_paths: Single path (str) or list of paths (files or directories)
            provider_name: Name of the local provider (recommended)
            provider_id: ID of the local provider (alternative to provider_name)
            catalog_id: Target catalog ID (defaults to current catalog from login)
            import_config: Optional config dict with model_version, metadata, etc.
            wait: If True, block until import completes
            
        Returns:
            Dict containing job details
            
        Example:
            >>> # Upload a single file (uses current catalog)
            >>> client.upload_model_from_local_files(
            ...     provider_name="my-local-provider",
            ...     model_name="my-model",
            ...     file_paths="/path/to/model.pt",
            ...     import_config={"model_version": "1.0"},
            ...     wait=True
            ... )
            >>> 
            >>> # Upload a directory (all files recursively)
            >>> client.upload_model_from_local_files(
            ...     provider_name="my-local-provider",
            ...     model_name="my-model",
            ...     file_paths="/path/to/model_directory",
            ...     wait=True
            ... )
        """
        try:
            jwt = get_access_token()
            
            # Resolve provider_name to provider_id
            resolved_provider_id = provider_id
            if provider_name:
                provider = self._sdk.external_providers.get_external_provider_by_name(jwt, provider_name)
                if not provider:
                    raise ValueError(f"No external provider found with name '{provider_name}'")
                resolved_provider_id = provider["id"]
            elif not provider_id:
                raise ValueError("Either provider_name or provider_id is required")
            
            # Use current catalog if not specified
            if not catalog_id:
                catalog_id = os.environ.get("EDGEAI_CURRENT_CATALOG")
                if not catalog_id:
                    raise ValueError("No catalog specified and no current catalog in environment. Please login first.")
            
            job = self._sdk.import_jobs.create_import_job_with_upload(
                jwt,
                provider_id=resolved_provider_id,
                catalog_id=catalog_id,
                model_name=model_name,
                file_paths=file_paths,
                import_config=import_config,
            )
            
            if not job:
                return {}
            
            if wait:
                job_id = job.get("job_id")
                if job_id:
                    print(f"Import job {job_id} created. Waiting for completion...")
                    job = self._sdk.import_jobs.wait_for_import_job(jwt, job_id)
                    print(f"Import job {job_id} completed with status: {job.get('status')}")
            
            return job
        except AuthenticationError:
            raise
        except Exception as exc:
            print(f"Error uploading model: {exc}")
            return {}

    # Benchmarking
    def run_benchmark(
        self,
        name: str,
        model_specs: List[Dict[str, Any]],
        device_types: List[str],
        *,
        description: Optional[str] = None,
        benchmark_type: str = "inference_speed",
        config: Optional[Dict[str, Any]] = None,
        wait: bool = False,
    ) -> Dict[str, Any]:
        """Run a new benchmark on target devices.
        
        Args:
            name: Name for the benchmark run
            model_specs: List of models to benchmark. Each dict should have:
                - catalog_id: str
                - model_name: str
                - versions: List[str]
            device_types: List of target device types (e.g., ["jetson_agx"])
            description: Optional description
            benchmark_type: Type of benchmark (inference_speed, stress, etc.)
            config: Optional benchmark configuration
            wait: If True, block until benchmark completes
        """
        try:
            from .services.benchmarks import BenchmarkConfig
            
            jwt = get_access_token()
            if not jwt:
                raise AuthenticationError("Not authenticated. Please log in first.")
            
            benchmark_config = None
            if config:
                benchmark_config = BenchmarkConfig(**config)
                
            run = self._sdk.benchmarks.create(
                backend_jwt=jwt,
                name=name,
                model_specs=model_specs,
                device_types=device_types,
                description=description,
                benchmark_type=benchmark_type,
                config=benchmark_config,
            )
            
            if wait:
                print(f"Benchmark {run.run_id} started. Waiting for completion...")
                run.wait_for_completion(jwt, verbose=True)
                
            return run._data
        except Exception as exc:
            print(f"Error running benchmark: {exc}")
            return {}

    def list_benchmarks(
        self, status: Optional[str] = None, limit: int = 20, page: int = 1
    ) -> Dict[str, Any]:
        """List benchmark runs with optional filtering."""
        try:
            jwt = get_access_token()
            if not jwt:
                raise AuthenticationError("Not authenticated. Please log in first.")
            return self._sdk.benchmarks.list(jwt, status=status, limit=limit, page=page)
        except Exception as exc:
            print(f"Error listing benchmarks{f' with status {status}' if status else ''}: {exc}")
            return {}

    def get_benchmark(self, run_id: str) -> Dict[str, Any]:
        """Get details and results of a specific benchmark run."""
        try:
            jwt = get_access_token()
            if not jwt:
                raise AuthenticationError("Not authenticated. Please log in first.")
            run = self._sdk.benchmarks.get(jwt, run_id)
            return run._data if run else {}
        except Exception as exc:
            print(f"Error getting benchmark {run_id}: {exc}")
            return {}

    def cancel_benchmark(self, run_id: str) -> bool:
        """Cancel a pending or running benchmark."""
        try:
            jwt = get_access_token()
            if not jwt:
                raise AuthenticationError("Not authenticated. Please log in first.")
            return self._sdk.benchmarks.cancel(jwt, run_id)
        except Exception as exc:
            print(f"Error cancelling benchmark {run_id}: {exc}")
            return False

    def delete_benchmark(self, run_id: str) -> bool:
        """Delete a benchmark run record."""
        try:
            jwt = get_access_token()
            if not jwt:
                raise AuthenticationError("Not authenticated. Please log in first.")
            return self._sdk.benchmarks.delete(jwt, run_id)
        except Exception as exc:
            print(f"Error deleting benchmark {run_id}: {exc}")
            return False

    # Device Pool
    def list_device_pool(self, limit: int = 20, page: int = 1) -> Dict[str, Any]:
        """List available device types in the benchmark pool."""
        try:
            jwt = get_access_token()
            if not jwt:
                raise AuthenticationError("Not authenticated. Please log in first.")
            return self._sdk.benchmarks.list_device_pool(jwt, limit=limit, page=page)
        except Exception as exc:
            print(f"Error listing device pool: {exc}")
            return {}

    def add_device_to_pool(
        self,
        device_type: str,
        cluster_names: List[str],
        helm_chart: str,
        description: Optional[str] = None,
        capabilities: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Add a new device type to the benchmark pool (Admin)."""
        try:
            jwt = get_access_token()
            if not jwt:
                raise AuthenticationError("Not authenticated. Please log in first.")
            return self._sdk.benchmarks.add_device_to_pool(
                jwt,
                device_type=device_type,
                cluster_names=cluster_names,
                helm_chart=helm_chart,
                description=description,
                capabilities=capabilities,
            )
        except Exception as exc:
            print(f"Error adding device to pool: {exc}")
            return {}

    def update_device_pool(
        self,
        device_type: str,
        cluster_names: Optional[List[str]] = None,
        helm_chart: Optional[str] = None,
        description: Optional[str] = None,
        capabilities: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Update an existing device pool entry (Admin)."""
        try:
            jwt = get_access_token()
            if not jwt:
                raise AuthenticationError("Not authenticated. Please log in first.")
            return self._sdk.benchmarks.update_device_pool(
                jwt,
                device_type=device_type,
                cluster_names=cluster_names,
                helm_chart=helm_chart,
                description=description,
                capabilities=capabilities,
            )
        except Exception as exc:
            print(f"Error updating device pool: {exc}")
            return {}

    def remove_device_from_pool(self, device_type: str) -> bool:
        """Remove a device type from the pool (Admin)."""
        try:
            jwt = get_access_token()
            if not jwt:
                raise AuthenticationError("Not authenticated. Please log in first.")
            return self._sdk.benchmarks.remove_device_from_pool(jwt, device_type)
        except Exception as exc:
            print(f"Error removing device from pool: {exc}")
            return False


# Module-level convenience functions

def login(
    catalog_id: Optional[str] = None,
    *,
    email: Optional[str] = None,
    password: Optional[str] = None,
    prompt_password: bool = False,
    service_url: Optional[str] = None,
    debug: bool = False,
) -> Dict[str, str]:
    """Convenience function for authentication without creating a client instance."""
    client = ZededaEdgeAIClient(service_url=service_url, debug=debug)
    return client.login(catalog_id, email=email, password=password,
                       prompt_password=prompt_password)


def list_catalogs(
    *,
    service_url: Optional[str] = None,
    debug: bool = False,
    formatted: bool = True,
) -> Optional[Dict[str, Any]]:
    """Convenience function for listing catalogs."""
    client = ZededaEdgeAIClient(service_url=service_url, debug=debug)
    return client.list_catalogs(formatted=formatted)


def switch_catalog(
    catalog_id: str,
    *,
    service_url: Optional[str] = None,
    debug: bool = False,
) -> Dict[str, str]:
    """Convenience function for catalog switching."""
    client = ZededaEdgeAIClient(service_url=service_url, debug=debug)
    return client.switch_catalog(catalog_id)


def logout(
    *,
    service_url: Optional[str] = None,
    debug: bool = False,
) -> Dict[str, Any]:
    """Convenience function for terminating the active session."""
    client = ZededaEdgeAIClient(service_url=service_url, debug=debug)
    return client.logout()


# External Provider convenience functions

def list_external_providers(
    *,
    limit: int = 50,
    page: int = 1,
    search: Optional[str] = None,
    service_url: Optional[str] = None,
    debug: bool = False,
) -> Dict[str, Any]:
    """List external model providers."""
    client = ZededaEdgeAIClient(service_url=service_url, debug=debug)
    return client.list_external_providers(limit=limit, page=page, search=search)


def create_external_provider(
    payload: Dict[str, Any],
    *,
    service_url: Optional[str] = None,
    debug: bool = False,
) -> Dict[str, Any]:
    """Create a new external provider configuration."""
    client = ZededaEdgeAIClient(service_url=service_url, debug=debug)
    return client.create_external_provider(payload)


def get_external_provider(
    provider_id: str,
    *,
    service_url: Optional[str] = None,
    debug: bool = False,
) -> Dict[str, Any]:
    """Get details of a specific external provider."""
    client = ZededaEdgeAIClient(service_url=service_url, debug=debug)
    return client.get_external_provider(provider_id)


def update_external_provider(
    provider_id: str,
    payload: Dict[str, Any],
    *,
    service_url: Optional[str] = None,
    debug: bool = False,
) -> Dict[str, Any]:
    """Update an existing external provider configuration."""
    client = ZededaEdgeAIClient(service_url=service_url, debug=debug)
    return client.update_external_provider(provider_id, payload)


def delete_external_provider(
    provider_id: str,
    *,
    service_url: Optional[str] = None,
    debug: bool = False,
) -> bool:
    """Delete an external provider configuration."""
    client = ZededaEdgeAIClient(service_url=service_url, debug=debug)
    return client.delete_external_provider(provider_id)


# Import Job convenience functions

def import_model_from_external_provider(
    payload: Dict[str, Any],
    wait: bool = False,
    *,
    service_url: Optional[str] = None,
    debug: bool = False,
) -> Dict[str, Any]:
    """Import a model from an external provider."""
    client = ZededaEdgeAIClient(service_url=service_url, debug=debug)
    return client.import_model_from_external_provider(payload, wait=wait)


def list_import_jobs(
    *,
    limit: int = 20,
    page: int = 1,
    catalog_id: Optional[str] = None,
    status: Optional[str] = None,
    service_url: Optional[str] = None,
    debug: bool = False,
) -> Dict[str, Any]:
    """List import jobs."""
    client = ZededaEdgeAIClient(service_url=service_url, debug=debug)
    return client.list_import_jobs(limit=limit, page=page, catalog_id=catalog_id, status=status)


# Benchmark convenience functions

def run_benchmark(
    name: str,
    model_specs: List[Dict[str, Any]],
    device_types: List[str],
    *,
    description: Optional[str] = None,
    benchmark_type: str = "inference_speed",
    config: Optional[Dict[str, Any]] = None,
    wait: bool = False,
    service_url: Optional[str] = None,
    debug: bool = False,
) -> Dict[str, Any]:
    """Run a new benchmark."""
    client = ZededaEdgeAIClient(service_url=service_url, debug=debug)
    return client.run_benchmark(
        name=name,
        model_specs=model_specs,
        device_types=device_types,
        description=description,
        benchmark_type=benchmark_type,
        config=config,
        wait=wait,
    )


def list_benchmarks(
    *,
    status: Optional[str] = None,
    limit: int = 20,
    page: int = 1,
    service_url: Optional[str] = None,
    debug: bool = False,
) -> Dict[str, Any]:
    """List benchmark runs."""
    client = ZededaEdgeAIClient(service_url=service_url, debug=debug)
    return client.list_benchmarks(status=status, limit=limit, page=page)


def get_benchmark(
    run_id: str,
    *,
    service_url: Optional[str] = None,
    debug: bool = False,
) -> Dict[str, Any]:
    """Get benchmark details."""
    client = ZededaEdgeAIClient(service_url=service_url, debug=debug)
    return client.get_benchmark(run_id)


# Device Pool convenience functions

def list_device_pool(
    *,
    limit: int = 20,
    page: int = 1,
    service_url: Optional[str] = None,
    debug: bool = False,
) -> Dict[str, Any]:
    """List device pool."""
    client = ZededaEdgeAIClient(service_url=service_url, debug=debug)
    return client.list_device_pool(limit=limit, page=page)


def add_device_to_pool(
    device_type: str,
    cluster_names: List[str],
    helm_chart: str,
    description: Optional[str] = None,
    capabilities: Optional[Dict[str, Any]] = None,
    *,
    service_url: Optional[str] = None,
    debug: bool = False,
) -> Dict[str, Any]:
    """Add a new device type to the benchmark pool (Admin)."""
    client = ZededaEdgeAIClient(service_url=service_url, debug=debug)
    return client.add_device_to_pool(
        device_type=device_type,
        cluster_names=cluster_names,
        helm_chart=helm_chart,
        description=description,
        capabilities=capabilities,
    )


def update_device_pool(
    device_type: str,
    cluster_names: Optional[List[str]] = None,
    helm_chart: Optional[str] = None,
    description: Optional[str] = None,
    capabilities: Optional[Dict[str, Any]] = None,
    *,
    service_url: Optional[str] = None,
    debug: bool = False,
) -> Dict[str, Any]:
    """Update an existing device pool entry (Admin)."""
    client = ZededaEdgeAIClient(service_url=service_url, debug=debug)
    return client.update_device_pool(
        device_type=device_type,
        cluster_names=cluster_names,
        helm_chart=helm_chart,
        description=description,
        capabilities=capabilities,
    )


def remove_device_from_pool(
    device_type: str,
    *,
    service_url: Optional[str] = None,
    debug: bool = False,
) -> bool:
    """Remove a device type from the pool (Admin)."""
    client = ZededaEdgeAIClient(service_url=service_url, debug=debug)
    return client.remove_device_from_pool(device_type)


def test_provider_connection(
    provider_id: str,
    overrides: Optional[Dict[str, Any]] = None,
    *,
    service_url: Optional[str] = None,
    debug: bool = False,
) -> Dict[str, Any]:
    """Test connectivity to an external provider."""
    client = ZededaEdgeAIClient(service_url=service_url, debug=debug)
    return client.test_provider_connection(provider_id, overrides)


def browse_provider(
    provider_id: str,
    path: Optional[str] = None,
    search: Optional[str] = None,
    cursor: Optional[str] = None,
    *,
    service_url: Optional[str] = None,
    debug: bool = False,
) -> Dict[str, Any]:
    """Browse contents of an external provider."""
    client = ZededaEdgeAIClient(service_url=service_url, debug=debug)
    return client.browse_provider(provider_id, path, search, cursor)


def get_import_job(
    job_id: str,
    *,
    service_url: Optional[str] = None,
    debug: bool = False,
) -> Dict[str, Any]:
    """Get status and details of a specific import job."""
    client = ZededaEdgeAIClient(service_url=service_url, debug=debug)
    return client.get_import_job(job_id)


def cancel_import_job(
    job_id: str,
    *,
    service_url: Optional[str] = None,
    debug: bool = False,
) -> Dict[str, Any]:
    """Cancel a pending or running import job."""
    client = ZededaEdgeAIClient(service_url=service_url, debug=debug)
    return client.cancel_import_job(job_id)


def retry_import_job(
    job_id: str,
    *,
    service_url: Optional[str] = None,
    debug: bool = False,
) -> Dict[str, Any]:
    """Retry a failed import job."""
    client = ZededaEdgeAIClient(service_url=service_url, debug=debug)
    return client.retry_import_job(job_id)


def delete_import_job(
    job_id: str,
    *,
    service_url: Optional[str] = None,
    debug: bool = False,
) -> Dict[str, Any]:
    """Delete an import job record."""
    client = ZededaEdgeAIClient(service_url=service_url, debug=debug)
    return client.delete_import_job(job_id)
