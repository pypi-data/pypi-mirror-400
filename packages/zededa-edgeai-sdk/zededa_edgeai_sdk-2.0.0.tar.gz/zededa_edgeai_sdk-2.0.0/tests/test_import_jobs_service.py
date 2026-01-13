"""Unit tests for ImportJobService."""

import os
import tempfile
import unittest
from unittest.mock import Mock, patch

from zededa_edgeai_sdk.services.import_jobs import ImportJobService
from zededa_edgeai_sdk.services.http import HTTPService


class TestImportJobService(unittest.TestCase):
    """Test cases for ImportJobService."""

    def setUp(self):
        """Set up test fixtures."""
        self.backend_url = "https://api.example.com"
        self.http = HTTPService(debug=False)
        self.service = ImportJobService(self.backend_url, self.http)
        self.jwt = "test-jwt-token"

    @patch.object(HTTPService, "request")
    def test_create_import_job(self, mock_request):
        """Test creating a new import job."""
        mock_response = Mock()
        mock_response.status_code = 202
        mock_response.json.return_value = {
            "job_id": "job-123",
            "status": "pending",
            "external_provider_id": "provider-1",
            "model_identifier": "user/model",
        }
        mock_request.return_value = mock_response

        payload = {
            "external_provider_id": "provider-1",
            "model_identifier": "user/model",
            "target_catalog_id": "catalog-1",
        }
        result = self.service.create_import_job(self.jwt, payload)

        self.assertEqual(result["job_id"], "job-123")
        self.assertEqual(result["status"], "pending")
        mock_request.assert_called_once()

    @patch.object(HTTPService, "request")
    def test_get_import_job(self, mock_request):
        """Test getting a specific import job."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "job_id": "job-123",
            "status": "completed",
            "progress": 100,
        }
        mock_request.return_value = mock_response

        result = self.service.get_import_job(self.jwt, "job-123")

        self.assertEqual(result["job_id"], "job-123")
        self.assertEqual(result["status"], "completed")
        mock_request.assert_called_once()

    @patch.object(HTTPService, "request")
    def test_get_import_job_not_found(self, mock_request):
        """Test getting a non-existent import job."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_request.return_value = mock_response

        result = self.service.get_import_job(self.jwt, "nonexistent")

        self.assertEqual(result, {})
        mock_request.assert_called_once()

    @patch.object(HTTPService, "request")
    def test_list_import_jobs(self, mock_request):
        """Test listing import jobs with pagination."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "jobs": [
                {"job_id": "job-1", "status": "completed"},
                {"job_id": "job-2", "status": "running"},
            ],
            "total": 2,
            "page": 1,
            "limit": 20,
        }
        mock_request.return_value = mock_response

        result = self.service.list_import_jobs(
            self.jwt, limit=20, page=1, catalog_id="catalog-1"
        )

        self.assertEqual(len(result["jobs"]), 2)
        self.assertEqual(result["total"], 2)
        mock_request.assert_called_once()

    @patch.object(HTTPService, "request")
    def test_cancel_import_job(self, mock_request):
        """Test cancelling an import job."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "job_id": "job-123",
            "status": "cancelled",
            "message": "Job cancelled successfully",
        }
        mock_request.return_value = mock_response

        result = self.service.cancel_import_job(self.jwt, "job-123")

        self.assertEqual(result["status"], "cancelled")
        mock_request.assert_called_once()

    @patch.object(HTTPService, "request")
    def test_retry_import_job(self, mock_request):
        """Test retrying a failed import job."""
        mock_response = Mock()
        mock_response.status_code = 202
        mock_response.json.return_value = {
            "job_id": "job-123",
            "status": "pending",
            "message": "Job queued for retry",
        }
        mock_request.return_value = mock_response

        result = self.service.retry_import_job(self.jwt, "job-123")

        self.assertEqual(result["status"], "pending")
        mock_request.assert_called_once()

    @patch.object(HTTPService, "request")
    def test_delete_import_job(self, mock_request):
        """Test deleting an import job."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "message": "Import job deleted successfully"
        }
        mock_request.return_value = mock_response

        result = self.service.delete_import_job(self.jwt, "job-123")

        self.assertIn("message", result)
        mock_request.assert_called_once()

    @patch.object(HTTPService, "request")
    def test_wait_for_import_job(self, mock_request):
        """Test waiting for an import job to complete."""
        # Simulate job progression
        responses = [
            Mock(status_code=200, json=lambda: {"job_id": "job-123", "status": "running"}),
            Mock(status_code=200, json=lambda: {"job_id": "job-123", "status": "running"}),
            Mock(status_code=200, json=lambda: {"job_id": "job-123", "status": "completed"}),
        ]
        mock_request.side_effect = responses

        result = self.service.wait_for_import_job(
            self.jwt, "job-123", poll_interval=0.1
        )

        self.assertEqual(result["status"], "completed")
        self.assertEqual(mock_request.call_count, 3)

    @patch.object(HTTPService, "request")
    def test_wait_for_import_job_timeout(self, mock_request):
        """Test waiting for an import job with timeout."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"job_id": "job-123", "status": "running"}
        mock_request.return_value = mock_response

        with self.assertRaises(TimeoutError):
            self.service.wait_for_import_job(
                self.jwt, "job-123", poll_interval=0.1, timeout=0.3
            )

    @patch("zededa_edgeai_sdk.services.import_jobs.requests.post")
    def test_create_import_job_with_upload_preserves_directory_structure(self, mock_post):
        """Test that create_import_job_with_upload preserves file structure."""
        mock_response = Mock()
        mock_response.status_code = 202
        mock_response.json.return_value = {"job_id": "job-456", "status": "pending"}
        mock_post.return_value = mock_response

        # Create a temporary directory with nested structure
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create nested structure: temp_dir/subdir1/file1.txt, temp_dir/subdir2/nested/file2.txt
            subdir1 = os.path.join(temp_dir, "subdir1")
            subdir2_nested = os.path.join(temp_dir, "subdir2", "nested")
            os.makedirs(subdir1)
            os.makedirs(subdir2_nested)
            
            file1_path = os.path.join(subdir1, "file1.txt")
            file2_path = os.path.join(subdir2_nested, "file2.txt")
            root_file = os.path.join(temp_dir, "model.bin")
            
            with open(file1_path, "w") as f:
                f.write("content1")
            with open(file2_path, "w") as f:
                f.write("content2")
            with open(root_file, "w") as f:
                f.write("model_content")
            
            # Call the method with the directory
            result = self.service.create_import_job_with_upload(
                self.jwt,
                provider_id="provider-123",
                catalog_id="catalog-456",
                model_name="test-model",
                file_paths=temp_dir,
                import_config={"model_version": "1.0"},
            )
            
            # Check that the post was called
            self.assertEqual(result["job_id"], "job-456")
            mock_post.assert_called_once()
            
            # Extract the files argument from the call
            call_kwargs = mock_post.call_args[1]
            files = call_kwargs["files"]
            
            # Get the file names from the files list
            # files is a list of tuples: ("files", (filename, file_handle, content_type))
            file_names = [f[1][0] for f in files]
            
            # Check that the directory structure is preserved
            # Files should have paths like "subdir1/file1.txt", not just "file1.txt"
            self.assertIn("subdir1/file1.txt", file_names)
            self.assertIn(os.path.join("subdir2", "nested", "file2.txt"), file_names)
            self.assertIn("model.bin", file_names)
            
            # Verify that flat names are NOT used (except for root file)
            flat_names = ["file1.txt", "file2.txt"]
            for flat_name in flat_names:
                if flat_name in file_names:
                    # This would indicate structure was lost
                    self.fail(f"Directory structure not preserved: {flat_name} should include path")

    @patch("zededa_edgeai_sdk.services.import_jobs.requests.post")
    def test_create_import_job_with_upload_single_file(self, mock_post):
        """Test that single file upload uses just the basename."""
        mock_response = Mock()
        mock_response.status_code = 202
        mock_response.json.return_value = {"job_id": "job-789", "status": "pending"}
        mock_post.return_value = mock_response

        with tempfile.NamedTemporaryFile(suffix=".pt", delete=False) as temp_file:
            temp_file.write(b"model content")
            temp_file_path = temp_file.name
        
        try:
            result = self.service.create_import_job_with_upload(
                self.jwt,
                provider_id="provider-123",
                catalog_id="catalog-456",
                model_name="test-model",
                file_paths=temp_file_path,
            )
            
            self.assertEqual(result["job_id"], "job-789")
            mock_post.assert_called_once()
            
            # Extract the files argument
            call_kwargs = mock_post.call_args[1]
            files = call_kwargs["files"]
            
            # For single file, should use just the basename
            file_names = [f[1][0] for f in files]
            self.assertEqual(len(file_names), 1)
            self.assertEqual(file_names[0], os.path.basename(temp_file_path))
        finally:
            os.unlink(temp_file_path)


if __name__ == "__main__":
    unittest.main()
