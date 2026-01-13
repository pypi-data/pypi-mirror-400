"""
Unit tests for the SDK Benchmark Service.

Tests cover:
- BenchmarkConfig initialization and serialization
- BenchmarkMetrics parsing
- BenchmarkResult parsing
- BenchmarkRun operations
- BenchmarkService CRUD operations
"""

import unittest
from unittest.mock import Mock

from zededa_edgeai_sdk.services.benchmarks import (
    BenchmarkConfig,
    BenchmarkMetrics,
    BenchmarkResult,
    BenchmarkRun,
    BenchmarkService,
)


class TestBenchmarkConfig(unittest.TestCase):
    """Test BenchmarkConfig class."""

    def test_default_values(self):
        """Test default configuration values."""
        config = BenchmarkConfig()
        self.assertEqual(config.duration_seconds, 60)
        self.assertEqual(config.concurrency, 1)
        self.assertEqual(config.batch_size, 1)
        self.assertEqual(config.warmup_iterations, 10)
        self.assertIsNone(config.iterations)
        self.assertIsNone(config.max_tokens)
        self.assertIsNone(config.prompt_length)

    def test_custom_values(self):
        """Test configuration with custom values."""
        config = BenchmarkConfig(
            duration_seconds=120,
            concurrency=4,
            batch_size=8,
            warmup_iterations=20,
            iterations=1000,
            max_tokens=256,
            prompt_length=128,
        )
        self.assertEqual(config.duration_seconds, 120)
        self.assertEqual(config.concurrency, 4)
        self.assertEqual(config.batch_size, 8)
        self.assertEqual(config.warmup_iterations, 20)
        self.assertEqual(config.iterations, 1000)
        self.assertEqual(config.max_tokens, 256)
        self.assertEqual(config.prompt_length, 128)

    def test_to_dict_basic(self):
        """Test to_dict with basic configuration."""
        config = BenchmarkConfig()
        result = config.to_dict()
        self.assertEqual(result["duration_seconds"], 60)
        self.assertEqual(result["concurrency"], 1)
        self.assertEqual(result["batch_size"], 1)
        self.assertEqual(result["warmup_iterations"], 10)
        self.assertNotIn("iterations", result)
        self.assertNotIn("max_tokens", result)
        self.assertNotIn("prompt_length", result)

    def test_to_dict_with_optional_fields(self):
        """Test to_dict includes optional fields when set."""
        config = BenchmarkConfig(
            iterations=500,
            max_tokens=128,
            prompt_length=64,
        )
        result = config.to_dict()
        self.assertEqual(result["iterations"], 500)
        self.assertEqual(result["max_tokens"], 128)
        self.assertEqual(result["prompt_length"], 64)


class TestBenchmarkMetrics(unittest.TestCase):
    """Test BenchmarkMetrics class."""

    def test_empty_data(self):
        """Test metrics with empty data."""
        metrics = BenchmarkMetrics({})
        self.assertEqual(metrics.latency_p50_ms, 0)
        self.assertEqual(metrics.latency_p95_ms, 0)
        self.assertEqual(metrics.latency_p99_ms, 0)
        self.assertEqual(metrics.cpu_usage_percent, 0)
        self.assertEqual(metrics.memory_usage_mb, 0)
        self.assertIsNone(metrics.latency_avg_ms)
        self.assertIsNone(metrics.throughput_fps)

    def test_full_data(self):
        """Test metrics with full data."""
        data = {
            "latency_p50_ms": 25.5,
            "latency_p95_ms": 35.0,
            "latency_p99_ms": 45.0,
            "latency_avg_ms": 28.0,
            "latency_min_ms": 20.0,
            "latency_max_ms": 50.0,
            "throughput_fps": 40.0,
            "throughput_tps": None,
            "cpu_usage_percent": 65,
            "memory_usage_mb": 512,
            "gpu_utilization_percent": 85,
            "power_usage_watts": 15.5,
            "total_requests": 2400,
            "failed_requests": 5,
            "error_rate": 0.2,
        }
        metrics = BenchmarkMetrics(data)
        self.assertEqual(metrics.latency_p50_ms, 25.5)
        self.assertEqual(metrics.latency_p95_ms, 35.0)
        self.assertEqual(metrics.latency_p99_ms, 45.0)
        self.assertEqual(metrics.latency_avg_ms, 28.0)
        self.assertEqual(metrics.latency_min_ms, 20.0)
        self.assertEqual(metrics.latency_max_ms, 50.0)
        self.assertEqual(metrics.throughput_fps, 40.0)
        self.assertEqual(metrics.cpu_usage_percent, 65)
        self.assertEqual(metrics.memory_usage_mb, 512)
        self.assertEqual(metrics.gpu_utilization_percent, 85)
        self.assertEqual(metrics.power_usage_watts, 15.5)
        self.assertEqual(metrics.total_requests, 2400)
        self.assertEqual(metrics.failed_requests, 5)
        self.assertEqual(metrics.error_rate, 0.2)

    def test_repr(self):
        """Test string representation."""
        metrics = BenchmarkMetrics({
            "latency_p50_ms": 25.5,
            "throughput_fps": 40.0,
            "cpu_usage_percent": 65,
        })
        repr_str = repr(metrics)
        self.assertIn("latency_p50=25.5ms", repr_str)
        self.assertIn("fps=40.0", repr_str)
        self.assertIn("cpu=65%", repr_str)


class TestBenchmarkResult(unittest.TestCase):
    """Test BenchmarkResult class."""

    def test_result_parsing(self):
        """Test parsing benchmark result data."""
        data = {
            "result_id": "result-123",
            "run_id": "run-456",
            "device_type": "jetson_agx",
            "cluster_name": "lab-jetson-01",
            "model_version": "1",
            "metrics": {
                "latency_p50_ms": 25.5,
                "throughput_fps": 40.0,
            },
            "hardware_info": {
                "device": "Jetson AGX Orin",
                "architecture": "aarch64",
            },
            "logs_url": "https://example.com/logs/123",
            "created_at": "2024-01-15T10:00:00Z",
        }
        result = BenchmarkResult(data)
        self.assertEqual(result.result_id, "result-123")
        self.assertEqual(result.run_id, "run-456")
        self.assertEqual(result.device_type, "jetson_agx")
        self.assertEqual(result.cluster_name, "lab-jetson-01")
        self.assertEqual(result.model_version, "1")
        self.assertIsInstance(result.metrics, BenchmarkMetrics)
        self.assertEqual(result.metrics.latency_p50_ms, 25.5)
        self.assertEqual(result.hardware_info["device"], "Jetson AGX Orin")
        self.assertEqual(result.logs_url, "https://example.com/logs/123")

    def test_repr(self):
        """Test string representation."""
        data = {
            "device_type": "jetson_agx",
            "model_version": "1",
            "metrics": {"throughput_fps": 40.0},
        }
        result = BenchmarkResult(data)
        repr_str = repr(result)
        self.assertIn("jetson_agx", repr_str)
        self.assertIn("version=1", repr_str)


class TestBenchmarkRun(unittest.TestCase):
    """Test BenchmarkRun class."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_service = Mock(spec=BenchmarkService)
        self.run_data = {
            "run_id": "run-123",
            "name": "Test Benchmark",
            "description": "Test description",
            "catalog_id": "catalog-456",
            "model_name": "test-model",
            "model_versions": ["1", "2"],
            "target_device_types": ["jetson_agx"],
            "benchmark_type": "inference_speed",
            "configuration": {"duration_seconds": 60},
            "status": "pending",
            "progress": 0,
            "expected_results": 2,
            "received_results": 0,
            "error_message": None,
            "started_at": None,
            "completed_at": None,
            "created_at": "2024-01-15T10:00:00Z",
        }

    def test_run_parsing(self):
        """Test parsing benchmark run data."""
        run = BenchmarkRun(self.run_data, self.mock_service)
        self.assertEqual(run.run_id, "run-123")
        self.assertEqual(run.name, "Test Benchmark")
        self.assertEqual(run.description, "Test description")
        self.assertEqual(run.model_specs, self.run_data.get("model_specs", []))
        self.assertEqual(run.target_device_types, ["jetson_agx"])
        self.assertEqual(run.benchmark_type, "inference_speed")
        self.assertEqual(run.status, "pending")
        self.assertEqual(run.progress, 0)
        self.assertEqual(run.expected_results, 2)
        self.assertEqual(run.received_results, 0)

    def test_refresh(self):
        """Test refresh method."""
        run = BenchmarkRun(self.run_data, self.mock_service)
        updated_data = self.run_data.copy()
        updated_data["status"] = "running"
        updated_data["progress"] = 50
        self.mock_service.get.return_value = BenchmarkRun(updated_data, self.mock_service)

        run.refresh("test-jwt")
        self.assertEqual(run.status, "running")
        self.assertEqual(run.progress, 50)

    def test_cancel(self):
        """Test cancel method."""
        run = BenchmarkRun(self.run_data, self.mock_service)
        self.mock_service.cancel.return_value = True

        result = run.cancel("test-jwt")
        self.assertTrue(result)
        self.mock_service.cancel.assert_called_once_with("test-jwt", "run-123")

    def test_get_results(self):
        """Test get_results method."""
        run = BenchmarkRun(self.run_data, self.mock_service)
        mock_http = Mock()
        mock_http.get.return_value = [
            {"result_id": "r1", "device_type": "jetson_agx", "metrics": {}},
            {"result_id": "r2", "device_type": "jetson_agx", "metrics": {}},
        ]
        self.mock_service._http = mock_http
        self.mock_service.backend_url = "https://test.example.com"

        results = run.get_results("test-jwt")
        self.assertEqual(len(results), 2)
        self.assertIsInstance(results[0], BenchmarkResult)

    def test_repr(self):
        """Test string representation."""
        run = BenchmarkRun(self.run_data, self.mock_service)
        repr_str = repr(run)
        self.assertIn("run-123", repr_str)
        self.assertIn("Test Benchmark", repr_str)
        self.assertIn("pending", repr_str)


class TestBenchmarkService(unittest.TestCase):
    """Test BenchmarkService class."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_http = Mock()
        self.service = BenchmarkService("https://test.example.com", self.mock_http)
        self.test_jwt = "test-jwt-token"

    def test_create_with_defaults(self):
        """Test creating benchmark with default config."""
        self.mock_http.post.return_value = {
            "run_id": "new-run",
            "name": "Test",
            "status": "pending",
        }

        result = self.service.create(
            backend_jwt=self.test_jwt,
            name="Test",
            model_specs=[{"catalog_id": "catalog-1", "model_name": "model-1", "versions": ["1"]}],
            device_types=["jetson_agx"],
        )

        self.assertIsInstance(result, BenchmarkRun)
        self.assertEqual(result.run_id, "new-run")

        # Verify API call
        call_args = self.mock_http.post.call_args
        self.assertEqual(call_args[0][0], "https://test.example.com/api/v1/benchmarks")
        self.assertIn("Authorization", call_args[1]["headers"])
        self.assertEqual(call_args[1]["headers"]["Authorization"], f"Bearer {self.test_jwt}")
        payload = call_args[1]["json"]
        self.assertEqual(payload["name"], "Test")
        self.assertEqual(payload["target_device_types"], ["jetson_agx"])
        self.assertEqual(payload["benchmark_type"], "inference_speed")
        # Default config values
        self.assertEqual(payload["configuration"]["duration_seconds"], 60)

    def test_create_with_custom_config(self):
        """Test creating benchmark with custom config."""
        self.mock_http.post.return_value = {"run_id": "new-run", "status": "pending"}
        config = BenchmarkConfig(duration_seconds=300, batch_size=4)

        self.service.create(
            backend_jwt=self.test_jwt,
            name="Test",
            model_specs=[{"catalog_id": "catalog-1", "model_name": "model-1", "versions": ["1"]}],
            device_types=["jetson_agx"],
            config=config,
            description="Custom benchmark",
            benchmark_type="stress",
        )

        payload = self.mock_http.post.call_args[1]["json"]
        self.assertEqual(payload["configuration"]["duration_seconds"], 300)
        self.assertEqual(payload["configuration"]["batch_size"], 4)
        self.assertEqual(payload["description"], "Custom benchmark")
        self.assertEqual(payload["benchmark_type"], "stress")

    def test_get_success(self):
        """Test getting benchmark by ID."""
        self.mock_http.get.return_value = {
            "run_id": "run-123",
            "name": "Test",
            "status": "completed",
        }

        result = self.service.get(self.test_jwt, "run-123")
        self.assertIsInstance(result, BenchmarkRun)
        self.assertEqual(result.run_id, "run-123")
        call_args = self.mock_http.get.call_args
        self.assertEqual(call_args[0][0], "https://test.example.com/api/v1/benchmarks/run-123")
        self.assertEqual(call_args[1]["headers"]["Authorization"], f"Bearer {self.test_jwt}")

    def test_get_not_found(self):
        """Test getting non-existent benchmark."""
        self.mock_http.get.side_effect = Exception("Not found")

        result = self.service.get(self.test_jwt, "nonexistent")
        self.assertIsNone(result)

    def test_list_default(self):
        """Test listing benchmarks with defaults."""
        self.mock_http.get.return_value = {
            "items": [
                {"run_id": "run-1", "status": "completed"},
                {"run_id": "run-2", "status": "running"},
            ],
            "total": 2,
            "page": 1,
            "total_pages": 1,
            "has_next": False,
            "has_previous": False,
        }

        result = self.service.list(self.test_jwt)
        self.assertEqual(len(result["items"]), 2)
        self.assertEqual(result["total"], 2)
        self.assertFalse(result["has_next"])

        call_args = self.mock_http.get.call_args
        self.assertEqual(call_args[0][0], "https://test.example.com/api/v1/benchmarks")
        self.assertEqual(call_args[1]["params"]["limit"], 20)
        self.assertEqual(call_args[1]["params"]["page"], 1)
        self.assertEqual(call_args[1]["headers"]["Authorization"], f"Bearer {self.test_jwt}")

    def test_list_with_filters(self):
        """Test listing benchmarks with filters."""
        self.mock_http.get.return_value = {"items": [], "total": 0}

        self.service.list(self.test_jwt, status="completed", limit=50, page=2)

        params = self.mock_http.get.call_args[1]["params"]
        self.assertEqual(params["status"], "completed")
        self.assertEqual(params["limit"], 50)
        self.assertEqual(params["page"], 2)

    def test_cancel_success(self):
        """Test cancelling benchmark."""
        self.mock_http.post.return_value = {"status": "cancelled"}

        result = self.service.cancel(self.test_jwt, "run-123")
        self.assertTrue(result)
        call_args = self.mock_http.post.call_args
        self.assertEqual(call_args[0][0], "https://test.example.com/api/v1/benchmarks/run-123/cancel")
        self.assertEqual(call_args[1]["headers"]["Authorization"], f"Bearer {self.test_jwt}")

    def test_cancel_failure(self):
        """Test cancelling non-existent benchmark raises exception."""
        self.mock_http.post.side_effect = Exception("Not found")

        with self.assertRaises(Exception) as ctx:
            self.service.cancel(self.test_jwt, "nonexistent")
        self.assertIn("Not found", str(ctx.exception))

    def test_list_device_pool(self):
        """Test listing device pool."""
        self.mock_http.get.return_value = {
            "devices": [
                {"device_type": "jetson_agx", "is_available": True},
                {"device_type": "x86_intel", "is_available": False},
            ]
        }

        result = self.service.list_device_pool(self.test_jwt)
        self.assertEqual(len(result["devices"]), 2)
        self.assertEqual(result["devices"][0]["device_type"], "jetson_agx")
        call_args = self.mock_http.get.call_args
        self.assertEqual(call_args[0][0], "https://test.example.com/api/v1/benchmarks/device-pool")
        self.assertEqual(call_args[1]["headers"]["Authorization"], f"Bearer {self.test_jwt}")


class TestBenchmarkRunWaitForCompletion(unittest.TestCase):
    """Test BenchmarkRun.wait_for_completion method."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_service = Mock(spec=BenchmarkService)
        self.mock_http = Mock()
        self.mock_service._http = self.mock_http
        self.mock_service.backend_url = "https://test.example.com"
        self.test_jwt = "test-jwt-token"

    def test_wait_completed_immediately(self):
        """Test waiting when benchmark is already completed."""
        run_data = {
            "run_id": "run-123",
            "status": "completed",
            "progress": 100,
            "expected_results": 2,
            "received_results": 2,
        }
        run = BenchmarkRun(run_data, self.mock_service)
        self.mock_service.get.return_value = run
        self.mock_http.get.return_value = []

        results = run.wait_for_completion(self.test_jwt, verbose=False)
        self.assertEqual(results, [])

    def test_wait_failed_raises(self):
        """Test that failed benchmark raises RuntimeError."""
        run_data = {
            "run_id": "run-123",
            "status": "failed",
            "error_message": "Device error",
        }
        run = BenchmarkRun(run_data, self.mock_service)
        self.mock_service.get.return_value = run

        with self.assertRaises(RuntimeError) as ctx:
            run.wait_for_completion(self.test_jwt, verbose=False)
        self.assertIn("Device error", str(ctx.exception))

    def test_wait_cancelled_raises(self):
        """Test that cancelled benchmark raises RuntimeError."""
        run_data = {
            "run_id": "run-123",
            "status": "cancelled",
        }
        run = BenchmarkRun(run_data, self.mock_service)
        self.mock_service.get.return_value = run

        with self.assertRaises(RuntimeError) as ctx:
            run.wait_for_completion(self.test_jwt, verbose=False)
        self.assertIn("cancelled", str(ctx.exception))

    def test_wait_timeout_raises(self):
        """Test that timeout raises TimeoutError."""
        run_data = {
            "run_id": "run-123",
            "status": "running",
            "progress": 50,
        }
        run = BenchmarkRun(run_data, self.mock_service)
        # Always return running status
        self.mock_service.get.return_value = run

        with self.assertRaises(TimeoutError):
            run.wait_for_completion(self.test_jwt, timeout=0.1, poll_interval=0.05, verbose=False)


if __name__ == "__main__":
    unittest.main()
