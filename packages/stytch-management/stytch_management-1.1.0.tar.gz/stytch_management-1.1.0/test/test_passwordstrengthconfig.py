"""Integration tests for PasswordStrengthConfig resource."""

import os
import unittest

from stytch_management import Client

WORKSPACE_KEY_ID = os.environ.get("STYTCH_WORKSPACE_KEY_ID")
WORKSPACE_KEY_SECRET = os.environ.get("STYTCH_WORKSPACE_KEY_SECRET")


@unittest.skipIf(
    not (WORKSPACE_KEY_ID and WORKSPACE_KEY_SECRET),
    "Integration tests require STYTCH_WORKSPACE_KEY_ID and STYTCH_WORKSPACE_KEY_SECRET",
)
class TestPasswordStrengthConfigIntegration(unittest.TestCase):
    """Integration tests for PasswordStrengthConfig resource."""

    @classmethod
    def setUpClass(cls):
        """Create a client and disposable project."""
        cls.client = Client(
            workspace_key_id=WORKSPACE_KEY_ID,
            workspace_key_secret=WORKSPACE_KEY_SECRET,
        )

        create_project_resp = cls.client.projects.create(
            name="Disposable Consumer Project", vertical="CONSUMER"
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

    def test_get_password_strength_config(self):
        """Test getting password strength config."""
        response = self.client.password_strength_config.get(
            project_slug=self.project_slug,
            environment_slug=self.environment_slug,
        )

        self.assertIsNotNone(response.request_id)
        self.assertIsNotNone(response.password_strength_config.validation_policy)

    def test_set_password_strength_config_with_luds_policy(self):
        """Test setting password strength config with LUDS policy."""
        response = self.client.password_strength_config.set(
            project_slug=self.project_slug,
            environment_slug=self.environment_slug,
            check_breach_on_creation=True,
            check_breach_on_authentication=True,
            validate_on_authentication=True,
            validation_policy="LUDS",
            luds_min_password_length=10,
            luds_min_password_complexity=3,
        )

        self.assertTrue(response.password_strength_config.check_breach_on_creation)
        self.assertTrue(
            response.password_strength_config.check_breach_on_authentication
        )
        self.assertTrue(response.password_strength_config.validate_on_authentication)
        self.assertEqual(response.password_strength_config.validation_policy, "LUDS")
        self.assertEqual(response.password_strength_config.luds_min_password_length, 10)
        self.assertEqual(
            response.password_strength_config.luds_min_password_complexity, 3
        )

    def test_set_password_strength_config_with_zxcvbn_policy(self):
        """Test setting password strength config with ZXCVBN policy."""
        response = self.client.password_strength_config.set(
            project_slug=self.project_slug,
            environment_slug=self.environment_slug,
            check_breach_on_creation=False,
            check_breach_on_authentication=False,
            validate_on_authentication=False,
            validation_policy="ZXCVBN",
        )

        self.assertFalse(response.password_strength_config.check_breach_on_creation)
        self.assertFalse(
            response.password_strength_config.check_breach_on_authentication
        )
        self.assertFalse(response.password_strength_config.validate_on_authentication)
        self.assertEqual(response.password_strength_config.validation_policy, "ZXCVBN")
        self.assertIsNone(response.password_strength_config.luds_min_password_length)
        self.assertIsNone(
            response.password_strength_config.luds_min_password_complexity
        )


if __name__ == "__main__":
    unittest.main()
