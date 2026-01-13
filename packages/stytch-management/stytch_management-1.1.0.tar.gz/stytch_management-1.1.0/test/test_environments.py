"""Integration tests for Environments resource."""

import os
import unittest

from stytch_management import Client

WORKSPACE_KEY_ID = os.environ.get("STYTCH_WORKSPACE_KEY_ID")
WORKSPACE_KEY_SECRET = os.environ.get("STYTCH_WORKSPACE_KEY_SECRET")


@unittest.skipIf(
    not (WORKSPACE_KEY_ID and WORKSPACE_KEY_SECRET),
    "Integration tests require STYTCH_WORKSPACE_KEY_ID and STYTCH_WORKSPACE_KEY_SECRET",
)
class TestEnvironmentsIntegration(unittest.TestCase):
    """Integration tests for Environments resource."""

    @classmethod
    def setUpClass(cls):
        """Create a client and disposable projects."""
        cls.client = Client(
            workspace_key_id=WORKSPACE_KEY_ID,
            workspace_key_secret=WORKSPACE_KEY_SECRET,
        )

        # Create B2B project
        b2b_resp = cls.client.projects.create(
            name="Disposable B2B Project", vertical="B2B"
        )
        cls.b2b_project_slug = b2b_resp.project.project_slug

        # Create live environment first (required by API)
        cls.client.environments.create(
            project_slug=cls.b2b_project_slug,
            name="production",
            type="LIVE",
            environment_slug="production",
        )

        # Create Consumer project
        consumer_resp = cls.client.projects.create(
            name="Disposable Consumer Project", vertical="CONSUMER"
        )
        cls.consumer_project_slug = consumer_resp.project.project_slug

        # Create live environment first (required by API)
        cls.client.environments.create(
            project_slug=cls.consumer_project_slug,
            name="production",
            type="LIVE",
            environment_slug="production",
        )

    @classmethod
    def tearDownClass(cls):
        """Clean up the disposable projects."""
        if hasattr(cls, "b2b_project_slug") and cls.b2b_project_slug:
            cls.client.projects.delete(project_slug=cls.b2b_project_slug)
        if hasattr(cls, "consumer_project_slug") and cls.consumer_project_slug:
            cls.client.projects.delete(project_slug=cls.consumer_project_slug)

    def test_create_environment_base_case(self):
        """Test creating an environment with base case."""
        slug = "custom-slug"
        zero_downtime_url = "https://example.com/migration"

        response = self.client.environments.create(
            project_slug=self.b2b_project_slug,
            name="Test Environment",
            type="TEST",
            environment_slug=slug,
            cross_org_passwords_enabled=True,
            user_impersonation_enabled=True,
            zero_downtime_session_migration_url=zero_downtime_url,
        )

        self.assertEqual(response.environment.name, "Test Environment")
        self.assertEqual(response.environment.type, "TEST")
        self.assertEqual(response.environment.environment_slug, slug)
        self.assertTrue(response.environment.cross_org_passwords_enabled)
        self.assertTrue(response.environment.user_impersonation_enabled)
        self.assertEqual(
            response.environment.zero_downtime_session_migration_url, zero_downtime_url
        )

    def test_create_environment_user_locking_fields(self):
        """Test creating an environment with user locking fields."""
        response = self.client.environments.create(
            project_slug=self.b2b_project_slug,
            name="Test Environment",
            type="TEST",
            user_lock_self_serve_enabled=True,
            user_lock_threshold=5,
            user_lock_ttl=600,
        )

        self.assertEqual(response.environment.name, "Test Environment")
        self.assertEqual(response.environment.type, "TEST")
        self.assertTrue(response.environment.user_lock_self_serve_enabled)
        self.assertEqual(response.environment.user_lock_threshold, 5)
        self.assertEqual(response.environment.user_lock_ttl, 600)

    def test_create_environment_idp_fields(self):
        """Test creating an environment with IDP fields."""
        idp_auth_url = "https://example.com/idp"
        idp_template_content = '{"field": {{ user.user_id }} }'

        response = self.client.environments.create(
            project_slug=self.consumer_project_slug,
            name="Test Environment",
            type="TEST",
            idp_authorization_url=idp_auth_url,
            idp_dynamic_client_registration_enabled=True,
            idp_dynamic_client_registration_access_token_template_content=idp_template_content,
        )

        self.assertEqual(response.environment.name, "Test Environment")
        self.assertEqual(response.environment.type, "TEST")
        self.assertEqual(response.environment.idp_authorization_url, idp_auth_url)
        self.assertTrue(response.environment.idp_dynamic_client_registration_enabled)
        self.assertEqual(
            response.environment.idp_dynamic_client_registration_access_token_template_content,
            idp_template_content,
        )

    def test_get_existing_environment(self):
        """Test getting an existing environment."""
        # Get all environments
        all_resp = self.client.environments.get_all(project_slug=self.b2b_project_slug)
        env = next((e for e in all_resp.environments if e.type == "LIVE"), None)

        response = self.client.environments.get(
            project_slug=self.b2b_project_slug,
            environment_slug=env.environment_slug,
        )

        self.assertEqual(response.environment.environment_slug, env.environment_slug)

    def test_get_environment_does_not_exist(self):
        """Test that getting a non-existent environment raises an error."""
        with self.assertRaises(Exception):
            self.client.environments.get(
                project_slug=self.b2b_project_slug,
                environment_slug="nonexistent-environment",
            )

    def test_get_with_missing_environment_slug(self):
        """Test that missing environment slug raises an error."""
        with self.assertRaises(Exception):
            self.client.environments.get(
                project_slug=self.b2b_project_slug, environment_slug=""
            )

    def test_get_all_environments(self):
        """Test getting all environments."""
        create_resp = self.client.environments.create(
            project_slug=self.b2b_project_slug,
            name="Another Test Environment",
            type="TEST",
        )

        response = self.client.environments.get_all(project_slug=self.b2b_project_slug)

        # Should have at least live + test environment
        self.assertGreaterEqual(len(response.environments), 2)

        env_slugs = [e.environment_slug for e in response.environments]
        self.assertIn(create_resp.environment.environment_slug, env_slugs)

    def test_update_environment_base_case(self):
        """Test updating an environment with base case."""
        # Create test environment
        create_resp = self.client.environments.create(
            project_slug=self.b2b_project_slug,
            name="Test Environment",
            type="TEST",
        )

        new_name = "Updated Environment Name"
        zero_downtime_url = "https://example.com/migration"

        response = self.client.environments.update(
            project_slug=self.b2b_project_slug,
            environment_slug=create_resp.environment.environment_slug,
            name=new_name,
            cross_org_passwords_enabled=True,
            user_impersonation_enabled=True,
            zero_downtime_session_migration_url=zero_downtime_url,
        )

        self.assertEqual(response.environment.name, new_name)
        self.assertTrue(response.environment.cross_org_passwords_enabled)
        self.assertTrue(response.environment.user_impersonation_enabled)
        self.assertEqual(
            response.environment.zero_downtime_session_migration_url, zero_downtime_url
        )

    def test_update_environment_user_locking_fields(self):
        """Test updating an environment with user locking fields."""
        create_resp = self.client.environments.create(
            project_slug=self.b2b_project_slug,
            name="Test Environment",
            type="TEST",
        )

        response = self.client.environments.update(
            project_slug=self.b2b_project_slug,
            environment_slug=create_resp.environment.environment_slug,
            user_lock_self_serve_enabled=True,
            user_lock_threshold=5,
            user_lock_ttl=600,
        )

        self.assertTrue(response.environment.user_lock_self_serve_enabled)
        self.assertEqual(response.environment.user_lock_threshold, 5)
        self.assertEqual(response.environment.user_lock_ttl, 600)

    def test_update_environment_idp_fields(self):
        """Test updating an environment with IDP fields."""
        create_resp = self.client.environments.create(
            project_slug=self.consumer_project_slug,
            name="Test Environment",
            type="TEST",
        )

        idp_auth_url = "https://example.com/idp"
        idp_template_content = '{"field": {{ user.user_id }} }'

        response = self.client.environments.update(
            project_slug=self.consumer_project_slug,
            environment_slug=create_resp.environment.environment_slug,
            idp_authorization_url=idp_auth_url,
            idp_dynamic_client_registration_enabled=True,
            idp_dynamic_client_registration_access_token_template_content=idp_template_content,
        )

        self.assertEqual(response.environment.idp_authorization_url, idp_auth_url)
        self.assertTrue(response.environment.idp_dynamic_client_registration_enabled)
        self.assertEqual(
            response.environment.idp_dynamic_client_registration_access_token_template_content,
            idp_template_content,
        )

    def test_update_does_not_overwrite_existing_values(self):
        """Test that update does not overwrite existing values."""
        create_resp = self.client.environments.create(
            project_slug=self.b2b_project_slug,
            name="Test Environment",
            type="TEST",
        )

        # First update
        self.client.environments.update(
            project_slug=self.b2b_project_slug,
            environment_slug=create_resp.environment.environment_slug,
            cross_org_passwords_enabled=True,
            user_impersonation_enabled=True,
        )

        # Second update with only name
        new_name = "Updated Environment Name"
        response = self.client.environments.update(
            project_slug=self.b2b_project_slug,
            environment_slug=create_resp.environment.environment_slug,
            name=new_name,
        )

        # Other values should remain
        self.assertEqual(response.environment.name, new_name)
        self.assertTrue(response.environment.cross_org_passwords_enabled)
        self.assertTrue(response.environment.user_impersonation_enabled)

    def test_delete_environment(self):
        """Test deleting an environment."""
        create_resp = self.client.environments.create(
            project_slug=self.b2b_project_slug,
            name="Test Environment",
            type="TEST",
        )

        self.client.environments.delete(
            project_slug=self.b2b_project_slug,
            environment_slug=create_resp.environment.environment_slug,
        )

        # Verify deletion
        with self.assertRaises(Exception):
            self.client.environments.get(
                project_slug=self.b2b_project_slug,
                environment_slug=create_resp.environment.environment_slug,
            )


if __name__ == "__main__":
    unittest.main()
