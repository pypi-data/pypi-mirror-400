"""
Benchmark Service for EdgeAI SDK

Provides Python interface for model benchmarking operations including
creating, monitoring, and retrieving benchmark results.
"""

from typing import Any, Dict, List, Optional
import time
import logging

logger = logging.getLogger(__name__)


class BenchmarkConfig:
    """Configuration for a benchmark run."""

    def __init__(
        self,
        duration_seconds: int = 60,
        concurrency: int = 1,
        batch_size: int = 1,
        warmup_iterations: int = 10,
        iterations: Optional[int] = None,
        max_tokens: Optional[int] = None,
        prompt_length: Optional[int] = None,
    ):
        """Initialize benchmark configuration.

        Parameters
        ----------
        duration_seconds : int
            Benchmark duration in seconds (30-3600). Default: 60
        concurrency : int
            Number of parallel inference workers (1-16). Default: 1
        batch_size : int
            Batch size for inference (1-32). Default: 1
        warmup_iterations : int
            Number of warmup iterations (0-100). Default: 10
        iterations : int, optional
            If set, run N iterations instead of duration
        max_tokens : int, optional
            Max tokens for GenAI models (1-4096)
        prompt_length : int, optional
            Input token count for GenAI (1-2048)
        """
        self.duration_seconds = duration_seconds
        self.concurrency = concurrency
        self.batch_size = batch_size
        self.warmup_iterations = warmup_iterations
        self.iterations = iterations
        self.max_tokens = max_tokens
        self.prompt_length = prompt_length

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        config = {
            "duration_seconds": self.duration_seconds,
            "concurrency": self.concurrency,
            "batch_size": self.batch_size,
            "warmup_iterations": self.warmup_iterations,
        }
        if self.iterations is not None:
            config["iterations"] = self.iterations
        if self.max_tokens is not None:
            config["max_tokens"] = self.max_tokens
        if self.prompt_length is not None:
            config["prompt_length"] = self.prompt_length
        return config


class BenchmarkResult:
    """Result from a single device/version benchmark."""

    def __init__(self, data: Dict[str, Any]):
        self._data = data
        self.result_id = data.get("result_id")
        self.run_id = data.get("run_id")
        self.device_type = data.get("device_type")
        self.cluster_name = data.get("cluster_name")
        self.model_version = data.get("model_version")
        self.metrics = BenchmarkMetrics(data.get("metrics", {}))
        self.hardware_info = data.get("hardware_info")
        self.logs_url = data.get("logs_url")
        self.created_at = data.get("created_at")

    def __repr__(self) -> str:
        return (
            f"BenchmarkResult(device={self.device_type}, "
            f"version={self.model_version}, "
            f"fps={self.metrics.throughput_fps})"
        )


class BenchmarkMetrics:
    """Metrics collected during benchmark execution."""

    def __init__(self, data: Dict[str, Any]):
        self._data = data
        # Latency metrics
        self.latency_p50_ms = data.get("latency_p50_ms", 0)
        self.latency_p95_ms = data.get("latency_p95_ms", 0)
        self.latency_p99_ms = data.get("latency_p99_ms", 0)
        self.latency_avg_ms = data.get("latency_avg_ms")
        self.latency_min_ms = data.get("latency_min_ms")
        self.latency_max_ms = data.get("latency_max_ms")
        # Throughput
        self.throughput_fps = data.get("throughput_fps")
        self.throughput_tps = data.get("throughput_tps")
        # Resource usage
        self.cpu_usage_percent = data.get("cpu_usage_percent", 0)
        self.memory_usage_mb = data.get("memory_usage_mb", 0)
        self.gpu_utilization_percent = data.get("gpu_utilization_percent")
        self.power_usage_watts = data.get("power_usage_watts")
        # Request stats
        self.total_requests = data.get("total_requests")
        self.failed_requests = data.get("failed_requests")
        self.error_rate = data.get("error_rate")

    def __repr__(self) -> str:
        return (
            f"BenchmarkMetrics(latency_p50={self.latency_p50_ms}ms, "
            f"fps={self.throughput_fps}, cpu={self.cpu_usage_percent}%)"
        )


class BenchmarkRun:
    """Represents a benchmark run with methods to monitor and retrieve results."""

    def __init__(self, data: Dict[str, Any], service: "BenchmarkService"):
        self._data = data
        self._service = service
        self.run_id = data.get("run_id")
        self.name = data.get("name")
        self.description = data.get("description")
        self.model_specs = data.get("model_specs", [])
        self.target_device_types = data.get("target_device_types", [])
        self.benchmark_type = data.get("benchmark_type")
        self.configuration = data.get("configuration", {})
        self.status = data.get("status")
        self.progress = data.get("progress", 0)
        self.expected_results = data.get("expected_results", 0)
        self.received_results = data.get("received_results", 0)
        self.error_message = data.get("error_message")
        self.started_at = data.get("started_at")
        self.completed_at = data.get("completed_at")
        self.created_at = data.get("created_at")
        self._results: List[BenchmarkResult] = []

    def refresh(self, backend_jwt: str) -> "BenchmarkRun":
        """Refresh benchmark status from server."""
        updated = self._service.get(backend_jwt, self.run_id)
        if updated:
            self.__dict__.update(updated.__dict__)
        return self

    def wait_for_completion(
        self,
        backend_jwt: str,
        timeout: int = 600,
        poll_interval: int = 10,
        verbose: bool = True,
    ) -> List[BenchmarkResult]:
        """Wait for benchmark to complete and return results.

        Parameters
        ----------
        backend_jwt : str
            JWT authentication token
        timeout : int
            Maximum time to wait in seconds. Default: 600 (10 minutes)
        poll_interval : int
            Seconds between status checks. Default: 10
        verbose : bool
            Print progress updates. Default: True

        Returns
        -------
        List[BenchmarkResult]
            List of benchmark results when complete

        Raises
        ------
        TimeoutError
            If benchmark doesn't complete within timeout
        RuntimeError
            If benchmark fails or is cancelled
        """
        terminal_statuses = {"completed", "failed", "cancelled", "timeout"}
        start_time = time.time()

        while True:
            self.refresh(backend_jwt)

            if verbose:
                print(
                    f"  Status: {self.status} | Progress: {self.progress}% | "
                    f"Results: {self.received_results}/{self.expected_results}"
                )

            if self.status in terminal_statuses:
                break

            elapsed = time.time() - start_time
            if elapsed >= timeout:
                raise TimeoutError(
                    f"Benchmark {self.run_id} did not complete within {timeout} seconds"
                )

            remaining = timeout - elapsed
            sleep_time = min(poll_interval, remaining)
            time.sleep(sleep_time)

        if self.status == "failed":
            raise RuntimeError(
                f"Benchmark failed: {self.error_message or 'Unknown error'}"
            )
        if self.status == "cancelled":
            raise RuntimeError("Benchmark was cancelled")
        if self.status == "timeout":
            raise RuntimeError("Benchmark timed out on device")

        # Fetch full results
        return self.get_results(backend_jwt)

    def get_results(self, backend_jwt: str) -> List[BenchmarkResult]:
        """Get all results for this benchmark run."""
        headers = {"Authorization": f"Bearer {backend_jwt}"}
        results_data = self._service._http.get(
            f"{self._service.backend_url}/api/v1/benchmarks/{self.run_id}/results",
            headers=headers
        )
        # API returns a bare list of result objects directly
        if isinstance(results_data, list):
            self._results = [BenchmarkResult(r) for r in results_data]
        elif isinstance(results_data, dict):
            # Fallback if response format changes to dict-wrapped
            self._results = [BenchmarkResult(r) for r in results_data.get("results", [])]
        else:
            # Unexpected response type; log and return an empty result list
            logger.warning(
                "Unexpected benchmark results response type: %s",
                type(results_data).__name__,
            )
            self._results = []
        return self._results

    def cancel(self, backend_jwt: str) -> bool:
        """Cancel this benchmark run."""
        return self._service.cancel(backend_jwt, self.run_id)

    def delete(self, backend_jwt: str) -> bool:
        """Delete this benchmark run record."""
        return self._service.delete(backend_jwt, self.run_id)

    def __repr__(self) -> str:
        return (
            f"BenchmarkRun(id={self.run_id}, name={self.name}, "
            f"status={self.status}, progress={self.progress}%)"
        )


class BenchmarkService:
    """Service for managing benchmark runs and device pools.

    Provides methods to create, list, retrieve, and cancel benchmark runs,
    as well as managing the pool of available edge devices.
    """

    def __init__(self, backend_url: str, http_client):
        """Initialize benchmark service with HTTP client.

        Parameters
        ----------
        backend_url : str
            Backend API URL
        http_client
            HTTP client for making API requests
        """
        self.backend_url = backend_url.rstrip("/")
        self._http = http_client

    def create(
        self,
        backend_jwt: str,
        name: str,
        model_specs: List[Dict[str, Any]],
        device_types: List[str],
        *,
        description: Optional[str] = None,
        benchmark_type: str = "inference_speed",
        config: Optional[BenchmarkConfig] = None,
    ) -> BenchmarkRun:
        """Create a new benchmark run.

        Parameters
        ----------
        backend_jwt : str
            JWT authentication token
        name : str
            Name for the benchmark run
        model_specs : List[Dict[str, Any]]
            List of models to benchmark. Each dict should have:
            - catalog_id: str
            - model_name: str
            - versions: List[str]
        device_types : List[str]
            List of target device types (e.g., ["jetson_agx", "x86_intel"])
        description : str, optional
            Description of the benchmark
        benchmark_type : str
            Type of benchmark: inference_speed, stress, sustained, latency, throughput
        config : BenchmarkConfig, optional
            Benchmark configuration (uses defaults if not provided)

        Returns
        -------
        BenchmarkRun
            Created benchmark run object
        """
        if config is None:
            config = BenchmarkConfig()

        payload = {
            "name": name,
            "model_specs": model_specs,
            "target_device_types": device_types,
            "benchmark_type": benchmark_type,
            "configuration": config.to_dict(),
        }
        if description:
            payload["description"] = description

        headers = {"Authorization": f"Bearer {backend_jwt}"}
        response = self._http.post(f"{self.backend_url}/api/v1/benchmarks", headers=headers, json=payload)
        return BenchmarkRun(response, self)

    def get(self, backend_jwt: str, run_id: str) -> Optional[BenchmarkRun]:
        """Retrieve a specific benchmark run.

        Parameters
        ----------
        backend_jwt : str
            JWT authentication token
        run_id : str
            Benchmark run ID

        Returns
        -------
        BenchmarkRun or None
            Benchmark run if found, None otherwise
        """
        try:
            headers = {"Authorization": f"Bearer {backend_jwt}"}
            response = self._http.get(f"{self.backend_url}/api/v1/benchmarks/{run_id}", headers=headers)
            return BenchmarkRun(response, self)
        except Exception as e:
            logger.warning(f"Failed to get benchmark {run_id}: {e}")
            return None

    def list(
        self,
        backend_jwt: str,
        status: Optional[str] = None,
        limit: int = 20,
        page: int = 1,
    ) -> Dict[str, Any]:
        """List benchmark runs with optional filters.

        Parameters
        ----------
        backend_jwt : str
            JWT authentication token
        status : str, optional
            Filter by status
        limit : int
            Results per page (default: 20)
        page : int
            Page number (default: 1)

        Returns
        -------
        Dict[str, Any]
            Paginated list of benchmark runs
        """
        params = {"limit": limit, "page": page}
        if status:
            params["status"] = status

        headers = {"Authorization": f"Bearer {backend_jwt}"}
        response = self._http.get(f"{self.backend_url}/api/v1/benchmarks", headers=headers, params=params)
        return {
            "items": [BenchmarkRun(item, self) for item in response.get("items", [])],
            "total": response.get("total", 0),
            "page": response.get("page", 1),
            "total_pages": response.get("total_pages", 1),
            "has_next": response.get("has_next", False),
            "has_previous": response.get("has_previous", False),
        }

    def cancel(self, backend_jwt: str, run_id: str) -> bool:
        """Cancel a benchmark run.

        Parameters
        ----------
        backend_jwt : str
            JWT authentication token
        run_id : str
            Benchmark run ID to cancel

        Returns
        -------
        bool
            True if cancelled successfully

        Raises
        ------
        requests.exceptions.HTTPError
            If the API request fails
        """
        headers = {"Authorization": f"Bearer {backend_jwt}"}
        self._http.post(f"{self.backend_url}/api/v1/benchmarks/{run_id}/cancel", headers=headers)
        return True

    def delete(self, backend_jwt: str, run_id: str) -> bool:
        """Delete a benchmark run record.

        Parameters
        ----------
        backend_jwt : str
            JWT authentication token
        run_id : str
            Benchmark run ID to delete

        Returns
        -------
        bool
            True if deleted successfully

        Raises
        ------
        requests.exceptions.HTTPError
            If the API request fails
        """
        headers = {"Authorization": f"Bearer {backend_jwt}"}
        self._http.delete(f"{self.backend_url}/api/v1/benchmarks/{run_id}", headers=headers)
        return True

    # Device Pool Management

    def list_device_pool(self, backend_jwt: str, limit: int = 20, page: int = 1) -> Dict[str, Any]:
        """List available device types for benchmarking.

        Parameters
        ----------
        backend_jwt : str
            JWT authentication token
        limit : int
            Results per page (default: 20)
        page : int
            Page number (default: 1)

        Returns
        -------
        Dict[str, Any]
            Paginated list of available devices
        """
        params = {"limit": limit, "page": page}
        headers = {"Authorization": f"Bearer {backend_jwt}"}
        response = self._http.get(f"{self.backend_url}/api/v1/benchmarks/device-pool", headers=headers, params=params)
        return response

    def add_device_to_pool(
        self,
        backend_jwt: str,
        device_type: str,
        cluster_names: List[str],
        helm_chart: str,
        description: Optional[str] = None,
        capabilities: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Add a new device type to the benchmark pool.

        Parameters
        ----------
        backend_jwt : str
            JWT authentication token
        device_type : str
            Unique identifier for the device type
        cluster_names : List[str]
            List of cluster names supporting this device type
        helm_chart : str
            Name of the Helm chart to use for benchmarks on this device
        description : str, optional
            Human-readable description
        capabilities : Dict, optional
            Device capabilities (architecture, gpu, etc.)

        Returns
        -------
        Dict[str, Any]
            The created device pool entry
        """
        payload = {
            "device_type": device_type,
            "cluster_names": cluster_names,
            "helm_chart": helm_chart,
        }
        if description:
            payload["description"] = description
        if capabilities:
            payload["capabilities"] = capabilities

        headers = {"Authorization": f"Bearer {backend_jwt}"}
        return self._http.post(f"{self.backend_url}/api/v1/benchmarks/device-pool", headers=headers, json=payload)

    def update_device_pool(
        self,
        backend_jwt: str,
        device_type: str,
        cluster_names: Optional[List[str]] = None,
        helm_chart: Optional[str] = None,
        description: Optional[str] = None,
        capabilities: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Update an existing device pool entry.

        Parameters
        ----------
        backend_jwt : str
            JWT authentication token
        device_type : str
            The device type to update
        cluster_names : List[str], optional
            Updated list of cluster names
        helm_chart : str, optional
            Updated Helm chart name
        description : str, optional
            Updated description
        capabilities : Dict, optional
            Updated capabilities

        Returns
        -------
        Dict[str, Any]
            The updated device pool entry
        """
        payload = {}
        if cluster_names is not None:
            payload["cluster_names"] = cluster_names
        if helm_chart is not None:
            payload["helm_chart"] = helm_chart
        if description is not None:
            payload["description"] = description
        if capabilities is not None:
            payload["capabilities"] = capabilities

        headers = {"Authorization": f"Bearer {backend_jwt}"}
        return self._http.put(f"{self.backend_url}/api/v1/benchmarks/device-pool/{device_type}", headers=headers, json=payload)

    def remove_device_from_pool(self, backend_jwt: str, device_type: str) -> bool:
        """Remove a device type from the pool.

        Parameters
        ----------
        backend_jwt : str
            JWT authentication token
        device_type : str
            The device type to remove

        Returns
        -------
        bool
            True if removed successfully

        Raises
        ------
        requests.exceptions.HTTPError
            If the API request fails
        """
        headers = {"Authorization": f"Bearer {backend_jwt}"}
        self._http.delete(f"{self.backend_url}/api/v1/benchmarks/device-pool/{device_type}", headers=headers)
        return True
