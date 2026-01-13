"""Unit tests for external provider CLI commands."""

import os
import unittest
from unittest.mock import Mock, patch

from zededa_edgeai_sdk.commands.external_providers import (
    execute_external_provider_list,
    execute_external_provider_create,
    execute_external_provider_get,
    execute_external_provider_update,
    execute_external_provider_delete,
    execute_test_connection,
    execute_browse_provider,
)
from zededa_edgeai_sdk.exceptions import AuthenticationError


class TestExternalProviderCommands(unittest.TestCase):
    """Test cases for external provider CLI commands."""

    def setUp(self):
        """Set up test fixtures."""
        self.service_url = "https://api.example.com"
        self.jwt_token = "test-jwt-token"

    @patch.dict(os.environ, {"EDGEAI_ACCESS_TOKEN": "test-jwt-token"})
    @patch("zededa_edgeai_sdk.commands.external_providers.ZededaEdgeAISDK")
    def test_execute_external_provider_list(self, mock_sdk_class):
        """Test listing external providers command."""
        mock_sdk = Mock()
        mock_sdk.external_providers.list_external_providers.return_value = {
            "providers": [{"id": "p1", "name": "Provider 1"}],
            "total": 1,
        }
        mock_sdk_class.return_value = mock_sdk

        result = execute_external_provider_list(
            limit=50, page=1, service_url=self.service_url, debug=False
        )

        self.assertEqual(result["total"], 1)
        mock_sdk.external_providers.list_external_providers.assert_called_once()

    @patch.dict(os.environ, {}, clear=True)
    def test_execute_external_provider_list_not_logged_in(self):
        """Test listing external providers without authentication."""
        with self.assertRaises(AuthenticationError):
            execute_external_provider_list(
                limit=50, page=1, service_url=self.service_url, debug=False
            )

    @patch.dict(os.environ, {"EDGEAI_ACCESS_TOKEN": "test-jwt-token"})
    @patch("zededa_edgeai_sdk.commands.external_providers.ZededaEdgeAISDK")
    def test_execute_external_provider_create(self, mock_sdk_class):
        """Test creating external provider command."""
        mock_sdk = Mock()
        mock_sdk.external_providers.create_external_provider.return_value = {
            "id": "p1",
            "name": "New Provider",
        }
        mock_sdk_class.return_value = mock_sdk

        result = execute_external_provider_create(
            "New Provider",
            "huggingface",
            url="https://huggingface.co",
            service_url=self.service_url,
            debug=False,
        )

        self.assertEqual(result["name"], "New Provider")
        mock_sdk.external_providers.create_external_provider.assert_called_once()

    @patch.dict(os.environ, {"EDGEAI_ACCESS_TOKEN": "test-jwt-token"})
    @patch("zededa_edgeai_sdk.commands.external_providers.ZededaEdgeAISDK")
    def test_execute_external_provider_get(self, mock_sdk_class):
        """Test getting external provider command by name."""
        mock_sdk = Mock()
        mock_sdk.external_providers.get_external_provider_by_name.return_value = {
            "id": "p1",
            "name": "Provider 1",
        }
        mock_sdk_class.return_value = mock_sdk

        result = execute_external_provider_get(
            "Provider 1", service_url=self.service_url, debug=False
        )

        self.assertEqual(result["id"], "p1")
        mock_sdk.external_providers.get_external_provider_by_name.assert_called_once()

    @patch.dict(os.environ, {"EDGEAI_ACCESS_TOKEN": "test-jwt-token"})
    @patch("zededa_edgeai_sdk.commands.external_providers.ZededaEdgeAISDK")
    def test_execute_external_provider_update(self, mock_sdk_class):
        """Test updating external provider command by name."""
        mock_sdk = Mock()
        mock_sdk.external_providers.update_external_provider.return_value = {
            "id": "p1",
            "name": "Updated Name",
        }
        mock_sdk_class.return_value = mock_sdk

        result = execute_external_provider_update(
            "Provider 1", name="Updated Name", service_url=self.service_url, debug=False
        )

        self.assertEqual(result["name"], "Updated Name")
        mock_sdk.external_providers.update_external_provider.assert_called_once()

    @patch.dict(os.environ, {"EDGEAI_ACCESS_TOKEN": "test-jwt-token"})
    @patch("zededa_edgeai_sdk.commands.external_providers.ZededaEdgeAISDK")
    def test_execute_external_provider_delete(self, mock_sdk_class):
        """Test deleting external provider command by name."""
        mock_sdk = Mock()
        mock_sdk.external_providers.delete_external_provider.return_value = True
        mock_sdk_class.return_value = mock_sdk

        result = execute_external_provider_delete(
            "Provider 1", service_url=self.service_url, debug=False
        )

        self.assertTrue(result["success"])
        mock_sdk.external_providers.delete_external_provider.assert_called_once()

    @patch.dict(os.environ, {"EDGEAI_ACCESS_TOKEN": "test-jwt-token"})
    @patch("zededa_edgeai_sdk.commands.external_providers.ZededaEdgeAISDK")
    def test_execute_test_connection(self, mock_sdk_class):
        """Test connection testing command by provider name."""
        mock_sdk = Mock()
        mock_sdk.external_providers.test_connection.return_value = {
            "success": True,
            "message": "Connection successful",
        }
        mock_sdk_class.return_value = mock_sdk

        result = execute_test_connection(
            "Provider 1", service_url=self.service_url, debug=False
        )

        self.assertTrue(result["success"])
        mock_sdk.external_providers.test_connection.assert_called_once()

    @patch.dict(os.environ, {"EDGEAI_ACCESS_TOKEN": "test-jwt-token"})
    @patch("zededa_edgeai_sdk.commands.external_providers.ZededaEdgeAISDK")
    def test_execute_browse_provider(self, mock_sdk_class):
        """Test browse provider command by provider name."""
        mock_sdk = Mock()
        mock_sdk.external_providers.browse_provider.return_value = {
            "items": [{"name": "model1"}],
            "cursor": None,
        }
        mock_sdk_class.return_value = mock_sdk

        result = execute_browse_provider(
            "Provider 1", path="/models", service_url=self.service_url, debug=False
        )

        self.assertEqual(len(result["items"]), 1)
        mock_sdk.external_providers.browse_provider.assert_called_once()


if __name__ == "__main__":
    unittest.main()
