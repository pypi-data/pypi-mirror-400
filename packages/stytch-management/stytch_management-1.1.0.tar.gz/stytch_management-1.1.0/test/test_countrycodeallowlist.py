"""Integration tests for CountryCodeAllowlist resource."""

import os
import unittest

from stytch_management import Client

WORKSPACE_KEY_ID = os.environ.get("STYTCH_WORKSPACE_KEY_ID")
WORKSPACE_KEY_SECRET = os.environ.get("STYTCH_WORKSPACE_KEY_SECRET")


@unittest.skipIf(
    not (WORKSPACE_KEY_ID and WORKSPACE_KEY_SECRET),
    "Integration tests require STYTCH_WORKSPACE_KEY_ID and STYTCH_WORKSPACE_KEY_SECRET",
)
class TestCountryCodeAllowlistIntegration(unittest.TestCase):
    """Integration tests for CountryCodeAllowlist resource."""

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

        # Create test environment
        cls.client.environments.create(
            project_slug=cls.b2b_project_slug,
            name="test",
            type="TEST",
            environment_slug="test",
        )

        # Create second test environment for mutation tests
        cls.client.environments.create(
            project_slug=cls.b2b_project_slug,
            name="test-mutation",
            type="TEST",
            environment_slug="test-mutation",
        )

        b2b_envs_resp = cls.client.environments.get_all(
            project_slug=cls.b2b_project_slug
        )
        b2b_test_env = next(
            (
                e
                for e in b2b_envs_resp.environments
                if e.type == "TEST" and e.environment_slug == "test"
            ),
            None,
        )
        cls.b2b_environment_slug = b2b_test_env.environment_slug

        b2b_test_mutation_env = next(
            (
                e
                for e in b2b_envs_resp.environments
                if e.type == "TEST" and e.environment_slug == "test-mutation"
            ),
            None,
        )
        cls.b2b_mutation_environment_slug = b2b_test_mutation_env.environment_slug

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

        # Create test environment
        cls.client.environments.create(
            project_slug=cls.consumer_project_slug,
            name="test",
            type="TEST",
            environment_slug="test",
        )

        # Create second test environment for mutation tests
        cls.client.environments.create(
            project_slug=cls.consumer_project_slug,
            name="test-mutation",
            type="TEST",
            environment_slug="test-mutation",
        )

        consumer_envs_resp = cls.client.environments.get_all(
            project_slug=cls.consumer_project_slug
        )
        consumer_test_env = next(
            (
                e
                for e in consumer_envs_resp.environments
                if e.type == "TEST" and e.environment_slug == "test"
            ),
            None,
        )
        cls.consumer_environment_slug = consumer_test_env.environment_slug

        consumer_test_mutation_env = next(
            (
                e
                for e in consumer_envs_resp.environments
                if e.type == "TEST" and e.environment_slug == "test-mutation"
            ),
            None,
        )
        cls.consumer_mutation_environment_slug = (
            consumer_test_mutation_env.environment_slug
        )

    @classmethod
    def tearDownClass(cls):
        """Clean up the disposable projects."""
        if hasattr(cls, "b2b_project_slug") and cls.b2b_project_slug:
            cls.client.projects.delete(project_slug=cls.b2b_project_slug)
        if hasattr(cls, "consumer_project_slug") and cls.consumer_project_slug:
            cls.client.projects.delete(project_slug=cls.consumer_project_slug)

    def test_get_allowed_sms_country_codes_default(self):
        """Test getting default allowed SMS country codes."""
        expected = ["CA", "US"]

        response = self.client.country_code_allowlist.get_allowed_sms_country_codes(
            project_slug=self.b2b_project_slug,
            environment_slug=self.b2b_environment_slug,
        )

        self.assertEqual(response.country_codes, expected)

    def test_get_allowed_sms_country_codes_after_setting(self):
        """Test getting allowed SMS country codes after setting."""
        expected = ["CA", "MX", "US"]

        self.client.country_code_allowlist.set_allowed_sms_country_codes(
            project_slug=self.consumer_project_slug,
            environment_slug=self.consumer_mutation_environment_slug,
            country_codes=expected,
        )

        response = self.client.country_code_allowlist.get_allowed_sms_country_codes(
            project_slug=self.consumer_project_slug,
            environment_slug=self.consumer_mutation_environment_slug,
        )

        self.assertEqual(response.country_codes, expected)

    def test_get_allowed_sms_project_does_not_exist(self):
        """Test that getting SMS codes for non-existent project raises an error."""
        with self.assertRaises(Exception):
            self.client.country_code_allowlist.get_allowed_sms_country_codes(
                project_slug="project-does-not-exist",
                environment_slug="test",
            )

    def test_get_allowed_whatsapp_country_codes_default(self):
        """Test getting default allowed WhatsApp country codes."""
        expected = ["CA", "US"]

        response = (
            self.client.country_code_allowlist.get_allowed_whatsapp_country_codes(
                project_slug=self.consumer_project_slug,
                environment_slug=self.consumer_environment_slug,
            )
        )

        self.assertEqual(response.country_codes, expected)

    def test_get_allowed_whatsapp_country_codes_after_setting(self):
        """Test getting allowed WhatsApp country codes after setting."""
        expected = ["CA", "MX", "US"]

        self.client.country_code_allowlist.set_allowed_whatsapp_country_codes(
            project_slug=self.consumer_project_slug,
            environment_slug=self.consumer_mutation_environment_slug,
            country_codes=expected,
        )

        response = (
            self.client.country_code_allowlist.get_allowed_whatsapp_country_codes(
                project_slug=self.consumer_project_slug,
                environment_slug=self.consumer_mutation_environment_slug,
            )
        )

        self.assertEqual(response.country_codes, expected)

    def test_get_allowed_whatsapp_b2b_not_supported(self):
        """Test that WhatsApp is not supported for B2B projects."""
        with self.assertRaises(Exception) as context:
            self.client.country_code_allowlist.get_allowed_whatsapp_country_codes(
                project_slug=self.b2b_project_slug,
                environment_slug=self.b2b_environment_slug,
            )
        self.assertIn(
            "country_code_allowlist_b2b_whatsapp_not_supported", str(context.exception)
        )

    def test_get_allowed_whatsapp_project_does_not_exist(self):
        """Test that getting WhatsApp codes for non-existent project raises an error."""
        with self.assertRaises(Exception):
            self.client.country_code_allowlist.get_allowed_whatsapp_country_codes(
                project_slug="project-does-not-exist",
                environment_slug="test",
            )

    def test_set_allowed_sms_country_codes(self):
        """Test setting allowed SMS country codes."""
        expected = ["CA", "MX", "US"]

        set_resp = self.client.country_code_allowlist.set_allowed_sms_country_codes(
            project_slug=self.consumer_project_slug,
            environment_slug=self.consumer_mutation_environment_slug,
            country_codes=expected,
        )

        self.assertEqual(set_resp.country_codes, expected)

        get_resp = self.client.country_code_allowlist.get_allowed_sms_country_codes(
            project_slug=self.consumer_project_slug,
            environment_slug=self.consumer_mutation_environment_slug,
        )

        self.assertEqual(get_resp.country_codes, expected)

    def test_set_allowed_sms_project_does_not_exist(self):
        """Test that setting SMS codes for non-existent project raises an error."""
        with self.assertRaises(Exception):
            self.client.country_code_allowlist.set_allowed_sms_country_codes(
                project_slug="project-does-not-exist",
                environment_slug="test",
                country_codes=["CA", "MX", "US"],
            )

    def test_set_allowed_whatsapp_country_codes(self):
        """Test setting allowed WhatsApp country codes."""
        expected = ["CA", "MX", "US"]

        set_resp = (
            self.client.country_code_allowlist.set_allowed_whatsapp_country_codes(
                project_slug=self.consumer_project_slug,
                environment_slug=self.consumer_mutation_environment_slug,
                country_codes=expected,
            )
        )

        self.assertEqual(set_resp.country_codes, expected)

        get_resp = (
            self.client.country_code_allowlist.get_allowed_whatsapp_country_codes(
                project_slug=self.consumer_project_slug,
                environment_slug=self.consumer_mutation_environment_slug,
            )
        )

        self.assertEqual(get_resp.country_codes, expected)

    def test_set_allowed_whatsapp_b2b_not_supported(self):
        """Test that WhatsApp is not supported for B2B projects when setting."""
        with self.assertRaises(Exception) as context:
            self.client.country_code_allowlist.set_allowed_whatsapp_country_codes(
                project_slug=self.b2b_project_slug,
                environment_slug=self.b2b_environment_slug,
                country_codes=["CA", "MX", "US"],
            )
        self.assertIn(
            "country_code_allowlist_b2b_whatsapp_not_supported", str(context.exception)
        )

    def test_set_allowed_whatsapp_project_does_not_exist(self):
        """Test that setting WhatsApp codes for non-existent project raises an error."""
        with self.assertRaises(Exception):
            self.client.country_code_allowlist.set_allowed_whatsapp_country_codes(
                project_slug="project-does-not-exist",
                environment_slug="test",
                country_codes=["CA", "MX", "US"],
            )


if __name__ == "__main__":
    unittest.main()
