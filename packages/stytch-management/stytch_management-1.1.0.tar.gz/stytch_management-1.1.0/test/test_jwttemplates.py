"""Integration tests for JWTTemplates resource."""

import os
import unittest

from stytch_management import Client

WORKSPACE_KEY_ID = os.environ.get("STYTCH_WORKSPACE_KEY_ID")
WORKSPACE_KEY_SECRET = os.environ.get("STYTCH_WORKSPACE_KEY_SECRET")


@unittest.skipIf(
    not (WORKSPACE_KEY_ID and WORKSPACE_KEY_SECRET),
    "Integration tests require STYTCH_WORKSPACE_KEY_ID and STYTCH_WORKSPACE_KEY_SECRET",
)
class TestJWTTemplatesIntegration(unittest.TestCase):
    """Integration tests for JWTTemplates resource."""

    @classmethod
    def setUpClass(cls):
        """Create a client and disposable projects."""
        cls.client = Client(
            workspace_key_id=WORKSPACE_KEY_ID,
            workspace_key_secret=WORKSPACE_KEY_SECRET,
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

        # Create test environment
        cls.client.environments.create(
            project_slug=cls.consumer_project_slug,
            name="test",
            type="TEST",
            environment_slug="test",
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

    @classmethod
    def tearDownClass(cls):
        """Clean up the disposable projects."""
        if hasattr(cls, "consumer_project_slug") and cls.consumer_project_slug:
            cls.client.projects.delete(project_slug=cls.consumer_project_slug)
        if hasattr(cls, "b2b_project_slug") and cls.b2b_project_slug:
            cls.client.projects.delete(project_slug=cls.b2b_project_slug)

    def test_get_session_template(self):
        """Test getting a session JWT template."""
        envs_resp = self.client.environments.get_all(
            project_slug=self.consumer_project_slug
        )
        test_env = next((e for e in envs_resp.environments if e.type == "TEST"), None)
        environment_slug = test_env.environment_slug

        template_content = (
            '{"custom_user_id": "user-123", "custom_email": "test@example.com"}'
        )
        custom_audience = "my-custom-audience"

        # Set template
        self.client.jwt_templates.set(
            project_slug=self.consumer_project_slug,
            environment_slug=environment_slug,
            jwt_template_type="SESSION",
            template_content=template_content,
            custom_audience=custom_audience,
        )

        # Get template
        response = self.client.jwt_templates.get(
            project_slug=self.consumer_project_slug,
            environment_slug=environment_slug,
            jwt_template_type="SESSION",
        )

        self.assertEqual(response.jwt_template.template_content, template_content)
        self.assertEqual(response.jwt_template.custom_audience, custom_audience)
        self.assertEqual(response.jwt_template.jwt_template_type, "SESSION")

    def test_get_m2m_template(self):
        """Test getting an M2M JWT template."""
        envs_resp = self.client.environments.get_all(project_slug=self.b2b_project_slug)
        test_env = next((e for e in envs_resp.environments if e.type == "TEST"), None)
        environment_slug = test_env.environment_slug

        template_content = (
            '{"custom_org_id": "org-456", "custom_name": "Test Organization"}'
        )
        custom_audience = "m2m-audience"

        # Set template
        self.client.jwt_templates.set(
            project_slug=self.b2b_project_slug,
            environment_slug=environment_slug,
            jwt_template_type="M2M",
            template_content=template_content,
            custom_audience=custom_audience,
        )

        # Get template
        response = self.client.jwt_templates.get(
            project_slug=self.b2b_project_slug,
            environment_slug=environment_slug,
            jwt_template_type="M2M",
        )

        self.assertEqual(response.jwt_template.template_content, template_content)
        self.assertEqual(response.jwt_template.custom_audience, custom_audience)
        self.assertEqual(response.jwt_template.jwt_template_type, "M2M")

    def test_set_session_template(self):
        """Test setting a session JWT template."""
        envs_resp = self.client.environments.get_all(
            project_slug=self.consumer_project_slug
        )
        test_env = next((e for e in envs_resp.environments if e.type == "TEST"), None)
        environment_slug = test_env.environment_slug

        template_content = (
            '{"custom_user_id": "user-123", "custom_email": "test@example.com"}'
        )
        custom_audience = "my-custom-audience"

        response = self.client.jwt_templates.set(
            project_slug=self.consumer_project_slug,
            environment_slug=environment_slug,
            jwt_template_type="SESSION",
            template_content=template_content,
            custom_audience=custom_audience,
        )

        self.assertEqual(response.jwt_template.template_content, template_content)
        self.assertEqual(response.jwt_template.custom_audience, custom_audience)
        self.assertEqual(response.jwt_template.jwt_template_type, "SESSION")

    def test_set_m2m_template(self):
        """Test setting an M2M JWT template."""
        envs_resp = self.client.environments.get_all(project_slug=self.b2b_project_slug)
        test_env = next((e for e in envs_resp.environments if e.type == "TEST"), None)
        environment_slug = test_env.environment_slug

        template_content = (
            '{"custom_org_id": "org-456", "custom_name": "Test Organization"}'
        )
        custom_audience = "m2m-audience"

        response = self.client.jwt_templates.set(
            project_slug=self.b2b_project_slug,
            environment_slug=environment_slug,
            jwt_template_type="M2M",
            template_content=template_content,
            custom_audience=custom_audience,
        )

        self.assertEqual(response.jwt_template.template_content, template_content)
        self.assertEqual(response.jwt_template.custom_audience, custom_audience)
        self.assertEqual(response.jwt_template.jwt_template_type, "M2M")


if __name__ == "__main__":
    unittest.main()
