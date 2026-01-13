"""Unit tests for ExternalProviderService."""

import unittest
from unittest.mock import Mock, patch

from zededa_edgeai_sdk.services.external_providers import ExternalProviderService
from zededa_edgeai_sdk.services.http import HTTPService


class TestExternalProviderService(unittest.TestCase):
    """Test cases for ExternalProviderService."""

    def setUp(self):
        """Set up test fixtures."""
        self.backend_url = "https://api.example.com"
        self.http = HTTPService(debug=False)
        self.service = ExternalProviderService(self.backend_url, self.http)
        self.jwt = "test-jwt-token"

    @patch.object(HTTPService, "request")
    def test_list_external_providers(self, mock_request):
        """Test listing external providers with pagination."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "providers": [
                {"id": "provider-1", "name": "HuggingFace", "type": "huggingface"},
                {"id": "provider-2", "name": "Azure", "type": "azure"},
            ],
            "total": 2,
            "page": 1,
            "limit": 50,
        }
        mock_request.return_value = mock_response

        result = self.service.list_external_providers(
            self.jwt, limit=50, page=1, search="hugging"
        )

        self.assertEqual(len(result["providers"]), 2)
        self.assertEqual(result["total"], 2)
        mock_request.assert_called_once()

    @patch.object(HTTPService, "request")
    def test_create_external_provider(self, mock_request):
        """Test creating a new external provider."""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "id": "provider-123",
            "name": "My HuggingFace",
            "type": "huggingface",
            "url": "https://huggingface.co",
        }
        mock_request.return_value = mock_response

        payload = {
            "name": "My HuggingFace",
            "type": "huggingface",
            "url": "https://huggingface.co",
        }
        result = self.service.create_external_provider(self.jwt, payload)

        self.assertEqual(result["id"], "provider-123")
        self.assertEqual(result["name"], "My HuggingFace")
        mock_request.assert_called_once()

    @patch.object(HTTPService, "request")
    def test_get_external_provider(self, mock_request):
        """Test getting a specific external provider."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "provider-123",
            "name": "My Provider",
            "type": "azure",
        }
        mock_request.return_value = mock_response

        result = self.service.get_external_provider(self.jwt, "provider-123")

        self.assertEqual(result["id"], "provider-123")
        self.assertEqual(result["name"], "My Provider")
        mock_request.assert_called_once()

    @patch.object(HTTPService, "request")
    def test_get_external_provider_not_found(self, mock_request):
        """Test getting a non-existent external provider."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_request.return_value = mock_response

        result = self.service.get_external_provider(self.jwt, "nonexistent")

        self.assertEqual(result, {})
        mock_request.assert_called_once()

    @patch.object(HTTPService, "request")
    def test_update_external_provider(self, mock_request):
        """Test updating an external provider by name."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "provider-123",
            "name": "Updated Name",
            "type": "azure",
        }
        mock_request.return_value = mock_response

        payload = {"name": "Updated Name"}
        result = self.service.update_external_provider(
            self.jwt, "My Provider", payload
        )

        self.assertEqual(result["name"], "Updated Name")
        mock_request.assert_called_once()

    @patch.object(HTTPService, "request")
    def test_delete_external_provider(self, mock_request):
        """Test deleting an external provider by name."""
        mock_response = Mock()
        mock_response.status_code = 204
        mock_request.return_value = mock_response

        result = self.service.delete_external_provider(self.jwt, "My Provider")

        self.assertTrue(result)
        mock_request.assert_called_once()

    @patch.object(HTTPService, "request")
    def test_delete_external_provider_not_found(self, mock_request):
        """Test deleting a non-existent external provider by name."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_request.return_value = mock_response

        result = self.service.delete_external_provider(self.jwt, "nonexistent")

        self.assertFalse(result)
        mock_request.assert_called_once()

    @patch.object(HTTPService, "request")
    def test_test_connection(self, mock_request):
        """Test testing provider connection by name."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "message": "Connection successful",
        }
        mock_request.return_value = mock_response

        result = self.service.test_connection(self.jwt, "My Provider")

        self.assertTrue(result["success"])
        self.assertEqual(result["message"], "Connection successful")
        mock_request.assert_called_once()

    @patch.object(HTTPService, "request")
    def test_browse_provider(self, mock_request):
        """Test browsing provider contents by name."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [
                {"name": "model1", "type": "model"},
                {"name": "model2", "type": "model"},
            ],
            "cursor": "next-page-token",
        }
        mock_request.return_value = mock_response

        result = self.service.browse_provider(
            self.jwt, "My Provider", path="/models", search="yolo"
        )

        self.assertEqual(len(result["items"]), 2)
        self.assertEqual(result["cursor"], "next-page-token")
        mock_request.assert_called_once()


if __name__ == "__main__":
    unittest.main()
