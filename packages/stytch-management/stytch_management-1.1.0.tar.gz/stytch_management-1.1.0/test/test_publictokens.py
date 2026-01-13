"""Integration tests for PublicTokens resource."""

import os
import unittest

from stytch_management import Client

WORKSPACE_KEY_ID = os.environ.get("STYTCH_WORKSPACE_KEY_ID")
WORKSPACE_KEY_SECRET = os.environ.get("STYTCH_WORKSPACE_KEY_SECRET")


@unittest.skipIf(
    not (WORKSPACE_KEY_ID and WORKSPACE_KEY_SECRET),
    "Integration tests require STYTCH_WORKSPACE_KEY_ID and STYTCH_WORKSPACE_KEY_SECRET",
)
class TestPublicTokensIntegration(unittest.TestCase):
    """Integration tests for PublicTokens resource."""

    @classmethod
    def setUpClass(cls):
        """Create a client and disposable project."""
        cls.client = Client(
            workspace_key_id=WORKSPACE_KEY_ID,
            workspace_key_secret=WORKSPACE_KEY_SECRET,
        )

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

        envs_resp = cls.client.environments.get_all(project_slug=cls.project_slug)
        test_env = next((e for e in envs_resp.environments if e.type == "TEST"), None)
        cls.environment_slug = test_env.environment_slug

    @classmethod
    def tearDownClass(cls):
        """Clean up the disposable project."""
        if hasattr(cls, "project_slug") and cls.project_slug:
            cls.client.projects.delete(project_slug=cls.project_slug)

    def test_create_public_token(self):
        """Test creating a public token."""
        response = self.client.public_tokens.create(
            project_slug=self.project_slug,
            environment_slug=self.environment_slug,
        )

        self.assertIsNotNone(response.public_token.public_token)
        self.assertGreater(len(response.public_token.public_token), 10)
        self.assertIsNotNone(response.public_token.created_at)

    def test_get_existing_public_token(self):
        """Test getting an existing public token."""
        create_resp = self.client.public_tokens.create(
            project_slug=self.project_slug,
            environment_slug=self.environment_slug,
        )

        response = self.client.public_tokens.get(
            project_slug=self.project_slug,
            environment_slug=self.environment_slug,
            public_token=create_resp.public_token.public_token,
        )

        self.assertEqual(response.public_token, create_resp.public_token)

    def test_get_with_missing_public_token(self):
        """Test that missing public token raises an error."""
        with self.assertRaises(Exception):
            self.client.public_tokens.get(
                project_slug=self.project_slug,
                environment_slug=self.environment_slug,
                public_token="",
            )

    def test_get_all_public_tokens(self):
        """Test getting all public tokens."""
        created_tokens = []
        for _ in range(3):
            create_resp = self.client.public_tokens.create(
                project_slug=self.project_slug,
                environment_slug=self.environment_slug,
            )
            created_tokens.append(create_resp.public_token)

        response = self.client.public_tokens.get_all(
            project_slug=self.project_slug,
            environment_slug=self.environment_slug,
        )

        self.assertGreaterEqual(len(response.public_tokens), 3)

        token_values = [t.public_token for t in response.public_tokens]
        for token in created_tokens:
            self.assertIn(token.public_token, token_values)
            found_token = next(
                (
                    t
                    for t in response.public_tokens
                    if t.public_token == token.public_token
                ),
                None,
            )
            self.assertIsNotNone(found_token.created_at)

    def test_delete_existing_public_token(self):
        """Test deleting an existing public token."""
        # Create 2 public tokens first (can't delete all tokens)
        create_resp = self.client.public_tokens.create(
            project_slug=self.project_slug,
            environment_slug=self.environment_slug,
        )
        self.client.public_tokens.create(
            project_slug=self.project_slug,
            environment_slug=self.environment_slug,
        )

        response = self.client.public_tokens.delete(
            project_slug=self.project_slug,
            environment_slug=self.environment_slug,
            public_token=create_resp.public_token.public_token,
        )

        self.assertIsNotNone(response.request_id)

        # Verify token is deleted
        get_all_resp = self.client.public_tokens.get_all(
            project_slug=self.project_slug,
            environment_slug=self.environment_slug,
        )

        token_values = [t.public_token for t in get_all_resp.public_tokens]
        self.assertNotIn(create_resp.public_token.public_token, token_values)

    def test_delete_public_token_does_not_exist(self):
        """Test that deleting a non-existent public token raises an error."""
        with self.assertRaises(Exception):
            self.client.public_tokens.delete(
                project_slug=self.project_slug,
                environment_slug=self.environment_slug,
                public_token="public-token-does-not-exist",
            )


if __name__ == "__main__":
    unittest.main()
