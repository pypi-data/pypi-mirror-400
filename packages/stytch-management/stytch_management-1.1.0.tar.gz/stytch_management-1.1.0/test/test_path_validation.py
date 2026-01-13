"""Tests for path parameter validation."""

import unittest

from stytch_management import Client
from stytch_management.errors import ClientError


class TestPathParameterValidation(unittest.TestCase):
    """Test that path parameters are validated before making API requests."""

    def setUp(self):
        """Create a test client before each test."""
        self.client = Client(
            workspace_key_id="workspace-test-123",
            workspace_key_secret="secret-test-456",
        )


class TestProjectsPathValidation(TestPathParameterValidation):
    """Test path validation for Projects resource."""

    def test_get_with_empty_project_slug(self):
        """Test that get() raises ClientError when project_slug is empty."""
        with self.assertRaises(ClientError) as context:
            self.client.projects.get(project_slug="")

        self.assertEqual(context.exception.code, "MISSING_PATH_PARAMETER")
        self.assertIn("project_slug cannot be empty", str(context.exception))

    def test_delete_with_empty_project_slug(self):
        """Test that delete() raises ClientError when project_slug is empty."""
        with self.assertRaises(ClientError) as context:
            self.client.projects.delete(project_slug="")

        self.assertEqual(context.exception.code, "MISSING_PATH_PARAMETER")
        self.assertIn("project_slug cannot be empty", str(context.exception))

    def test_update_with_empty_project_slug(self):
        """Test that update() raises ClientError when project_slug is empty."""
        with self.assertRaises(ClientError) as context:
            self.client.projects.update(project_slug="", name="Test")

        self.assertEqual(context.exception.code, "MISSING_PATH_PARAMETER")
        self.assertIn("project_slug cannot be empty", str(context.exception))


class TestSecretsPathValidation(TestPathParameterValidation):
    """Test path validation for Secrets resource."""

    def test_create_with_empty_project_slug(self):
        """Test that create() raises ClientError when project_slug is empty."""
        with self.assertRaises(ClientError) as context:
            self.client.secrets.create(project_slug="", environment_slug="test-env")

        self.assertEqual(context.exception.code, "MISSING_PATH_PARAMETER")
        self.assertIn("project_slug cannot be empty", str(context.exception))

    def test_create_with_empty_environment_slug(self):
        """Test that create() raises ClientError when environment_slug is empty."""
        with self.assertRaises(ClientError) as context:
            self.client.secrets.create(project_slug="test-project", environment_slug="")

        self.assertEqual(context.exception.code, "MISSING_PATH_PARAMETER")
        self.assertIn("environment_slug cannot be empty", str(context.exception))


class TestEnvironmentsPathValidation(TestPathParameterValidation):
    """Test path validation for Environments resource."""

    def test_get_all_with_empty_project_slug(self):
        """Test that get_all() raises ClientError when project_slug is empty."""
        with self.assertRaises(ClientError) as context:
            self.client.environments.get_all(project_slug="")

        self.assertEqual(context.exception.code, "MISSING_PATH_PARAMETER")
        self.assertIn("project_slug cannot be empty", str(context.exception))

    def test_get_with_empty_project_slug(self):
        """Test that get() raises ClientError when project_slug is empty."""
        with self.assertRaises(ClientError) as context:
            self.client.environments.get(project_slug="", environment_slug="test-env")

        self.assertEqual(context.exception.code, "MISSING_PATH_PARAMETER")
        self.assertIn("project_slug cannot be empty", str(context.exception))

    def test_get_with_empty_environment_slug(self):
        """Test that get() raises ClientError when environment_slug is empty."""
        with self.assertRaises(ClientError) as context:
            self.client.environments.get(
                project_slug="test-project", environment_slug=""
            )

        self.assertEqual(context.exception.code, "MISSING_PATH_PARAMETER")
        self.assertIn("environment_slug cannot be empty", str(context.exception))


if __name__ == "__main__":
    unittest.main()
