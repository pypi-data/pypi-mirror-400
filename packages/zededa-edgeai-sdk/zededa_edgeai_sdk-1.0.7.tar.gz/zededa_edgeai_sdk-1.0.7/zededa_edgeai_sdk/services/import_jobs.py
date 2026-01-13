"""Import job management service for model import operations.

Provides functionality to create, monitor, and manage model import jobs
from external providers.
"""

from __future__ import annotations

import json
import os
import time
from typing import Any, Dict, List, Optional, Union

import requests

from .http import HTTPService

__all__ = ["ImportJobService"]


class ImportJobService:
    """Service for managing model import job operations.
    
    Handles creation, retrieval, listing, cancellation, retry, and deletion
    of import jobs that transfer models from external providers to catalogs.
    """

    def __init__(self, backend_url: str, http: HTTPService) -> None:
        """Initialize import job service with backend URL and HTTP client.
        
        Sets up the service to communicate with import job management
        endpoints using the provided HTTP service for consistent request
        handling and debug logging.
        """
        self.backend_url = backend_url.rstrip("/")
        self.http = http

    def create_import_job(
        self, backend_jwt: str, payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a new model import job.
        
        Initiates an import job to copy a model from an external provider
        to a target catalog. Returns job details with tracking ID.
        """
        url = f"{self.backend_url}/api/v1/import-jobs/models/import"
        headers = {
            "Authorization": f"Bearer {backend_jwt}",
            "Content-Type": "application/json",
        }

        try:
            response = self.http.request("POST", url, headers=headers, json=payload)
        except requests.RequestException as exc:
            raise ValueError(f"Failed to create import job: {exc}") from exc

        if response.status_code not in (200, 202):
            error_text = response.text
            raise ValueError(
                f"Failed to create import job: {response.status_code} {error_text}"
            )

        try:
            return response.json()
        except ValueError as exc:
            raise ValueError("Invalid JSON response from create import job") from exc

    def get_import_job(self, backend_jwt: str, job_id: str) -> Dict[str, Any]:
        """Retrieve status and details of a specific import job.
        
        Fetches current status, progress, and result information for
        the specified job ID. Returns empty dict if job not found or on error.
        """
        url = f"{self.backend_url}/api/v1/import-jobs/{job_id}"
        headers = {"Authorization": f"Bearer {backend_jwt}"}

        try:
            response = self.http.request("GET", url, headers=headers)
        except requests.RequestException as exc:
            print(f"[ERROR] Unable to get import job: {exc}")
            return {}

        if response.status_code == 404:
            return {}
        
        if response.status_code != 200:
            print(f"[ERROR] Failed to get import job: {response.status_code} {response.text}")
            return {}

        try:
            return response.json() or {}
        except ValueError:
            print("[ERROR] Invalid JSON response from get import job")
            return {}

    def list_import_jobs(
        self,
        backend_jwt: str,
        *,
        limit: int = 20,
        page: int = 1,
        catalog_id: Optional[str] = None,
        status: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List import jobs with optional filtering.
        
        Retrieves a paginated list of import jobs, optionally filtered
        by catalog or status.
        """
        url = f"{self.backend_url}/api/v1/import-jobs"
        headers = {"Authorization": f"Bearer {backend_jwt}"}
        params: Dict[str, Any] = {"limit": limit, "page": page}
        if catalog_id:
            params["catalog_id"] = catalog_id
        if status:
            params["status"] = status

        try:
            response = self.http.request("GET", url, headers=headers, params=params)
        except requests.RequestException as exc:
            print(f"[ERROR] Unable to list import jobs: {exc}")
            return {}

        if response.status_code != 200:
            print(
                f"[ERROR] Failed to list import jobs: {response.status_code} {response.text}"
            )
            return {}

        try:
            return response.json() or {}
        except ValueError:
            print("[ERROR] Invalid JSON response from list import jobs")
            return {}

    def cancel_import_job(self, backend_jwt: str, job_id: str) -> Dict[str, Any]:
        """Cancel a pending or running import job.
        
        Requests cancellation of the specified job. Job will transition
        to cancelled state if possible.
        """
        url = f"{self.backend_url}/api/v1/import-jobs/{job_id}/cancel"
        headers = {
            "Authorization": f"Bearer {backend_jwt}",
            "Content-Type": "application/json",
        }

        try:
            response = self.http.request("POST", url, headers=headers, json={})
        except requests.RequestException as exc:
            raise ValueError(f"Failed to cancel import job: {exc}") from exc

        if response.status_code != 200:
            error_text = response.text
            raise ValueError(
                f"Failed to cancel import job: {response.status_code} {error_text}"
            )

        try:
            return response.json()
        except ValueError as exc:
            raise ValueError("Invalid JSON response from cancel import job") from exc

    def retry_import_job(self, backend_jwt: str, job_id: str) -> Dict[str, Any]:
        """Retry a failed import job.
        
        Requeues a failed job for another attempt. Job must be in
        failed state and within retry limits.
        """
        url = f"{self.backend_url}/api/v1/import-jobs/{job_id}/retry"
        headers = {
            "Authorization": f"Bearer {backend_jwt}",
            "Content-Type": "application/json",
        }

        try:
            response = self.http.request("POST", url, headers=headers, json={})
        except requests.RequestException as exc:
            raise ValueError(f"Failed to retry import job: {exc}") from exc

        if response.status_code not in (200, 202):
            error_text = response.text
            raise ValueError(
                f"Failed to retry import job: {response.status_code} {error_text}"
            )

        try:
            return response.json()
        except ValueError as exc:
            raise ValueError("Invalid JSON response from retry import job") from exc

    def delete_import_job(self, backend_jwt: str, job_id: str) -> Dict[str, Any]:
        """Delete an import job record.
        
        Removes the job from the system. Cannot delete running jobs;
        cancel them first.
        """
        url = f"{self.backend_url}/api/v1/import-jobs/{job_id}"
        headers = {"Authorization": f"Bearer {backend_jwt}"}

        try:
            response = self.http.request("DELETE", url, headers=headers)
        except requests.RequestException as exc:
            raise ValueError(f"Failed to delete import job: {exc}") from exc

        if response.status_code == 200:
            try:
                return response.json()
            except ValueError:
                return {"message": "Import job deleted successfully"}
        
        error_text = response.text
        raise ValueError(
            f"Failed to delete import job: {response.status_code} {error_text}"
        )

    def wait_for_import_job(
        self,
        backend_jwt: str,
        job_id: str,
        *,
        poll_interval: float = 5.0,
        timeout: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Wait for an import job to complete.
        
        Polls the job status until it reaches a terminal state (completed,
        failed, or cancelled) or timeout is reached.
        """
        start_time = time.time()
        
        while True:
            job = self.get_import_job(backend_jwt, job_id)
            if not job:
                raise ValueError(f"Import job {job_id} not found")
            
            status = job.get("status", "").lower()
            if status in ("completed", "failed", "cancelled"):
                return job
            
            if timeout and (time.time() - start_time) >= timeout:
                raise TimeoutError(
                    f"Import job {job_id} did not complete within {timeout} seconds"
                )
            
            time.sleep(poll_interval)

    def create_import_job_with_upload(
        self,
        backend_jwt: str,
        *,
        provider_id: str,
        catalog_id: str,
        model_name: str,
        file_paths: Union[str, List[str]],
        import_config: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Create an import job with file upload from local filesystem.
        
        Uploads files from the local machine and creates an import job.
        This is the recommended method for importing models from your
        local filesystem. Supports both files and directories (recursively).
        File structure is preserved when uploading directories.
        
        Args:
            backend_jwt: Authentication token
            provider_id: ID of the local provider
            catalog_id: Target catalog ID
            model_name: Name for the imported model
            file_paths: Single path or list of paths (files or directories) to upload
            import_config: Optional configuration dict with metadata
            
        Returns:
            Dict containing job_id and status
            
        Raises:
            ValueError: If paths don't exist or upload fails
        """
        url = f"{self.backend_url}/api/v1/import-jobs/models/import-with-upload"
        headers = {"Authorization": f"Bearer {backend_jwt}"}
        
        # Normalize file paths to list
        if isinstance(file_paths, str):
            file_paths = [file_paths]
        
        # Collect all files (expand directories recursively)
        # Store tuples of (absolute_path, relative_name) to preserve directory structure
        all_files = []
        for path_item in file_paths:
            if not os.path.exists(path_item):
                raise ValueError(f"Path does not exist: {path_item}")
            
            if os.path.isfile(path_item):
                # For individual files, just use the basename
                all_files.append((path_item, os.path.basename(path_item)))
            elif os.path.isdir(path_item):
                # Recursively find all files in directory, preserving structure
                base_dir = path_item.rstrip(os.sep)
                for root, dirs, files in os.walk(path_item):
                    for file_name in files:
                        file_path = os.path.join(root, file_name)
                        # Calculate relative path from base directory to preserve structure
                        relative_path = os.path.relpath(file_path, base_dir)
                        all_files.append((file_path, relative_path))
            else:
                raise ValueError(f"Path is neither a file nor directory: {path_item}")
        
        if not all_files:
            raise ValueError("No files found to upload")
        
        # Prepare form data
        data = {
            "provider_id": provider_id,
            "catalog_id": catalog_id,
            "model_name": model_name,
            "import_config": json.dumps(import_config or {}),
        }
        
        # Make the upload request directly with requests (not via HTTPService)
        # HTTPService doesn't support multipart/form-data uploads
        if self.http.debug:
            print(f"[DEBUG] POST {url}")
            print(f"[DEBUG] Uploading {len(all_files)} file(s)")
            for abs_path, rel_name in all_files:
                print(f"[DEBUG]   {rel_name} <- {abs_path}")
            print(f"[DEBUG] Form data: provider_id={provider_id}, catalog_id={catalog_id}, model_name={model_name}")
        
        # Use context managers for file handles to ensure proper cleanup
        # Build a list of (field_name, (file_name, file_object, content_type)) tuples
        # all_files already contains tuples of (absolute_path, relative_name)
        files_to_upload = all_files
        
        # Open all files using nested context managers
        from contextlib import ExitStack
        
        with ExitStack() as stack:
            files = []
            for file_path, file_name in files_to_upload:
                file_handle = stack.enter_context(open(file_path, "rb"))
                files.append(("files", (file_name, file_handle, "application/octet-stream")))
            
            try:
                response = requests.post(
                    url,
                    headers=headers,
                    data=data,
                    files=files,
                    timeout=300,  # 5 minute timeout for large uploads
                )
            except requests.RequestException as exc:
                raise ValueError(f"Failed to upload files and create import job: {exc}") from exc
            
            if self.http.debug:
                print(f"[DEBUG] Response: {response.status_code}")
            
            if response.status_code not in (200, 202):
                error_text = response.text
                raise ValueError(
                    f"Failed to create import job with upload: {response.status_code} {error_text}"
                )
            
            try:
                return response.json()
            except ValueError as exc:
                raise ValueError("Invalid JSON response from import with upload") from exc
