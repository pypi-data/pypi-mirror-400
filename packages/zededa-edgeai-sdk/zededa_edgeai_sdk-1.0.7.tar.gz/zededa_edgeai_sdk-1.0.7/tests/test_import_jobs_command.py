"""Unit tests for import job CLI commands."""

import os
import unittest
from unittest.mock import Mock, patch

from zededa_edgeai_sdk.commands.import_jobs import (
    execute_import_job_create,
    execute_import_job_list,
    execute_import_job_get,
    execute_import_job_cancel,
    execute_import_job_retry,
    execute_import_job_delete,
)
from zededa_edgeai_sdk.exceptions import AuthenticationError


class TestImportJobCommands(unittest.TestCase):
    """Test cases for import job CLI commands."""

    def setUp(self):
        """Set up test fixtures."""
        self.service_url = "https://api.example.com"
        self.jwt_token = "test-jwt-token"

    @patch.dict(os.environ, {"EDGEAI_ACCESS_TOKEN": "test-jwt-token", "EDGEAI_CURRENT_CATALOG": "c1"})
    @patch("zededa_edgeai_sdk.commands.import_jobs.ZededaEdgeAISDK")
    def test_execute_import_job_create(self, mock_sdk_class):
        """Test creating import job command."""
        mock_sdk = Mock()
        mock_sdk.external_providers.get_external_provider_by_name.return_value = {
            "id": "p1",
            "provider_name": "test-provider"
        }
        mock_sdk.import_jobs.create_import_job.return_value = {
            "job_id": "job-123",
            "status": "pending",
        }
        mock_sdk_class.return_value = mock_sdk

        result = execute_import_job_create(
            provider_name="test-provider",
            model_identifier="user/model",
            target_catalog_id="c1",
            service_url=self.service_url,
            debug=False,
        )

        self.assertEqual(result["job_id"], "job-123")
        mock_sdk.external_providers.get_external_provider_by_name.assert_called_once()
        mock_sdk.import_jobs.create_import_job.assert_called_once()

    @patch.dict(os.environ, {}, clear=True)
    def test_execute_import_job_create_not_logged_in(self):
        """Test creating import job without authentication."""
        with self.assertRaises(AuthenticationError):
            execute_import_job_create(
                provider_name="test-provider",
                model_identifier="user/model",
                target_catalog_id="c1",
                service_url=self.service_url,
                debug=False,
            )

    @patch.dict(os.environ, {"EDGEAI_ACCESS_TOKEN": "test-jwt-token", "EDGEAI_CURRENT_CATALOG": "c1"})
    @patch("zededa_edgeai_sdk.commands.import_jobs.ZededaEdgeAISDK")
    def test_execute_import_job_create_with_wait(self, mock_sdk_class):
        """Test creating import job with wait flag."""
        mock_sdk = Mock()
        mock_sdk.external_providers.get_external_provider_by_name.return_value = {
            "id": "p1",
            "provider_name": "test-provider"
        }
        mock_sdk.import_jobs.create_import_job.return_value = {
            "job_id": "job-123",
            "status": "pending",
        }
        mock_sdk.import_jobs.wait_for_import_job.return_value = {
            "job_id": "job-123",
            "status": "completed",
        }
        mock_sdk_class.return_value = mock_sdk

        result = execute_import_job_create(
            provider_name="test-provider",
            model_identifier="user/model",
            target_catalog_id="c1",
            wait=True,
            service_url=self.service_url,
            debug=False,
        )

        self.assertEqual(result["status"], "completed")
        mock_sdk.external_providers.get_external_provider_by_name.assert_called_once()
        mock_sdk.import_jobs.wait_for_import_job.assert_called_once()

    @patch.dict(os.environ, {"EDGEAI_ACCESS_TOKEN": "test-jwt-token"})
    @patch("zededa_edgeai_sdk.commands.import_jobs.ZededaEdgeAISDK")
    def test_execute_import_job_list(self, mock_sdk_class):
        """Test listing import jobs command."""
        mock_sdk = Mock()
        mock_sdk.import_jobs.list_import_jobs.return_value = {
            "jobs": [{"job_id": "job-1", "status": "completed"}],
            "total": 1,
        }
        mock_sdk_class.return_value = mock_sdk

        result = execute_import_job_list(
            limit=20, page=1, service_url=self.service_url, debug=False
        )

        self.assertEqual(result["total"], 1)
        mock_sdk.import_jobs.list_import_jobs.assert_called_once()

    @patch.dict(os.environ, {"EDGEAI_ACCESS_TOKEN": "test-jwt-token"})
    @patch("zededa_edgeai_sdk.commands.import_jobs.ZededaEdgeAISDK")
    def test_execute_import_job_get(self, mock_sdk_class):
        """Test getting import job command."""
        mock_sdk = Mock()
        mock_sdk.import_jobs.get_import_job.return_value = {
            "job_id": "job-123",
            "status": "completed",
        }
        mock_sdk_class.return_value = mock_sdk

        result = execute_import_job_get(
            "job-123", service_url=self.service_url, debug=False
        )

        self.assertEqual(result["job_id"], "job-123")
        mock_sdk.import_jobs.get_import_job.assert_called_once()

    @patch.dict(os.environ, {"EDGEAI_ACCESS_TOKEN": "test-jwt-token"})
    @patch("zededa_edgeai_sdk.commands.import_jobs.ZededaEdgeAISDK")
    def test_execute_import_job_cancel(self, mock_sdk_class):
        """Test cancelling import job command."""
        mock_sdk = Mock()
        mock_sdk.import_jobs.cancel_import_job.return_value = {
            "job_id": "job-123",
            "status": "cancelled",
        }
        mock_sdk_class.return_value = mock_sdk

        result = execute_import_job_cancel(
            "job-123", service_url=self.service_url, debug=False
        )

        self.assertEqual(result["status"], "cancelled")
        mock_sdk.import_jobs.cancel_import_job.assert_called_once()

    @patch.dict(os.environ, {"EDGEAI_ACCESS_TOKEN": "test-jwt-token"})
    @patch("zededa_edgeai_sdk.commands.import_jobs.ZededaEdgeAISDK")
    def test_execute_import_job_retry(self, mock_sdk_class):
        """Test retrying import job command."""
        mock_sdk = Mock()
        mock_sdk.import_jobs.retry_import_job.return_value = {
            "job_id": "job-123",
            "status": "pending",
        }
        mock_sdk_class.return_value = mock_sdk

        result = execute_import_job_retry(
            "job-123", service_url=self.service_url, debug=False
        )

        self.assertEqual(result["status"], "pending")
        mock_sdk.import_jobs.retry_import_job.assert_called_once()

    @patch.dict(os.environ, {"EDGEAI_ACCESS_TOKEN": "test-jwt-token"})
    @patch("zededa_edgeai_sdk.commands.import_jobs.ZededaEdgeAISDK")
    def test_execute_import_job_delete(self, mock_sdk_class):
        """Test deleting import job command."""
        mock_sdk = Mock()
        mock_sdk.import_jobs.delete_import_job.return_value = {
            "message": "Job deleted successfully"
        }
        mock_sdk_class.return_value = mock_sdk

        result = execute_import_job_delete(
            "job-123", service_url=self.service_url, debug=False
        )

        self.assertIn("message", result)
        mock_sdk.import_jobs.delete_import_job.assert_called_once()


if __name__ == "__main__":
    unittest.main()
