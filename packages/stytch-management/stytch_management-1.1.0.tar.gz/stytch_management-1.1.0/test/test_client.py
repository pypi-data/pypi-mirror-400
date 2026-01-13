"""Unit tests for Client initialization."""

import unittest

from stytch_management import Client


class TestClient(unittest.TestCase):
    """Test Client initialization and configuration."""

    def test_create_client_with_valid_config(self):
        """Test that a client can be created with valid credentials."""
        client = Client(
            workspace_key_id="workspace-test-123",
            workspace_key_secret="secret-test-456",
        )

        self.assertIsNotNone(client)
        self.assertTrue(hasattr(client, "projects"))
        self.assertTrue(hasattr(client, "environments"))
        self.assertTrue(hasattr(client, "secrets"))

    def test_missing_workspace_key_id(self):
        """Test that ValueError is raised when workspace_key_id is missing."""
        with self.assertRaises(ValueError) as context:
            Client(
                workspace_key_id="",
                workspace_key_secret="secret-test-456",
            )
        self.assertIn('Missing "workspace_key_id"', str(context.exception))

    def test_missing_workspace_key_secret(self):
        """Test that ValueError is raised when workspace_key_secret is missing."""
        with self.assertRaises(ValueError) as context:
            Client(
                workspace_key_id="workspace-test-123",
                workspace_key_secret="",
            )
        self.assertIn('Missing "workspace_key_secret"', str(context.exception))

    def test_default_base_url(self):
        """Test that the default base URL is used if not provided."""
        client = Client(
            workspace_key_id="workspace-test-123",
            workspace_key_secret="secret-test-456",
        )

        # Access private attribute for testing
        self.assertEqual(client._http_client.base_url, "https://management.stytch.com/")

    def test_custom_base_url(self):
        """Test that a custom base URL can be provided."""
        custom_url = "https://custom.stytch.com"
        client = Client(
            workspace_key_id="workspace-test-123",
            workspace_key_secret="secret-test-456",
            base_url=custom_url,
        )

        # Access private attribute for testing
        self.assertEqual(client._http_client.base_url, f"{custom_url}/")

    def test_base_url_must_use_https(self):
        """Test that base_url must use HTTPS scheme."""
        with self.assertRaises(ValueError) as context:
            Client(
                workspace_key_id="workspace-test-123",
                workspace_key_secret="secret-test-456",
                base_url="http://insecure.com",
            )
        self.assertIn("base_url must use HTTPS scheme", str(context.exception))

    def test_base_url_gets_trailing_slash(self):
        """Test that base_url gets a trailing slash if missing."""
        client = Client(
            workspace_key_id="workspace-test-123",
            workspace_key_secret="secret-test-456",
            base_url="https://custom.stytch.com",
        )

        # Access private attribute for testing
        self.assertTrue(client._http_client.base_url.endswith("/"))

    def test_custom_timeout(self):
        """Test that a custom timeout can be provided."""
        client = Client(
            workspace_key_id="workspace-test-123",
            workspace_key_secret="secret-test-456",
            timeout=60,
        )

        # Access private attribute for testing
        self.assertEqual(client._http_client.timeout, 60)


if __name__ == "__main__":
    unittest.main()
