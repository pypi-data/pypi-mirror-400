"""Integration tests for Secrets resource.

These tests require real API credentials and are skipped by default.
Set STYTCH_WORKSPACE_KEY_ID and STYTCH_WORKSPACE_KEY_SECRET to run them.
"""

import os
import unittest

from stytch_management import Client

# Get credentials from environment
WORKSPACE_KEY_ID = os.environ.get("STYTCH_WORKSPACE_KEY_ID")
WORKSPACE_KEY_SECRET = os.environ.get("STYTCH_WORKSPACE_KEY_SECRET")


@unittest.skipIf(
    not (WORKSPACE_KEY_ID and WORKSPACE_KEY_SECRET),
    "Integration tests require STYTCH_WORKSPACE_KEY_ID and STYTCH_WORKSPACE_KEY_SECRET",
)
class TestSecretsIntegration(unittest.TestCase):
    """Integration tests for Secrets resource."""

    @classmethod
    def setUpClass(cls):
        """Create a client and disposable project."""
        cls.client = Client(
            workspace_key_id=WORKSPACE_KEY_ID,
            workspace_key_secret=WORKSPACE_KEY_SECRET,
        )

        # Create a disposable Consumer project
        create_project_resp = cls.client.projects.create(
            name="Disposable Project", vertical="CONSUMER"
        )
        cls.project_slug = create_project_resp.project.project_slug

        # Create live environment first (required by API)
        cls.client.environments.create(
            project_slug=cls.project_slug,
            name="production",
            type="LIVE",
            environment_slug="production",
        )

        # Create test environment
        cls.client.environments.create(
            project_slug=cls.project_slug,
            name="test",
            type="TEST",
            environment_slug="test",
        )

        # Get test environment slug
        envs_resp = cls.client.environments.get_all(project_slug=cls.project_slug)
        test_env = next((e for e in envs_resp.environments if e.type == "TEST"), None)
        cls.environment_slug = test_env.environment_slug

    @classmethod
    def tearDownClass(cls):
        """Clean up the disposable project."""
        if hasattr(cls, "project_slug") and cls.project_slug:
            cls.client.projects.delete(project_slug=cls.project_slug)

    def test_create_secret(self):
        """Test creating a secret."""
        response = self.client.secrets.create(
            project_slug=self.project_slug,
            environment_slug=self.environment_slug,
        )

        self.assertIsNotNone(response.secret.secret_id)
        self.assertIsNotNone(response.secret.secret)
        self.assertGreater(len(response.secret.secret), 10)
        self.assertIsNotNone(response.secret.created_at)

    def test_get_existing_secret(self):
        """Test getting an existing secret."""
        # Create a secret first
        create_resp = self.client.secrets.create(
            project_slug=self.project_slug,
            environment_slug=self.environment_slug,
        )

        # Get secret
        response = self.client.secrets.get(
            project_slug=self.project_slug,
            environment_slug=self.environment_slug,
            secret_id=create_resp.secret.secret_id,
        )

        self.assertEqual(response.secret.secret_id, create_resp.secret.secret_id)
        self.assertIsNotNone(response.secret.last_four)
        self.assertIsNotNone(response.secret.created_at)
        self.assertEqual(response.secret.last_four, create_resp.secret.secret[-4:])
        self.assertEqual(response.secret.created_at, create_resp.secret.created_at)

    def test_get_secret_does_not_exist(self):
        """Test that getting a non-existent secret raises an error."""
        with self.assertRaises(Exception):
            self.client.secrets.get(
                project_slug=self.project_slug,
                environment_slug=self.environment_slug,
                secret_id="secret-does-not-exist",
            )

    def test_get_with_missing_secret_id(self):
        """Test that missing secret ID raises an error."""
        with self.assertRaises(Exception):
            self.client.secrets.get(
                project_slug=self.project_slug,
                environment_slug=self.environment_slug,
                secret_id="",
            )

    def test_get_all_secrets(self):
        """Test getting all secrets."""
        # Create a few secrets first
        created_secrets = []
        for _ in range(3):
            create_resp = self.client.secrets.create(
                project_slug=self.project_slug,
                environment_slug=self.environment_slug,
            )
            created_secrets.append(create_resp.secret)

        # Get all secrets
        response = self.client.secrets.get_all(
            project_slug=self.project_slug,
            environment_slug=self.environment_slug,
        )

        self.assertGreaterEqual(len(response.secrets), 3)

        # Verify all created secrets are returned
        secret_ids = [s.secret_id for s in response.secrets]
        for secret in created_secrets:
            self.assertIn(secret.secret_id, secret_ids)
            found_secret = next(
                (s for s in response.secrets if s.secret_id == secret.secret_id), None
            )
            self.assertIsNotNone(found_secret.last_four)
            self.assertIsNotNone(found_secret.created_at)

    def test_delete_existing_secret(self):
        """Test deleting an existing secret."""
        # Create a secret first
        create_resp = self.client.secrets.create(
            project_slug=self.project_slug,
            environment_slug=self.environment_slug,
        )

        # Delete secret
        response = self.client.secrets.delete(
            project_slug=self.project_slug,
            environment_slug=self.environment_slug,
            secret_id=create_resp.secret.secret_id,
        )

        self.assertIsNotNone(response.request_id)

        # Verify secret is deleted
        with self.assertRaises(Exception):
            self.client.secrets.get(
                project_slug=self.project_slug,
                environment_slug=self.environment_slug,
                secret_id=create_resp.secret.secret_id,
            )

    def test_delete_secret_does_not_exist(self):
        """Test that deleting a non-existent secret raises an error."""
        with self.assertRaises(Exception):
            self.client.secrets.delete(
                project_slug=self.project_slug,
                environment_slug=self.environment_slug,
                secret_id="secret-does-not-exist",
            )


if __name__ == "__main__":
    unittest.main()
