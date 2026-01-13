"""Integration tests for RedirectURLs resource."""

import os
import unittest

from stytch_management import Client

WORKSPACE_KEY_ID = os.environ.get("STYTCH_WORKSPACE_KEY_ID")
WORKSPACE_KEY_SECRET = os.environ.get("STYTCH_WORKSPACE_KEY_SECRET")

TEST_REDIRECT_URL_1 = "https://localhost:3000/callback"
TEST_REDIRECT_URL_2 = "https://localhost:3001/auth/callback"
TEST_REDIRECT_URL_3 = "https://localhost:3002/login"


@unittest.skipIf(
    not (WORKSPACE_KEY_ID and WORKSPACE_KEY_SECRET),
    "Integration tests require STYTCH_WORKSPACE_KEY_ID and STYTCH_WORKSPACE_KEY_SECRET",
)
class TestRedirectURLsIntegration(unittest.TestCase):
    """Integration tests for RedirectURLs resource."""

    @classmethod
    def setUpClass(cls):
        """Create a client and disposable project."""
        cls.client = Client(
            workspace_key_id=WORKSPACE_KEY_ID,
            workspace_key_secret=WORKSPACE_KEY_SECRET,
        )

        create_project_resp = cls.client.projects.create(
            name="Disposable B2B Project", vertical="B2B"
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

    def test_create_redirect_url_with_single_type(self):
        """Test creating a redirect URL with single type."""
        response = self.client.redirect_urls.create(
            project_slug=self.project_slug,
            environment_slug=self.environment_slug,
            url=TEST_REDIRECT_URL_1,
            valid_types=[{"type": "LOGIN", "is_default": True}],
            do_not_promote_defaults=False,
        )

        self.assertEqual(response.redirect_url.url, TEST_REDIRECT_URL_1)
        self.assertEqual(len(response.redirect_url.valid_types), 1)
        self.assertEqual(response.redirect_url.valid_types[0].type, "LOGIN")
        self.assertTrue(response.redirect_url.valid_types[0].is_default)

    def test_create_redirect_url_with_multiple_types(self):
        """Test creating a redirect URL with multiple types."""
        response = self.client.redirect_urls.create(
            project_slug=self.project_slug,
            environment_slug=self.environment_slug,
            url=TEST_REDIRECT_URL_2,
            valid_types=[
                {"type": "LOGIN", "is_default": True},
                {"type": "SIGNUP", "is_default": False},
                {"type": "INVITE", "is_default": True},
            ],
            do_not_promote_defaults=False,
        )

        self.assertEqual(response.redirect_url.url, TEST_REDIRECT_URL_2)
        self.assertEqual(len(response.redirect_url.valid_types), 3)

        type_map = {t.type: t.is_default for t in response.redirect_url.valid_types}
        self.assertIn("LOGIN", type_map)
        self.assertIn("SIGNUP", type_map)
        self.assertIn("INVITE", type_map)

    def test_create_redirect_url_with_do_not_promote_defaults(self):
        """Test creating a redirect URL with do not promote defaults."""
        response = self.client.redirect_urls.create(
            project_slug=self.project_slug,
            environment_slug=self.environment_slug,
            url=TEST_REDIRECT_URL_3,
            valid_types=[{"type": "RESET_PASSWORD", "is_default": False}],
            do_not_promote_defaults=True,
        )

        self.assertEqual(response.redirect_url.url, TEST_REDIRECT_URL_3)
        self.assertEqual(len(response.redirect_url.valid_types), 1)
        self.assertEqual(response.redirect_url.valid_types[0].type, "RESET_PASSWORD")

    def test_create_duplicate_redirect_url(self):
        """Test handling duplicate redirect URL."""
        duplicate_url = "https://duplicate.example.com/callback"

        # Create first redirect URL
        self.client.redirect_urls.create(
            project_slug=self.project_slug,
            environment_slug=self.environment_slug,
            url=duplicate_url,
            valid_types=[{"type": "LOGIN", "is_default": True}],
        )

        # Create the same URL again - should update
        self.client.redirect_urls.create(
            project_slug=self.project_slug,
            environment_slug=self.environment_slug,
            url=duplicate_url,
            valid_types=[{"type": "SIGNUP", "is_default": True}],
        )

        get_resp = self.client.redirect_urls.get(
            project_slug=self.project_slug,
            environment_slug=self.environment_slug,
            url=duplicate_url,
        )

        self.assertEqual(len(get_resp.redirect_url.valid_types), 2)

    def test_get_all_redirect_urls(self):
        """Test getting all redirect URLs."""
        url1 = "https://getall1.example.com/callback"
        url2 = "https://getall2.example.com/callback"

        self.client.redirect_urls.create(
            project_slug=self.project_slug,
            environment_slug=self.environment_slug,
            url=url1,
            valid_types=[{"type": "LOGIN", "is_default": True}],
        )

        self.client.redirect_urls.create(
            project_slug=self.project_slug,
            environment_slug=self.environment_slug,
            url=url2,
            valid_types=[{"type": "SIGNUP", "is_default": True}],
        )

        response = self.client.redirect_urls.get_all(
            project_slug=self.project_slug,
            environment_slug=self.environment_slug,
        )

        self.assertGreaterEqual(len(response.redirect_urls), 2)

        url_map = {r.url: True for r in response.redirect_urls}
        self.assertIn(url1, url_map)
        self.assertIn(url2, url_map)

    def test_get_all_redirect_urls(self):
        """Test getting all redirect URLs."""
        response = self.client.redirect_urls.get_all(
            project_slug=self.project_slug,
            environment_slug=self.environment_slug,
        )

        self.assertIsNotNone(response.redirect_urls)
        self.assertIsInstance(response.redirect_urls, list)

    def test_get_existing_redirect_url(self):
        """Test getting an existing redirect URL."""
        get_url = "https://get.example.com/callback"

        create_resp = self.client.redirect_urls.create(
            project_slug=self.project_slug,
            environment_slug=self.environment_slug,
            url=get_url,
            valid_types=[{"type": "LOGIN", "is_default": True}],
        )

        response = self.client.redirect_urls.get(
            project_slug=self.project_slug,
            environment_slug=self.environment_slug,
            url=get_url,
        )

        self.assertEqual(response.redirect_url.url, create_resp.redirect_url.url)
        self.assertEqual(len(response.redirect_url.valid_types), 1)

        type_map = {t.type: t.is_default for t in response.redirect_url.valid_types}
        self.assertIn("LOGIN", type_map)
        self.assertTrue(type_map["LOGIN"])

    def test_get_existing_redirect_url_using_query_params(self):
        """Test getting an existing redirect URL using query params."""
        url_with_query_params = "https://localhost:3002/login?expires_at={}"

        self.client.redirect_urls.create(
            project_slug=self.project_slug,
            environment_slug=self.environment_slug,
            url=url_with_query_params,
            valid_types=[{"type": "INVITE", "is_default": False}],
        )

        response = self.client.redirect_urls.get(
            project_slug=self.project_slug,
            environment_slug=self.environment_slug,
            url=url_with_query_params,
        )

        self.assertEqual(response.redirect_url.url, url_with_query_params)
        self.assertEqual(len(response.redirect_url.valid_types), 1)

    def test_get_non_existent_redirect_url(self):
        """Test that getting a non-existent redirect URL raises an error."""
        with self.assertRaises(Exception):
            self.client.redirect_urls.get(
                project_slug=self.project_slug,
                environment_slug=self.environment_slug,
                url="https://nonexistent.example.com/callback",
            )

    def test_update_redirect_url_valid_types(self):
        """Test updating redirect URL valid types."""
        update_url = "https://update.example.com/callback"

        self.client.redirect_urls.create(
            project_slug=self.project_slug,
            environment_slug=self.environment_slug,
            url=update_url,
            valid_types=[{"type": "LOGIN", "is_default": True}],
        )

        response = self.client.redirect_urls.update(
            project_slug=self.project_slug,
            environment_slug=self.environment_slug,
            url=update_url,
            valid_types=[
                {"type": "LOGIN", "is_default": True},
                {"type": "SIGNUP", "is_default": True},
                {"type": "RESET_PASSWORD", "is_default": False},
            ],
            do_not_promote_defaults=False,
        )

        self.assertEqual(response.redirect_url.url, update_url)
        self.assertEqual(len(response.redirect_url.valid_types), 3)

        type_map = {t.type: t.is_default for t in response.redirect_url.valid_types}
        self.assertIn("LOGIN", type_map)
        self.assertIn("SIGNUP", type_map)
        self.assertIn("RESET_PASSWORD", type_map)

    def test_update_non_existent_redirect_url(self):
        """Test that updating a non-existent redirect URL raises an error."""
        with self.assertRaises(Exception):
            self.client.redirect_urls.update(
                project_slug=self.project_slug,
                environment_slug=self.environment_slug,
                url="https://nonexistent-update.example.com/callback",
                valid_types=[{"type": "LOGIN", "is_default": True}],
            )

    def test_delete_existing_redirect_url(self):
        """Test deleting an existing redirect URL."""
        delete_url = "https://delete.example.com/callback"

        self.client.redirect_urls.create(
            project_slug=self.project_slug,
            environment_slug=self.environment_slug,
            url=delete_url,
            valid_types=[{"type": "LOGIN", "is_default": True}],
        )

        response = self.client.redirect_urls.delete(
            project_slug=self.project_slug,
            environment_slug=self.environment_slug,
            url=delete_url,
            do_not_promote_defaults=False,
        )

        self.assertIsNotNone(response)

        # Verify deletion
        with self.assertRaises(Exception):
            self.client.redirect_urls.get(
                project_slug=self.project_slug,
                environment_slug=self.environment_slug,
                url=delete_url,
            )

    def test_delete_non_existent_redirect_url(self):
        """Test that deleting a non-existent redirect URL raises an error."""
        with self.assertRaises(Exception):
            self.client.redirect_urls.delete(
                project_slug=self.project_slug,
                environment_slug=self.environment_slug,
                url="https://nonexistent-delete.example.com/callback",
            )


if __name__ == "__main__":
    unittest.main()
