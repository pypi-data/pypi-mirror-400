"""CLI commands for import job management.

Provides command-line interface for creating and managing model
import jobs from external providers.
"""

from __future__ import annotations

import json
import os
import sys
from typing import Any, Dict, Optional

from . import CommandSpec, register_command
from ..config import get_service_url
from ..environment import require_auth
from ..utils.formatters import format_import_jobs, format_import_job
from ..zededa_edgeai_sdk import ZededaEdgeAISDK


@require_auth
def execute_import_job_create(
    *,
    provider_name: str,
    model_identifier: str,
    target_catalog_id: Optional[str] = None,
    model_name: Optional[str] = None,
    model_version: Optional[str] = None,
    metadata: Optional[str] = None,
    wait: bool = False,
    service_url: str,
    debug: bool = False,
    sdk: Optional[ZededaEdgeAISDK] = None,
    jwt: str,
) -> Dict[str, Any]:
    """Execute create import job command."""
    # Use current catalog from environment if not specified
    if not target_catalog_id:
        target_catalog_id = os.environ.get("EDGEAI_CURRENT_CATALOG")
        if not target_catalog_id:
            raise ValueError("No catalog specified and no current catalog in environment. Please login first.")

    if sdk is None:
        sdk = ZededaEdgeAISDK(service_url, debug=debug)

    # Fetch provider by name directly
    provider = sdk.external_providers.get_external_provider_by_name(jwt, provider_name)

    if not provider:
        raise ValueError(f"No external provider found with name '{provider_name}'")

    external_provider_id = provider["id"]

    payload: Dict[str, Any] = {
        "provider_id": external_provider_id,
        "catalog_id": target_catalog_id,
        "model_identifier": model_identifier,
    }
    
    # Build import_config with optional fields
    # The backend expects model_name, model_version, and metadata inside import_config
    import_config: Dict[str, Any] = {}
    if model_name:
        import_config["model_name"] = model_name
    if model_version:
        import_config["model_version"] = model_version
    if metadata:
        try:
            import_config["metadata"] = json.loads(metadata)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON in metadata: {exc}") from exc
    
    if import_config:
        payload["import_config"] = import_config

    job = sdk.import_jobs.create_import_job(jwt, payload)
    
    if wait and job:
        job_id = job.get("job_id")
        if job_id:
            print(f"Import job {job_id} created. Waiting for completion...")
            job = sdk.import_jobs.wait_for_import_job(jwt, job_id)
            status = job.get("status", "unknown")
            print(f"Import job {job_id} completed with status: {status}")
    
    return job


@require_auth
def execute_import_job_list(
    *,
    limit: int = 20,
    page: int = 1,
    catalog_id: Optional[str] = None,
    status: Optional[str] = None,
    service_url: str,
    debug: bool = False,
    sdk: Optional[ZededaEdgeAISDK] = None,
    jwt: str,
) -> Dict[str, Any]:
    """Execute list import jobs command."""
    if sdk is None:
        sdk = ZededaEdgeAISDK(service_url, debug=debug)

    return sdk.import_jobs.list_import_jobs(
        jwt, limit=limit, page=page, catalog_id=catalog_id, status=status
    )


@require_auth
def execute_import_job_get(
    job_id: str,
    *,
    service_url: str,
    debug: bool = False,
    sdk: Optional[ZededaEdgeAISDK] = None,
    jwt: str,
) -> Dict[str, Any]:
    """Execute get import job command."""
    if sdk is None:
        sdk = ZededaEdgeAISDK(service_url, debug=debug)

    return sdk.import_jobs.get_import_job(jwt, job_id)


@require_auth
def execute_import_job_cancel(
    job_id: str,
    *,
    service_url: str,
    debug: bool = False,
    sdk: Optional[ZededaEdgeAISDK] = None,
    jwt: str,
) -> Dict[str, Any]:
    """Execute cancel import job command."""
    if sdk is None:
        sdk = ZededaEdgeAISDK(service_url, debug=debug)

    return sdk.import_jobs.cancel_import_job(jwt, job_id)


@require_auth
def execute_import_job_retry(
    job_id: str,
    *,
    service_url: str,
    debug: bool = False,
    sdk: Optional[ZededaEdgeAISDK] = None,
    jwt: str,
) -> Dict[str, Any]:
    """Execute retry import job command."""
    if sdk is None:
        sdk = ZededaEdgeAISDK(service_url, debug=debug)

    return sdk.import_jobs.retry_import_job(jwt, job_id)


@require_auth
def execute_import_job_delete(
    job_id: str,
    *,
    service_url: str,
    debug: bool = False,
    sdk: Optional[ZededaEdgeAISDK] = None,
    jwt: str,
) -> Dict[str, Any]:
    """Execute delete import job command."""
    if sdk is None:
        sdk = ZededaEdgeAISDK(service_url, debug=debug)

    return sdk.import_jobs.delete_import_job(jwt, job_id)


@require_auth
def execute_import_job_upload(
    *,
    provider_name: str,
    catalog_id: Optional[str] = None,
    model_name: str,
    file_paths: list,
    model_version: Optional[str] = None,
    metadata: Optional[str] = None,
    wait: bool = False,
    service_url: str,
    debug: bool = False,
    sdk: Optional[ZededaEdgeAISDK] = None,
    jwt: str,
) -> Dict[str, Any]:
    """Execute import job with file upload command."""
    # Use current catalog from environment if not specified
    if not catalog_id:
        catalog_id = os.environ.get("EDGEAI_CURRENT_CATALOG")
        if not catalog_id:
            raise ValueError("No catalog specified and no current catalog in environment. Please login first.")

    if sdk is None:
        sdk = ZededaEdgeAISDK(service_url, debug=debug)

    # Fetch provider by name directly
    provider = sdk.external_providers.get_external_provider_by_name(jwt, provider_name)

    if not provider:
        raise ValueError(f"No provider found with name '{provider_name}'")

    provider_id = provider["id"]

    # Build import config
    import_config: Dict[str, Any] = {}
    if model_version:
        import_config["model_version"] = model_version
    if metadata:
        try:
            import_config["metadata"] = json.loads(metadata)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON in metadata: {exc}") from exc

    job = sdk.import_jobs.create_import_job_with_upload(
        jwt,
        provider_id=provider_id,
        catalog_id=catalog_id,
        model_name=model_name,
        file_paths=file_paths,
        import_config=import_config,
    )
    
    if wait and job:
        job_id = job.get("job_id")
        if job_id:
            print(f"Import job {job_id} created. Waiting for completion...")
            job = sdk.import_jobs.wait_for_import_job(jwt, job_id)
            status = job.get("status", "unknown")
            print(f"Import job {job_id} completed with status: {status}")
    
    return job


def _handle_import_job_create(args) -> None:
    """CLI handler for import-jobs create."""
    service_url = getattr(args, "service_url", None) or get_service_url()
    debug = getattr(args, "debug", False)
    wait = getattr(args, "wait", False)
    
    try:
        result = execute_import_job_create(
            provider_name=args.provider_name,
            model_identifier=args.model_identifier,
            target_catalog_id=getattr(args, 'target_catalog_id', None),
            model_name=args.model_name,
            model_version=args.model_version,
            metadata=args.metadata,
            wait=wait,
            service_url=service_url,
            debug=debug,
        )
        
        # If wait is True, the status messages are already printed by execute function
        # Just print the final result
        if wait:
            print(json.dumps(result, indent=2))
        else:
            # For async (no wait), show job created message and basic info
            job_id = result.get("job_id")
            status = result.get("status")
            print(f"Import job {job_id} created with status: {status}")
            print(f"Use 'zededa-edgeai import-jobs get {job_id}' to check status")
            
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def _handle_import_job_list(args) -> None:
    """CLI handler for import-jobs list."""
    service_url = getattr(args, "service_url", None) or get_service_url()
    debug = getattr(args, "debug", False)
    json_output = getattr(args, "json", False)
    try:
        result = execute_import_job_list(
            limit=args.limit,
            page=args.page,
            status=args.status,
            service_url=service_url,
            debug=debug,
        )
        output = format_import_jobs(result, json_output=json_output)
        print(output)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def _handle_import_job_get(args) -> None:
    """CLI handler for import-jobs get."""
    service_url = getattr(args, "service_url", None) or get_service_url()
    debug = getattr(args, "debug", False)
    json_output = getattr(args, "json", False)
    try:
        result = execute_import_job_get(
            job_id=args.job_id, service_url=service_url, debug=debug
        )
        if not result:
            print(f"Job {args.job_id} not found", file=sys.stderr)
            sys.exit(1)
        output = format_import_job(result, json_output=json_output)
        print(output)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def _handle_import_job_cancel(args) -> None:
    """CLI handler for import-jobs cancel."""
    service_url = getattr(args, "service_url", None) or get_service_url()
    debug = getattr(args, "debug", False)
    try:
        result = execute_import_job_cancel(
            args.job_id, service_url=service_url, debug=debug
        )
        print(json.dumps(result, indent=2))
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def _handle_import_job_retry(args) -> None:
    """CLI handler for import-jobs retry."""
    service_url = getattr(args, "service_url", None) or get_service_url()
    debug = getattr(args, "debug", False)
    try:
        result = execute_import_job_retry(
            args.job_id, service_url=service_url, debug=debug
        )
        print(json.dumps(result, indent=2))
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def _handle_import_job_delete(args) -> None:
    """CLI handler for import-jobs delete."""
    service_url = getattr(args, "service_url", None) or get_service_url()
    debug = getattr(args, "debug", False)
    try:
        result = execute_import_job_delete(
            args.job_id, service_url=service_url, debug=debug
        )
        print(json.dumps(result, indent=2))
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def _handle_import_job_upload(args) -> None:
    """CLI handler for import-jobs upload."""
    service_url = getattr(args, "service_url", None) or get_service_url()
    debug = getattr(args, "debug", False)
    wait = getattr(args, "wait", False)
    
    try:
        result = execute_import_job_upload(
            provider_name=args.provider_name,
            catalog_id=getattr(args, 'catalog_id', None),
            model_name=args.model_name,
            file_paths=args.files,
            model_version=args.model_version,
            metadata=args.metadata,
            wait=wait,
            service_url=service_url,
            debug=debug,
        )
        
        # If wait is True, the status messages are already printed by execute function
        # Just print the final result
        if wait:
            print(json.dumps(result, indent=2))
        else:
            # For async (no wait), show job created message and basic info
            job_id = result.get("job_id")
            status = result.get("status")
            print(f"Import job {job_id} created with status: {status}")
            print(f"Use 'zededa-edgeai import-jobs get {job_id}' to check status")
            
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def _setup_import_job_subcommands(subparsers) -> None:
    """Set up import-jobs subcommands."""
    # Upload (recommended for local files)
    upload_parser = subparsers.add_parser(
        "upload", 
        help="Upload local files and create import job (recommended)"
    )
    upload_parser.add_argument("--provider-name", required=True, help="Local provider name")
    upload_parser.add_argument("--catalog-id", help="Target catalog ID (defaults to current catalog)")
    upload_parser.add_argument("--model-name", required=True, help="Model name")
    upload_parser.add_argument("--files", nargs="+", required=True, help="File paths to upload")
    upload_parser.add_argument("--model-version", help="Model version")
    upload_parser.add_argument("--metadata", help="Model metadata (JSON)")
    upload_parser.add_argument("--wait", action="store_true", help="Wait for job completion")
    upload_parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    upload_parser.set_defaults(_command_handler=_handle_import_job_upload)

    # Create
    create_parser = subparsers.add_parser("create", help="Create import job")
    create_parser.add_argument("--provider-name", required=True, help="External provider name")
    create_parser.add_argument("--model-identifier", required=True, help="The model name in the external provider to import")
    create_parser.add_argument("--model-name", help="Model name")
    create_parser.add_argument("--model-version", help="Model version")
    create_parser.add_argument("--metadata", help="Model metadata (JSON)")
    create_parser.add_argument("--wait", action="store_true", help="Wait for job completion")
    create_parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    create_parser.set_defaults(_command_handler=_handle_import_job_create)

    # List
    list_parser = subparsers.add_parser("list", help="List import jobs")
    list_parser.add_argument("--limit", type=int, default=20, help="Results per page")
    list_parser.add_argument("--page", type=int, default=1, help="Page number")
    list_parser.add_argument("--catalog-id", help="Filter by catalog ID")
    list_parser.add_argument("--status", help="Filter by status")
    list_parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    list_parser.add_argument("--json", action="store_true", help="Output in JSON format")
    list_parser.set_defaults(_command_handler=_handle_import_job_list)

    # Get
    get_parser = subparsers.add_parser("get", help="Get import job details")
    get_parser.add_argument("job_id", help="Import job ID")
    get_parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    get_parser.add_argument("--json", action="store_true", help="Output in JSON format")
    get_parser.set_defaults(_command_handler=_handle_import_job_get)

    # Cancel
    cancel_parser = subparsers.add_parser("cancel", help="Cancel import job")
    cancel_parser.add_argument("job_id", help="Import job ID")
    cancel_parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    cancel_parser.set_defaults(_command_handler=_handle_import_job_cancel)

    # Retry
    retry_parser = subparsers.add_parser("retry", help="Retry failed import job")
    retry_parser.add_argument("job_id", help="Import job ID")
    retry_parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    retry_parser.set_defaults(_command_handler=_handle_import_job_retry)

    # Delete
    delete_parser = subparsers.add_parser("delete", help="Delete import job")
    delete_parser.add_argument("job_id", help="Import job ID")
    delete_parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    delete_parser.set_defaults(_command_handler=_handle_import_job_delete)


def register_import_job_commands() -> None:
    """Register import job command group."""
    command_spec = CommandSpec(
        name="import-jobs",
        help="Manage model import jobs",
        subcommand_setup=_setup_import_job_subcommands,
    )
    register_command(command_spec)
