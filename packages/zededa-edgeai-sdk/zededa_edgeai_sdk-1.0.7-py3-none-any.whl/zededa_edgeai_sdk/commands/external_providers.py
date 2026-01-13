"""CLI commands for external provider management.

Provides command-line interface for CRUD operations on external
model provider configurations.
"""

from __future__ import annotations

import json
import sys
from typing import Any, Dict, Optional

from . import CommandSpec, register_command
from ..config import get_service_url
from ..environment import require_auth
from ..utils.formatters import format_external_providers, format_external_provider
from ..zededa_edgeai_sdk import ZededaEdgeAISDK


@require_auth
def execute_external_provider_list(
    *,
    limit: int = 50,
    page: int = 1,
    search: Optional[str] = None,
    service_url: str,
    debug: bool = False,
    sdk: Optional[ZededaEdgeAISDK] = None,
    jwt: str,
) -> Dict[str, Any]:
    """Execute list external providers command."""
    if sdk is None:
        sdk = ZededaEdgeAISDK(service_url, debug=debug)

    result = sdk.external_providers.list_external_providers(
        jwt, limit=limit, page=page, search=search
    )
    return result


def _get_auth_fields_for_provider(provider_type: str) -> set:
    """Get the set of field names that should go in auth_credentials for each provider type.
    
    Based on what each backend connector expects in self.credentials vs self.connection_config.
    """
    auth_field_mappings = {
        # MLflow: uses credentials.get('username'), credentials.get('password'), credentials.get('token')
        "mlflow": {"username", "password", "token"},
        # Azure Blob: uses credentials.get('account_key')
        "blob": {"account_key"},
        # Azure ML: uses credentials.get('tenant_id'), credentials.get('client_id'), credentials.get('client_secret')
        "azure": {"tenant_id", "client_id", "client_secret"},
        # S3: uses credentials.get('access_key'), credentials.get('secret_key'), credentials.get('token')
        "s3": {"access_key", "secret_key", "token", "access_key_id", "secret_access_key", 
               "aws_access_key_id", "aws_secret_access_key", "session_token", "aws_session_token"},
        # SageMaker: same as S3
        "sagemaker": {"access_key", "secret_key", "token", "access_key_id", "secret_access_key",
                      "aws_access_key_id", "aws_secret_access_key", "session_token", "aws_session_token"},
        # HuggingFace: uses credentials.get('token')
        "huggingface": {"token"},
        # Local: no credentials needed
        "local": set(),
    }
    return auth_field_mappings.get(provider_type, set())


@require_auth
def execute_external_provider_create(
    name: str,
    provider_type: str,
    *,
    url: Optional[str] = None,
    config: Optional[str] = None,
    description: Optional[str] = None,
    is_private: bool = True,
    is_readonly: bool = False,
    service_url: str,
    debug: bool = False,
    sdk: Optional[ZededaEdgeAISDK] = None,
    jwt: str,
) -> Dict[str, Any]:
    """Execute create external provider command."""
    if sdk is None:
        sdk = ZededaEdgeAISDK(service_url, debug=debug)

    payload: Dict[str, Any] = {
        "provider_name": name,
        "provider_type": provider_type,
        "is_private": is_private,
        "is_readonly": is_readonly,
    }
    if url:
        payload["url"] = url
    if description:
        payload["description"] = description
    if config:
        try:
            config_dict = json.loads(config)
            # Split config into auth_credentials and connection_config based on provider type
            auth_fields = _get_auth_fields_for_provider(provider_type)
            auth_creds = {k: v for k, v in config_dict.items() if k in auth_fields}
            conn_config = {k: v for k, v in config_dict.items() if k not in auth_fields}
            
            if auth_creds:
                payload["auth_credentials"] = auth_creds
            if conn_config:
                payload["connection_config"] = conn_config
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON in config: {exc}") from exc

    return sdk.external_providers.create_external_provider(jwt, payload)


@require_auth
def execute_external_provider_get(
    provider_name: str,
    *,
    service_url: str,
    debug: bool = False,
    sdk: Optional[ZededaEdgeAISDK] = None,
    jwt: str,
) -> Dict[str, Any]:
    """Execute get external provider command by name."""
    if sdk is None:
        sdk = ZededaEdgeAISDK(service_url, debug=debug)

    return sdk.external_providers.get_external_provider_by_name(jwt, provider_name)


@require_auth
def execute_external_provider_update(
    provider_name: str,
    *,
    name: Optional[str] = None,
    url: Optional[str] = None,
    config: Optional[str] = None,
    description: Optional[str] = None,
    is_private: Optional[bool] = None,
    is_readonly: Optional[bool] = None,
    service_url: str,
    debug: bool = False,
    sdk: Optional[ZededaEdgeAISDK] = None,
    jwt: str,
) -> Dict[str, Any]:
    """Execute update external provider command by name."""
    if sdk is None:
        sdk = ZededaEdgeAISDK(service_url, debug=debug)

    payload: Dict[str, Any] = {}
    if name:
        payload["provider_name"] = name
    if url:
        payload["url"] = url
    if description:
        payload["description"] = description
    if is_private is not None:
        payload["is_private"] = is_private
    if is_readonly is not None:
        payload["is_readonly"] = is_readonly
    if config:
        try:
            config_dict = json.loads(config)
            # Get the existing provider to determine its type for correct field mapping
            existing = sdk.external_providers.get_external_provider_by_name(jwt, provider_name)
            provider_type = existing.get("provider_type", "")
            
            # Split config into auth_credentials and connection_config based on provider type
            auth_fields = _get_auth_fields_for_provider(provider_type)
            auth_creds = {k: v for k, v in config_dict.items() if k in auth_fields}
            conn_config = {k: v for k, v in config_dict.items() if k not in auth_fields}
            
            if auth_creds:
                payload["auth_credentials"] = auth_creds
            if conn_config:
                payload["connection_config"] = conn_config
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON in config: {exc}") from exc

    if not payload:
        raise ValueError("At least one field must be provided for update")

    return sdk.external_providers.update_external_provider(jwt, provider_name, payload)


@require_auth
def execute_external_provider_delete(
    provider_name: str,
    *,
    service_url: str,
    debug: bool = False,
    sdk: Optional[ZededaEdgeAISDK] = None,
    jwt: str,
) -> Dict[str, Any]:
    """Execute delete external provider command by name."""
    if sdk is None:
        sdk = ZededaEdgeAISDK(service_url, debug=debug)

    success = sdk.external_providers.delete_external_provider(jwt, provider_name)
    return {"success": success, "message": "Provider deleted" if success else "Provider not found"}


@require_auth
def execute_test_connection(
    provider_name: str,
    *,
    overrides: Optional[str] = None,
    service_url: str,
    debug: bool = False,
    sdk: Optional[ZededaEdgeAISDK] = None,
    jwt: str,
) -> Dict[str, Any]:
    """Execute test connection command by provider name."""
    if sdk is None:
        sdk = ZededaEdgeAISDK(service_url, debug=debug)

    override_dict = None
    if overrides:
        try:
            override_dict = json.loads(overrides)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON in overrides: {exc}") from exc

    return sdk.external_providers.test_connection(jwt, provider_name, override_dict)


@require_auth
def execute_browse_provider(
    provider_name: str,
    *,
    path: Optional[str] = None,
    search: Optional[str] = None,
    cursor: Optional[str] = None,
    service_url: str,
    debug: bool = False,
    sdk: Optional[ZededaEdgeAISDK] = None,
    jwt: str,
) -> Dict[str, Any]:
    """Execute browse provider command by provider name."""
    if sdk is None:
        sdk = ZededaEdgeAISDK(service_url, debug=debug)

    return sdk.external_providers.browse_provider(jwt, provider_name, path, search, cursor)


def _list_external_providers_handler(args):
    """CLI handler for external-providers list."""
    service_url = getattr(args, "service_url", None) or get_service_url()
    debug = getattr(args, "debug", False)
    json_output = getattr(args, "json", False)
    try:
        result = execute_external_provider_list(
            limit=args.limit,
            page=args.page,
            search=args.search,
            service_url=service_url,
            debug=debug,
        )
        output = format_external_providers(result, json_output=json_output)
        print(output)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def _handle_external_provider_create(args) -> None:
    """CLI handler for external-providers create."""
    service_url = getattr(args, "service_url", None) or get_service_url()
    debug = getattr(args, "debug", False)
    try:
        result = execute_external_provider_create(
            args.name,
            args.type,
            url=args.url,
            config=args.config,
            description=args.description,
            is_private=not args.public,  # CLI uses --public flag, defaulting to private
            is_readonly=args.readonly,
            service_url=service_url,
            debug=debug,
        )
        print(json.dumps(result, indent=2))
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def _handle_external_provider_get(args) -> None:
    """CLI handler for external-providers get."""
    service_url = getattr(args, "service_url", None) or get_service_url()
    debug = getattr(args, "debug", False)
    json_output = getattr(args, "json", False)
    try:
        result = execute_external_provider_get(
            args.provider_name, service_url=service_url, debug=debug
        )
        if not result:
            print(f"Provider '{args.provider_name}' not found", file=sys.stderr)
            sys.exit(1)
        output = format_external_provider(result, json_output=json_output)
        print(output)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def _handle_external_provider_update(args) -> None:
    """CLI handler for external-providers update."""
    service_url = getattr(args, "service_url", None) or get_service_url()
    debug = getattr(args, "debug", False)
    
    # Determine is_private based on flags
    is_private = None
    if args.public is not None:
        is_private = not args.public
        
    try:
        result = execute_external_provider_update(
            args.provider_name,
            name=args.name,
            url=args.url,
            config=args.config,
            description=args.description,
            is_private=is_private,
            is_readonly=args.readonly,
            service_url=service_url,
            debug=debug,
        )
        print(json.dumps(result, indent=2))
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def _handle_external_provider_delete(args) -> None:
    """CLI handler for external-providers delete."""
    service_url = getattr(args, "service_url", None) or get_service_url()
    debug = getattr(args, "debug", False)
    try:
        result = execute_external_provider_delete(
            args.provider_name, service_url=service_url, debug=debug
        )
        print(json.dumps(result, indent=2))
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def _handle_test_connection(args) -> None:
    """CLI handler for external-providers test-connection."""
    service_url = getattr(args, "service_url", None) or get_service_url()
    debug = getattr(args, "debug", False)
    try:
        result = execute_test_connection(
            args.provider_name,
            overrides=args.overrides,
            service_url=service_url,
            debug=debug,
        )
        print(json.dumps(result, indent=2))
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def _handle_browse_provider(args) -> None:
    """CLI handler for external-providers browse."""
    service_url = getattr(args, "service_url", None) or get_service_url()
    debug = getattr(args, "debug", False)
    try:
        result = execute_browse_provider(
            args.provider_name,
            path=args.path,
            search=args.search,
            service_url=service_url,
            debug=debug,
        )
        print(json.dumps(result, indent=2))
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def _setup_external_provider_subcommands(subparsers) -> None:
    """Set up external-providers subcommands."""
    # List
    list_parser = subparsers.add_parser("list", help="List external providers")
    list_parser.add_argument("--limit", type=int, default=50, help="Results per page")
    list_parser.add_argument("--page", type=int, default=1, help="Page number")
    list_parser.add_argument("--search", type=str, help="Search term")
    list_parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    list_parser.add_argument("--json", action="store_true", help="Output in JSON format")
    list_parser.set_defaults(_command_handler=_list_external_providers_handler)

    # Create
    create_parser = subparsers.add_parser("create", help="Create external provider")
    create_parser.add_argument("--name", required=True, help="Provider name")
    create_parser.add_argument("--type", required=True, help="Provider type")
    create_parser.add_argument("--url", help="Provider URL")
    create_parser.add_argument("--config", help="Provider config (JSON)")
    create_parser.add_argument("--description", help="Provider description")
    create_parser.add_argument("--public", action="store_true", help="Make provider public (default: private)")
    create_parser.add_argument("--readonly", action="store_true", help="Make provider read-only")
    create_parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    create_parser.set_defaults(_command_handler=_handle_external_provider_create)

    # Get
    get_parser = subparsers.add_parser("get", help="Get external provider details")
    get_parser.add_argument("provider_name", help="Provider name (unique name)")
    get_parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    get_parser.add_argument("--json", action="store_true", help="Output in JSON format")
    get_parser.set_defaults(_command_handler=_handle_external_provider_get)

    # Update
    update_parser = subparsers.add_parser("update", help="Update external provider")
    update_parser.add_argument("provider_name", help="Provider name (unique name)")
    update_parser.add_argument("--name", help="New provider name")
    update_parser.add_argument("--url", help="New provider URL")
    update_parser.add_argument("--config", help="New provider config (JSON)")
    update_parser.add_argument("--description", help="New provider description")
    update_parser.add_argument("--public", action="store_true", default=None, help="Set provider public")
    update_parser.add_argument("--private", action="store_false", dest="public", help="Set provider private")
    update_parser.add_argument("--readonly", action="store_true", default=None, help="Set provider read-only")
    update_parser.add_argument("--read-write", action="store_false", dest="readonly", help="Set provider read-write")
    update_parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    update_parser.set_defaults(_command_handler=_handle_external_provider_update)

    # Delete
    delete_parser = subparsers.add_parser("delete", help="Delete external provider")
    delete_parser.add_argument("provider_name", help="Provider name (unique name)")
    delete_parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    delete_parser.set_defaults(_command_handler=_handle_external_provider_delete)

    # Test connection
    test_parser = subparsers.add_parser("test-connection", help="Test provider connection")
    test_parser.add_argument("provider_name", help="Provider name (unique name)")
    test_parser.add_argument("--overrides", help="Config overrides (JSON)")
    test_parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    test_parser.set_defaults(_command_handler=_handle_test_connection)

    # Browse
    browse_parser = subparsers.add_parser("browse", help="Browse provider contents")
    browse_parser.add_argument("provider_name", help="Provider name (unique name)")
    browse_parser.add_argument("--path", help="Path to browse")
    browse_parser.add_argument("--search", help="Search term")
    browse_parser.add_argument("--cursor", help="Pagination cursor")
    browse_parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    browse_parser.set_defaults(_command_handler=_handle_browse_provider)


def register_external_provider_commands() -> None:
    """Register external provider command group."""
    command_spec = CommandSpec(
        name="external-providers",
        help="Manage external model providers",
        subcommand_setup=_setup_external_provider_subcommands,
    )
    register_command(command_spec)
