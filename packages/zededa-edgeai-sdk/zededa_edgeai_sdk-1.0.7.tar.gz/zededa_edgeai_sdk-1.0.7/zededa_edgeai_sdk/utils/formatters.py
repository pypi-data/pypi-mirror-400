"""Output formatting utilities for CLI commands.

Provides consistent formatting functions for pretty-printing command outputs
with support for both human-readable and JSON output modes.
"""

from __future__ import annotations

import json
from typing import Any, Dict

__all__ = [
    "format_external_providers",
    "format_external_provider",
    "format_import_jobs",
    "format_import_job",
    "format_catalogs",
    "format_benchmarks",
    "format_benchmark_run",
    "format_device_pool",
]


def format_external_providers(
    data: Dict[str, Any], *, json_output: bool = False
) -> str:
    """Format external providers list for display.
    
    Parameters
    ----------
    data : Dict[str, Any]
        Response data containing 'providers' list
    json_output : bool
        If True, return JSON; otherwise return pretty-printed format
        
    Returns
    -------
    str
        Formatted output string
    """
    if json_output:
        return json.dumps(data, indent=2)
    
    providers = data.get("providers", [])
    total = data.get("total", len(providers))
    page = data.get("page", 1)
    total_pages = data.get("total_pages", 1)
    
    if not providers:
        return "No external providers found."
    
    lines = []
    lines.append("External Providers:")
    lines.append("=" * 80)
    
    for idx, provider in enumerate(providers, 1):
        lines.append(f"\n{idx}. {provider.get('provider_name', 'N/A')}")
        lines.append(f"   ID: {provider.get('id', 'N/A')}")
        lines.append(f"   Type: {provider.get('provider_type', 'N/A')}")
        lines.append(f"   URL: {provider.get('url', 'N/A')}")
        lines.append(f"   Status: {provider.get('status', 'N/A')}")
        
        if provider.get('has_credentials'):
            creds_updated = provider.get('credentials_last_updated', 'N/A')
            lines.append(f"   Credentials: Yes (updated: {creds_updated})")
        else:
            lines.append("   Credentials: No")
        
        # Show connection config if present
        config = provider.get('connection_config', {})
        if config:
            lines.append(f"   Config: {json.dumps(config)}")
        
        if provider.get('description'):
            lines.append(f"   Description: {provider['description']}")
        
        lines.append(f"   Created: {provider.get('created_at', 'N/A')} by {provider.get('created_by', 'N/A')}")
    
    lines.append(f"\n{'=' * 80}")
    lines.append(f"Total: {total} providers | Page {page}/{total_pages}")
    
    return "\n".join(lines)


def format_external_provider(
    data: Dict[str, Any], *, json_output: bool = False
) -> str:
    """Format single external provider for display.
    
    Parameters
    ----------
    data : Dict[str, Any]
        Provider data
    json_output : bool
        If True, return JSON; otherwise return pretty-printed format
        
    Returns
    -------
    str
        Formatted output string
    """
    if json_output:
        return json.dumps(data, indent=2)
    
    lines = []
    lines.append("External Provider Details:")
    lines.append("=" * 80)
    lines.append(f"Name: {data.get('provider_name', 'N/A')}")
    lines.append(f"ID: {data.get('id', 'N/A')}")
    lines.append(f"Type: {data.get('provider_type', 'N/A')}")
    lines.append(f"URL: {data.get('url', 'N/A')}")
    lines.append(f"Status: {data.get('status', 'N/A')}")
    
    lines.append(f"Private: {data.get('is_private', False)}")
    lines.append(f"Read-only: {data.get('is_readonly', False)}")
    lines.append(f"Public: {data.get('is_public', False)}")
    
    if data.get('has_credentials'):
        creds_updated = data.get('credentials_last_updated', 'N/A')
        lines.append(f"Credentials: Yes (last updated: {creds_updated})")
    else:
        lines.append("Credentials: No")
    
    config = data.get('connection_config', {})
    if config:
        lines.append(f"\nConnection Config:")
        for key, value in config.items():
            lines.append(f"  {key}: {value}")
    
    if data.get('description'):
        lines.append(f"\nDescription: {data['description']}")
    
    lines.append(f"\nCreated: {data.get('created_at', 'N/A')} by {data.get('created_by', 'N/A')}")
    lines.append(f"Updated: {data.get('updated_at', 'N/A')} by {data.get('updated_by', 'N/A')}")
    
    return "\n".join(lines)


def format_import_jobs(data: Dict[str, Any], *, json_output: bool = False) -> str:
    """Format import jobs list for display.
    
    Parameters
    ----------
    data : Dict[str, Any]
        Response data containing 'jobs' list
    json_output : bool
        If True, return JSON; otherwise return pretty-printed format
        
    Returns
    -------
    str
        Formatted output string
    """
    if json_output:
        return json.dumps(data, indent=2)
    
    jobs = data.get("jobs", [])
    total = data.get("total", len(jobs))
    page = data.get("page", 1)
    total_pages = data.get("total_pages", 1)
    
    if not jobs:
        return "No import jobs found."
    
    lines = []
    lines.append("Model Import Jobs:")
    lines.append("=" * 80)
    
    for idx, job in enumerate(jobs, 1):
        result_metadata = job.get('result_metadata', {})
        model_name = result_metadata.get('model_name') or job.get('model_identifier', 'N/A')
        lines.append(f"\n{idx}. {model_name}")
        lines.append(f"   Job ID: {job.get('job_id', 'N/A')}")
        
        status = job.get('status', 'N/A')
        progress = job.get('progress_percentage')
        if progress is not None:
            lines.append(f"   Status: {status} ({progress}%)")
        else:
            lines.append(f"   Status: {status}")
        
        lines.append(f"   Provider ID: {job.get('provider_id', 'N/A')}")
        lines.append(f"   Catalog ID: {job.get('catalog_id', 'N/A')}")
        lines.append(f"   Model Identifier: {job.get('model_identifier', 'N/A')}")
        
        # Show version if available
        model_version = result_metadata.get('model_version') or result_metadata.get('version')
        if model_version:
            lines.append(f"   Version: {model_version}")
        
        # Show error if present
        error_details = job.get('error_details')
        if error_details:
            # Truncate long errors
            if len(error_details) > 100:
                error_details = error_details[:100] + "..."
            lines.append(f"   Error: {error_details}")
        
        lines.append(f"   Created: {job.get('created_at', 'N/A')}")
        
        if job.get('completed_at'):
            lines.append(f"   Completed: {job['completed_at']}")
    
    lines.append(f"\n{'=' * 80}")
    lines.append(f"Total: {total} jobs | Page {page}/{total_pages}")
    
    return "\n".join(lines)


def format_import_job(data: Dict[str, Any], *, json_output: bool = False) -> str:
    """Format single import job for display.
    
    Parameters
    ----------
    data : Dict[str, Any]
        Job data
    json_output : bool
        If True, return JSON; otherwise return pretty-printed format
        
    Returns
    -------
    str
        Formatted output string
    """
    if json_output:
        return json.dumps(data, indent=2)
    
    lines = []
    lines.append("Import Job Details:")
    lines.append("=" * 80)
    lines.append(f"Job ID: {data.get('job_id', 'N/A')}")
    
    # Get model name from result_metadata or model_identifier
    result_metadata = data.get('result_metadata', {})
    model_name = result_metadata.get('model_name') or data.get('model_identifier', 'N/A')
    lines.append(f"Model Name: {model_name}")
    
    status = data.get('status', 'N/A')
    lines.append(f"Status: {status}")
    
    # Provider information
    lines.append(f"\nProvider ID: {data.get('provider_id', 'N/A')}")
    lines.append(f"Catalog ID: {data.get('catalog_id', 'N/A')}")
    lines.append(f"Model Identifier: {data.get('model_identifier', 'N/A')}")
    
    # Model version from result_metadata
    model_version = result_metadata.get('model_version') or result_metadata.get('version')
    if model_version:
        lines.append(f"Model Version: {model_version}")
    
    # Progress information
    progress = data.get('progress_percentage')
    current_step = data.get('current_step')
    if progress is not None:
        step_info = f" (current step: {current_step})" if current_step else ""
        lines.append(f"\nProgress: {progress}%{step_info}")
    
    # Error details
    error_details = data.get('error_details')
    if error_details:
        lines.append(f"\nError Details:\n{error_details}")
    
    # Result metadata (catalog URI, artifact URI)
    if result_metadata:
        lines.append(f"\nResult Information:")
        if result_metadata.get('catalog_uri'):
            lines.append(f"  Catalog URI: {result_metadata['catalog_uri']}")
        if result_metadata.get('artifact_uri'):
            lines.append(f"  Artifact URI: {result_metadata['artifact_uri']}")
        if result_metadata.get('upload_temp_dir'):
            lines.append(f"  Upload Directory: {result_metadata['upload_temp_dir']}")
    
    # Retry information
    retry_count = data.get('retry_count', 0)
    can_retry = data.get('can_retry', False)
    if retry_count > 0 or can_retry:
        lines.append(f"\nRetry Count: {retry_count}")
        if can_retry:
            lines.append("  (Can be retried)")
    
    # Timestamps
    lines.append(f"\nCreated: {data.get('created_at', 'N/A')}")
    lines.append(f"Updated: {data.get('updated_at', 'N/A')}")
    
    if data.get('completed_at'):
        lines.append(f"Completed: {data['completed_at']}")
    
    return "\n".join(lines)


def format_catalogs(data: Dict[str, Any], *, json_output: bool = False) -> str:
    """Format catalogs list for display.
    
    Parameters
    ----------
    data : Dict[str, Any]
        Response data containing 'catalogs' list and 'current_catalog'
    json_output : bool
        If True, return JSON; otherwise return pretty-printed format
        
    Returns
    -------
    str
        Formatted output string
    """
    if json_output:
        return json.dumps(data, indent=2)
    
    catalogs = data.get("catalogs", [])
    current_catalog = data.get("current_catalog")
    user_email = data.get("user_email")
    
    if not catalogs:
        return "No catalogs available."
    
    lines = []
    lines.append("Available Catalogs:")
    lines.append("=" * 80)
    
    for idx, catalog in enumerate(catalogs, 1):
        catalog_name = catalog if isinstance(catalog, str) else catalog.get("name", "N/A")
        is_current = catalog_name == current_catalog
        suffix = " (current)" if is_current else ""
        lines.append(f" {idx}. {catalog_name}{suffix}")
    
    lines.append(f"\nTotal: {len(catalogs)} catalogs")
    if current_catalog:
        lines.append(f"Current catalog: {current_catalog}")
    if user_email:
        lines.append(f"User: {user_email}")
    
    return "\n".join(lines)


def format_benchmarks(data: Dict[str, Any], *, json_output: bool = False) -> str:
    """Format benchmark runs list for display."""
    if json_output:
        # Convert BenchmarkRun objects to dicts for JSON serialization
        if "items" in data:
            items = []
            for item in data["items"]:
                if hasattr(item, "_data"):
                    items.append(item._data)
                else:
                    items.append(item)
            data = data.copy()
            data["items"] = items
        return json.dumps(data, indent=2)
    
    items = data.get("items", [])
    total = data.get("total", len(items))
    page = data.get("page", 1)
    total_pages = data.get("total_pages", 1)
    
    if not items:
        return "No benchmarks found."
    
    lines = []
    lines.append("Benchmark Runs:")
    lines.append("=" * 110)
    lines.append(f"{'ID':<38} | {'NAME':<20} | {'STATUS':<12} | {'PROGRESS':<8} | {'CREATED':<20}")
    lines.append("-" * 110)
    
    for item in items:
        if hasattr(item, '_data'):
            item_data = item._data
        else:
            item_data = item
            
        run_id = item_data.get('run_id', 'N/A')
        name = item_data.get('name', 'N/A')
        status = item_data.get('status', 'N/A')
        progress = item_data.get('progress', 0)
        created = item_data.get('created_at', 'N/A')
        if isinstance(created, str) and 'T' in created:
            created = created.split('T')[0] + ' ' + created.split('T')[1].split('.')[0]
            
        lines.append(f"{run_id:<38} | {name[:20]:<20} | {status:<12} | {progress:>7}% | {created:<20}")
    
    lines.append(f"\n{'=' * 110}")
    lines.append(f"Total: {total} benchmarks | Page {page}/{total_pages}")
    
    return "\n".join(lines)


def format_benchmark_run(data: Any, *, json_output: bool = False) -> str:
    """Format single benchmark run for display."""
    if json_output:
        if hasattr(data, '_data'):
            return json.dumps(data._data, indent=2)
        return json.dumps(data, indent=2)
    
    if hasattr(data, '_data'):
        item = data._data
    else:
        item = data
        
    lines = []
    lines.append("Benchmark Run Details:")
    lines.append("=" * 80)
    lines.append(f"ID: {item.get('run_id', 'N/A')}")
    lines.append(f"Name: {item.get('name', 'N/A')}")
    lines.append(f"Status: {item.get('status', 'N/A')}")
    lines.append(f"Progress: {item.get('progress', 0)}%")
    
    if item.get('description'):
        lines.append(f"Description: {item['description']}")
        
    lines.append(f"\nBenchmark Type: {item.get('benchmark_type', 'N/A')}")
    lines.append(f"Target Devices: {', '.join(item.get('target_device_types', []))}")
    
    lines.append("\nModel Specifications:")
    for spec in item.get('model_specs', []):
        lines.append(f"  - Model: {spec.get('model_name')} (Catalog: {spec.get('catalog_id')})")
        lines.append(f"    Versions: {', '.join(spec.get('versions', []))}")
        
    config = item.get('configuration', {})
    if config:
        lines.append("\nConfiguration:")
        for k, v in config.items():
            if v is not None:
                lines.append(f"  {k}: {v}")
                
    results = item.get('results', [])
    if results:
        lines.append("\nResults:")
        lines.append("-" * 80)
        lines.append(f"{'DEVICE':<20} | {'VERSION':<15} | {'FPS':<8} | {'LATENCY (p50)':<15}")
        lines.append("-" * 80)
        for res in results:
            metrics = res.get('metrics', {})
            fps = metrics.get('throughput_fps', 'N/A')
            latency = metrics.get('latency_p50_ms', 'N/A')
            lines.append(f"{res.get('device_type', 'N/A'):<20} | {res.get('model_version', 'N/A'):<15} | {fps:<8} | {latency:<15}")
            
    if item.get('error_message'):
        lines.append(f"\nError: {item['error_message']}")
        
    lines.append(f"\nCreated: {item.get('created_at', 'N/A')}")
    if item.get('started_at'):
        lines.append(f"Started: {item['started_at']}")
    if item.get('completed_at'):
        lines.append(f"Completed: {item['completed_at']}")
        
    return "\n".join(lines)


def format_device_pool(data: Dict[str, Any], *, json_output: bool = False) -> str:
    """Format device pool list for display."""
    if json_output:
        return json.dumps(data, indent=2)
    
    devices = data.get("devices", [])
    total = data.get("total", len(devices))
    
    if not devices:
        return "No devices in pool."
    
    lines = []
    lines.append("Device Pool:")
    lines.append("=" * 130)
    lines.append(f"{'DEVICE TYPE':<40} | {'CLUSTERS':<40} | {'CHART':<30} | {'AVAILABLE'}")
    lines.append("-" * 130)
    
    for dev in devices:
        clusters = ", ".join(dev.get("cluster_names", []))
        if len(clusters) > 40:
            clusters = clusters[:37] + "..."
            
        avail = "Yes" if dev.get("is_available") else "No"
        lines.append(f"{dev.get('device_type', 'N/A'):<40} | {clusters:<40} | {dev.get('helm_chart', 'N/A'):<30} | {avail}")
        
    lines.append(f"\n{'=' * 130}")
    lines.append(f"Total: {total} device types")
    
    return "\n".join(lines)
