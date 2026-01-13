"""CLI commands for benchmarking and device pool management.

Provides command-line interface for running benchmarks and managing
device pools for model evaluation.
"""

from __future__ import annotations

import json
import sys
from typing import Any, Dict, List, Optional

import requests

from . import CommandSpec, register_command
from ..config import get_service_url
from ..environment import require_auth
from ..utils.formatters import format_benchmarks, format_benchmark_run, format_device_pool
from ..zededa_edgeai_sdk import ZededaEdgeAISDK


@require_auth
def execute_benchmark_run(
    *,
    name: str,
    model_specs_json: str,
    device_types: List[str],
    description: Optional[str] = None,
    benchmark_type: str = "inference_speed",
    wait: bool = False,
    service_url: str,
    debug: bool = False,
    sdk: Optional[ZededaEdgeAISDK] = None,
    jwt: str,
) -> Dict[str, Any]:
    """Execute run benchmark command."""
    if sdk is None:
        sdk = ZededaEdgeAISDK(service_url, debug=debug)

    try:
        model_specs = json.loads(model_specs_json)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in model-specs: {exc}") from exc

    run = sdk.benchmarks.create(
        backend_jwt=jwt,
        name=name,
        model_specs=model_specs,
        device_types=device_types,
        description=description,
        benchmark_type=benchmark_type,
    )

    if wait:
        print(f"Benchmark {run.run_id} started. Waiting for completion...")
        run.wait_for_completion(backend_jwt=jwt, verbose=True)
    
    return run._data


@require_auth
def execute_benchmark_list(
    *,
    status: Optional[str] = None,
    limit: int = 20,
    page: int = 1,
    service_url: str,
    debug: bool = False,
    sdk: Optional[ZededaEdgeAISDK] = None,
    jwt: str,
) -> Dict[str, Any]:
    """Execute list benchmarks command."""
    if sdk is None:
        sdk = ZededaEdgeAISDK(service_url, debug=debug)

    return sdk.benchmarks.list(backend_jwt=jwt, status=status, limit=limit, page=page)


@require_auth
def execute_benchmark_get(
    run_id: str,
    *,
    service_url: str,
    debug: bool = False,
    sdk: Optional[ZededaEdgeAISDK] = None,
    jwt: str,
) -> Dict[str, Any]:
    """Execute get benchmark command."""
    if sdk is None:
        sdk = ZededaEdgeAISDK(service_url, debug=debug)

    run = sdk.benchmarks.get(jwt, run_id)
    if not run:
        raise ValueError(f"Benchmark {run_id} not found")
    return run._data


@require_auth
def execute_benchmark_cancel(
    run_id: str,
    *,
    service_url: str,
    debug: bool = False,
    sdk: Optional[ZededaEdgeAISDK] = None,
    jwt: str,
) -> Dict[str, Any]:
    """Execute cancel benchmark command."""
    if sdk is None:
        sdk = ZededaEdgeAISDK(service_url, debug=debug)

    success = sdk.benchmarks.cancel(jwt, run_id)
    return {"status": "success" if success else "failed", "run_id": run_id}


@require_auth
def execute_benchmark_delete(
    run_id: str,
    *,
    service_url: str,
    debug: bool = False,
    sdk: Optional[ZededaEdgeAISDK] = None,
    jwt: str,
) -> Dict[str, Any]:
    """Execute delete benchmark command."""
    if sdk is None:
        sdk = ZededaEdgeAISDK(service_url, debug=debug)

    success = sdk.benchmarks.delete(jwt, run_id)
    return {"status": "success" if success else "failed", "run_id": run_id}


@require_auth
def execute_device_pool_list(
    *,
    limit: int = 20,
    page: int = 1,
    service_url: str,
    debug: bool = False,
    sdk: Optional[ZededaEdgeAISDK] = None,
    jwt: str,
) -> Dict[str, Any]:
    """Execute list device pool command."""
    if sdk is None:
        sdk = ZededaEdgeAISDK(service_url, debug=debug)

    return sdk.benchmarks.list_device_pool(backend_jwt=jwt, limit=limit, page=page)


@require_auth
def execute_device_pool_add(
    *,
    device_type: str,
    cluster_names: List[str],
    helm_chart: str,
    description: Optional[str] = None,
    capabilities_json: Optional[str] = None,
    service_url: str,
    debug: bool = False,
    sdk: Optional[ZededaEdgeAISDK] = None,
    jwt: str,
) -> Dict[str, Any]:
    """Execute add device to pool command."""
    if sdk is None:
        sdk = ZededaEdgeAISDK(service_url, debug=debug)

    capabilities = None
    if capabilities_json:
        try:
            capabilities = json.loads(capabilities_json)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON in capabilities: {exc}") from exc

    return sdk.benchmarks.add_device_to_pool(
        backend_jwt=jwt,
        device_type=device_type,
        cluster_names=cluster_names,
        helm_chart=helm_chart,
        description=description,
        capabilities=capabilities,
    )


@require_auth
def execute_device_pool_update(
    device_type: str,
    *,
    cluster_names: Optional[List[str]] = None,
    helm_chart: Optional[str] = None,
    description: Optional[str] = None,
    capabilities_json: Optional[str] = None,
    service_url: str,
    debug: bool = False,
    sdk: Optional[ZededaEdgeAISDK] = None,
    jwt: str,
) -> Dict[str, Any]:
    """Execute update device pool command."""
    if sdk is None:
        sdk = ZededaEdgeAISDK(service_url, debug=debug)

    capabilities = None
    if capabilities_json:
        try:
            capabilities = json.loads(capabilities_json)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON in capabilities: {exc}") from exc

    return sdk.benchmarks.update_device_pool(
        backend_jwt=jwt,
        device_type=device_type,
        cluster_names=cluster_names,
        helm_chart=helm_chart,
        description=description,
        capabilities=capabilities,
    )


@require_auth
def execute_device_pool_remove(
    device_type: str,
    *,
    service_url: str,
    debug: bool = False,
    sdk: Optional[ZededaEdgeAISDK] = None,
    jwt: str,
) -> Dict[str, Any]:
    """Execute remove device from pool command."""
    if sdk is None:
        sdk = ZededaEdgeAISDK(service_url, debug=debug)

    success = sdk.benchmarks.remove_device_from_pool(jwt, device_type)
    return {"status": "success" if success else "failed", "device_type": device_type}


def _handle_api_error(exc: Exception) -> None:
    """Handle API errors by printing detailed messages."""
    if isinstance(exc, requests.exceptions.HTTPError):
        try:
            error_detail = exc.response.json()
            if "detail" in error_detail:
                detail = error_detail["detail"]
                if isinstance(detail, list):
                    for err in detail:
                        msg = err.get("msg", "Unknown error")
                        loc = " -> ".join(str(l) for l in err.get("loc", []))
                        # Filter out 'body' from location if it's the first element
                        if loc.startswith("body -> "):
                            loc = loc[8:]
                        print(f"Error: {msg} (Location: {loc})", file=sys.stderr)
                else:
                    print(f"Error: {detail}", file=sys.stderr)
                return
        except Exception as parse_exc:
            # Failed to parse structured error details; fall back to generic message.
            print(
                f"Warning: unable to parse error details from response: {parse_exc}",
                file=sys.stderr,
            )
    print(f"Error: {exc}", file=sys.stderr)


# CLI Handlers

def _handle_benchmark_run(args) -> None:
    service_url = getattr(args, "service_url", None) or get_service_url()
    debug = getattr(args, "debug", False)
    wait = getattr(args, "wait", False)
    
    try:
        result = execute_benchmark_run(
            name=args.name,
            model_specs_json=args.model_specs,
            device_types=args.device_types,
            description=getattr(args, "description", None),
            benchmark_type=getattr(args, "benchmark_type", "inference_speed"),
            wait=wait,
            service_url=service_url,
            debug=debug,
        )
        print(json.dumps(result, indent=2))
    except Exception as exc:
        _handle_api_error(exc)
        sys.exit(1)


def _handle_benchmark_list(args) -> None:
    service_url = getattr(args, "service_url", None) or get_service_url()
    debug = getattr(args, "debug", False)
    json_output = getattr(args, "json", False)
    try:
        result = execute_benchmark_list(
            status=args.status,
            limit=args.limit,
            page=args.page,
            service_url=service_url,
            debug=debug,
        )
        print(format_benchmarks(result, json_output=json_output))
    except Exception as exc:
        _handle_api_error(exc)
        sys.exit(1)


def _handle_benchmark_get(args) -> None:
    service_url = getattr(args, "service_url", None) or get_service_url()
    debug = getattr(args, "debug", False)
    json_output = getattr(args, "json", False)
    try:
        result = execute_benchmark_get(
            run_id=args.run_id, service_url=service_url, debug=debug
        )
        print(format_benchmark_run(result, json_output=json_output))
    except Exception as exc:
        _handle_api_error(exc)
        sys.exit(1)


def _handle_benchmark_cancel(args) -> None:
    service_url = getattr(args, "service_url", None) or get_service_url()
    debug = getattr(args, "debug", False)
    try:
        result = execute_benchmark_cancel(
            args.run_id, service_url=service_url, debug=debug
        )
        print(json.dumps(result, indent=2))
    except Exception as exc:
        _handle_api_error(exc)
        sys.exit(1)


def _handle_benchmark_delete(args) -> None:
    service_url = getattr(args, "service_url", None) or get_service_url()
    debug = getattr(args, "debug", False)
    try:
        result = execute_benchmark_delete(
            args.run_id, service_url=service_url, debug=debug
        )
        print(json.dumps(result, indent=2))
    except Exception as exc:
        _handle_api_error(exc)
        sys.exit(1)


def _handle_device_pool_list(args) -> None:
    service_url = getattr(args, "service_url", None) or get_service_url()
    debug = getattr(args, "debug", False)
    json_output = getattr(args, "json", False)
    try:
        result = execute_device_pool_list(
            limit=args.limit,
            page=args.page,
            service_url=service_url,
            debug=debug,
        )
        print(format_device_pool(result, json_output=json_output))
    except Exception as exc:
        _handle_api_error(exc)
        sys.exit(1)


def _handle_device_pool_add(args) -> None:
    service_url = getattr(args, "service_url", None) or get_service_url()
    debug = getattr(args, "debug", False)
    try:
        result = execute_device_pool_add(
            device_type=args.device_type,
            cluster_names=getattr(args, "cluster_names", None),
            helm_chart=getattr(args, "helm_chart", None),
            description=getattr(args, "description", None),
            capabilities_json=getattr(args, "capabilities", None),
            service_url=service_url,
            debug=debug,
        )
        print(json.dumps(result, indent=2))
    except Exception as exc:
        _handle_api_error(exc)
        sys.exit(1)


def _handle_device_pool_update(args) -> None:
    service_url = getattr(args, "service_url", None) or get_service_url()
    debug = getattr(args, "debug", False)
    try:
        result = execute_device_pool_update(
            device_type=args.device_type,
            cluster_names=getattr(args, "cluster_names", None),
            helm_chart=getattr(args, "helm_chart", None),
            description=getattr(args, "description", None),
            capabilities_json=getattr(args, "capabilities", None),
            service_url=service_url,
            debug=debug,
        )
        print(json.dumps(result, indent=2))
    except Exception as exc:
        _handle_api_error(exc)
        sys.exit(1)


def _handle_device_pool_remove(args) -> None:
    service_url = getattr(args, "service_url", None) or get_service_url()
    debug = getattr(args, "debug", False)
    try:
        result = execute_device_pool_remove(
            args.device_type, service_url=service_url, debug=debug
        )
        print(json.dumps(result, indent=2))
    except Exception as exc:
        _handle_api_error(exc)
        sys.exit(1)


def _setup_benchmark_subcommands(subparsers) -> None:
    # Run
    run_parser = subparsers.add_parser("run", help="Run a new benchmark")
    run_parser.add_argument("--name", required=True, help="Benchmark run name")
    run_parser.add_argument("--model-specs", required=True, help="Model specifications (JSON list of objects with catalog_id, model_name, versions)")
    run_parser.add_argument("--device-types", nargs="+", required=True, help="Target device types")
    run_parser.add_argument("--description", help="Benchmark description")
    run_parser.add_argument("--benchmark-type", default="inference_speed", help="Type of benchmark")
    run_parser.add_argument("--wait", action="store_true", help="Wait for benchmark completion")
    run_parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    run_parser.set_defaults(_command_handler=_handle_benchmark_run)

    # List
    list_parser = subparsers.add_parser("list", help="List benchmark runs")
    list_parser.add_argument("--status", help="Filter by status")
    list_parser.add_argument("--limit", type=int, default=20, help="Results per page")
    list_parser.add_argument("--page", type=int, default=1, help="Page number")
    list_parser.add_argument("--json", action="store_true", help="Output in JSON format")
    list_parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    list_parser.set_defaults(_command_handler=_handle_benchmark_list)

    # Get
    get_parser = subparsers.add_parser("get", help="Get benchmark details")
    get_parser.add_argument("run_id", help="Benchmark run ID")
    get_parser.add_argument("--json", action="store_true", help="Output in JSON format")
    get_parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    get_parser.set_defaults(_command_handler=_handle_benchmark_get)

    # Cancel
    cancel_parser = subparsers.add_parser("cancel", help="Cancel benchmark run")
    cancel_parser.add_argument("run_id", help="Benchmark run ID")
    cancel_parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    cancel_parser.set_defaults(_command_handler=_handle_benchmark_cancel)

    # Delete
    delete_parser = subparsers.add_parser("delete", help="Delete benchmark run record")
    delete_parser.add_argument("run_id", help="Benchmark run ID")
    delete_parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    delete_parser.set_defaults(_command_handler=_handle_benchmark_delete)


def _setup_device_pool_subcommands(subparsers) -> None:
    # List
    list_parser = subparsers.add_parser("list", help="List device pool")
    list_parser.add_argument("--limit", type=int, default=20, help="Results per page")
    list_parser.add_argument("--page", type=int, default=1, help="Page number")
    list_parser.add_argument("--json", action="store_true", help="Output in JSON format")
    list_parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    list_parser.set_defaults(_command_handler=_handle_device_pool_list)

    # Add
    add_parser = subparsers.add_parser("add", help="Add device to pool (Admin)")
    add_parser.add_argument("--device-type", required=True, help="Device type identifier")
    add_parser.add_argument("--cluster-names", nargs="+", required=True, help="Supporting cluster names")
    add_parser.add_argument("--helm-chart", required=True, help="Helm chart name")
    add_parser.add_argument("--description", help="Device description")
    add_parser.add_argument("--capabilities", help="Device capabilities (JSON)")
    add_parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    add_parser.set_defaults(_command_handler=_handle_device_pool_add)

    # Update
    update_parser = subparsers.add_parser("update", help="Update device pool entry (Admin)")
    update_parser.add_argument("device_type", help="Device type to update")
    update_parser.add_argument("--cluster-names", nargs="+", help="Updated cluster names")
    update_parser.add_argument("--helm-chart", help="Updated Helm chart name")
    update_parser.add_argument("--description", help="Updated description")
    update_parser.add_argument("--capabilities", help="Updated capabilities (JSON)")
    update_parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    update_parser.set_defaults(_command_handler=_handle_device_pool_update)

    # Remove
    remove_parser = subparsers.add_parser("remove", help="Remove device from pool (Admin)")
    remove_parser.add_argument("device_type", help="Device type to remove")
    remove_parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    remove_parser.set_defaults(_command_handler=_handle_device_pool_remove)


def register_benchmark_commands() -> None:
    """Register benchmark and device-pool command groups."""
    benchmark_spec = CommandSpec(
        name="benchmarks",
        help="Manage model benchmarks",
        subcommand_setup=_setup_benchmark_subcommands,
    )
    register_command(benchmark_spec)

    device_pool_spec = CommandSpec(
        name="device-pool",
        help="Manage benchmark device pool",
        subcommand_setup=_setup_device_pool_subcommands,
    )
    register_command(device_pool_spec)
