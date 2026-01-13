"""Integration tests for EmailTemplates resource.

These tests require real API credentials and are skipped by default.
Set STYTCH_WORKSPACE_KEY_ID and STYTCH_WORKSPACE_KEY_SECRET to run them.
"""

import os
import random
import unittest

from stytch_management import Client

# Get credentials from environment
WORKSPACE_KEY_ID = os.environ.get("STYTCH_WORKSPACE_KEY_ID")
WORKSPACE_KEY_SECRET = os.environ.get("STYTCH_WORKSPACE_KEY_SECRET")


def random_id():
    """Generate a random ID for test templates."""
    return f"test-template-{random.randint(0, 1000000)}"


@unittest.skipIf(
    not (WORKSPACE_KEY_ID and WORKSPACE_KEY_SECRET),
    "Integration tests require STYTCH_WORKSPACE_KEY_ID and STYTCH_WORKSPACE_KEY_SECRET",
)
class TestEmailTemplatesIntegration(unittest.TestCase):
    """Integration tests for EmailTemplates resource."""

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

        # Create live environment
        cls.client.environments.create(
            project_slug=cls.project_slug,
            name="production",
            type="LIVE",
            environment_slug="production",
        )

    @classmethod
    def tearDownClass(cls):
        """Clean up the disposable project."""
        if hasattr(cls, "project_slug") and cls.project_slug:
            cls.client.projects.delete(project_slug=cls.project_slug)

    def test_create_prebuilt_template(self):
        """Test creating a prebuilt email template."""
        template_id = random_id()
        response = self.client.email_templates.create(
            project_slug=self.project_slug,
            template_id=template_id,
            name="Test Prebuilt Template",
            sender_information={
                "from_local_part": "noreply",
                "from_name": "No Reply",
                "reply_to_local_part": "support",
                "reply_to_name": "Support Team",
            },
            prebuilt_customization={
                "button_border_radius": 5.0,
                "button_color": "#007BFF",
                "button_text_color": "#FFFFFF",
                "font_family": "ARIAL",
                "text_alignment": "CENTER",
            },
        )

        self.assertEqual(response.email_template.template_id, template_id)
        self.assertEqual(response.email_template.name, "Test Prebuilt Template")
        self.assertIsNotNone(response.email_template.sender_information)
        self.assertIsNotNone(response.email_template.prebuilt_customization)
        self.assertIsNone(response.email_template.custom_html_customization)

    def test_get_existing_prebuilt_template(self):
        """Test getting an existing prebuilt email template."""
        template_id = random_id()

        # Create template first
        create_resp = self.client.email_templates.create(
            project_slug=self.project_slug,
            template_id=template_id,
            name="Test Prebuilt Template",
            sender_information={
                "from_local_part": "noreply",
                "from_name": "No Reply",
            },
            prebuilt_customization={
                "button_border_radius": 5.0,
                "button_color": "#007BFF",
                "button_text_color": "#FFFFFF",
                "font_family": "ARIAL",
                "text_alignment": "CENTER",
            },
        )

        # Get template
        response = self.client.email_templates.get(
            project_slug=self.project_slug, template_id=template_id
        )

        self.assertEqual(
            response.email_template.template_id, create_resp.email_template.template_id
        )
        self.assertEqual(response.email_template.name, create_resp.email_template.name)
        self.assertIsNotNone(response.email_template.prebuilt_customization)
        self.assertIsNone(response.email_template.custom_html_customization)

    def test_get_non_existent_template(self):
        """Test that getting a non-existent template raises an error."""
        with self.assertRaises(Exception):
            self.client.email_templates.get(
                project_slug=self.project_slug, template_id="non-existent-template"
            )

    def test_get_with_missing_template_id(self):
        """Test that missing template ID raises an error."""
        with self.assertRaises(Exception):
            self.client.email_templates.get(
                project_slug=self.project_slug, template_id=""
            )

    def test_get_all_templates(self):
        """Test getting all email templates."""
        template1_id = random_id()
        template2_id = random_id()

        # Create multiple templates
        self.client.email_templates.create(
            project_slug=self.project_slug,
            template_id=template1_id,
            name="Test Prebuilt Template 1",
            sender_information={
                "from_local_part": "noreply",
                "from_name": "No Reply",
            },
            prebuilt_customization={
                "button_border_radius": 5.0,
                "button_color": "#007BFF",
                "button_text_color": "#FFFFFF",
                "font_family": "ARIAL",
                "text_alignment": "CENTER",
            },
        )

        self.client.email_templates.create(
            project_slug=self.project_slug,
            template_id=template2_id,
            name="Test Prebuilt Template 2",
            sender_information={
                "from_local_part": "noreply",
                "from_name": "No Reply",
            },
            prebuilt_customization={
                "button_border_radius": 5.0,
                "button_color": "#007BFF",
                "button_text_color": "#FFFFFF",
                "font_family": "ARIAL",
                "text_alignment": "CENTER",
            },
        )

        response = self.client.email_templates.get_all(project_slug=self.project_slug)

        self.assertGreaterEqual(len(response.email_templates), 2)

        template_ids = [t.template_id for t in response.email_templates]
        self.assertIn(template1_id, template_ids)
        self.assertIn(template2_id, template_ids)

    def test_update_prebuilt_template(self):
        """Test updating a prebuilt email template."""
        template_id = random_id()

        # Create template first
        self.client.email_templates.create(
            project_slug=self.project_slug,
            template_id=template_id,
            name="Test Prebuilt Template",
            sender_information={
                "from_local_part": "noreply",
                "from_name": "No Reply",
            },
            prebuilt_customization={
                "button_border_radius": 5.0,
                "button_color": "#007BFF",
                "button_text_color": "#FFFFFF",
                "font_family": "ARIAL",
                "text_alignment": "CENTER",
            },
        )

        # Update template
        new_name = "Updated Prebuilt Template"
        response = self.client.email_templates.update(
            project_slug=self.project_slug,
            template_id=template_id,
            name=new_name,
            prebuilt_customization={
                "button_border_radius": 10.0,
                "button_color": "#FF0000",
                "button_text_color": "#000000",
                "font_family": "HELVETICA",
                "text_alignment": "LEFT",
            },
        )

        self.assertEqual(response.email_template.template_id, template_id)
        self.assertEqual(response.email_template.name, new_name)
        self.assertIsNotNone(response.email_template.prebuilt_customization)
        self.assertEqual(
            response.email_template.prebuilt_customization.button_border_radius, 10.0
        )
        self.assertIsNone(response.email_template.custom_html_customization)

    def test_update_non_existent_template(self):
        """Test that updating a non-existent template raises an error."""
        with self.assertRaises(Exception):
            self.client.email_templates.update(
                project_slug=self.project_slug,
                template_id="non-existent-template",
                name="Non-existent Template",
            )

    def test_delete_existing_template(self):
        """Test deleting an existing email template."""
        template_id = random_id()

        # Create template first
        self.client.email_templates.create(
            project_slug=self.project_slug,
            template_id=template_id,
            name="Test Prebuilt Template",
            sender_information={
                "from_local_part": "noreply",
                "from_name": "No Reply",
            },
            prebuilt_customization={
                "button_border_radius": 5.0,
                "button_color": "#007BFF",
                "button_text_color": "#FFFFFF",
                "font_family": "ARIAL",
                "text_alignment": "CENTER",
            },
        )

        # Delete template
        response = self.client.email_templates.delete(
            project_slug=self.project_slug, template_id=template_id
        )

        self.assertIsNotNone(response)

        # Verify template is deleted
        with self.assertRaises(Exception):
            self.client.email_templates.get(
                project_slug=self.project_slug, template_id=template_id
            )

    def test_set_default_template(self):
        """Test setting a default email template."""
        template_id = random_id()

        # Create template first
        self.client.email_templates.create(
            project_slug=self.project_slug,
            template_id=template_id,
            name="Test Default Template",
            sender_information={
                "from_local_part": "noreply",
                "from_name": "No Reply",
            },
            prebuilt_customization={
                "button_border_radius": 5.0,
                "button_color": "#007BFF",
                "button_text_color": "#FFFFFF",
                "font_family": "ARIAL",
                "text_alignment": "CENTER",
            },
        )

        # Set as default
        response = self.client.email_templates.set_default(
            project_slug=self.project_slug,
            email_template_type="PREBUILT",
            template_id=template_id,
        )

        self.assertIsNotNone(response)

    def test_set_default_with_non_existent_template(self):
        """Test that setting default with non-existent template raises an error."""
        with self.assertRaises(Exception):
            self.client.email_templates.set_default(
                project_slug=self.project_slug,
                email_template_type="LOGIN",
                template_id="non-existent-template",
            )

    def test_get_default_template(self):
        """Test getting a default email template."""
        template_id = random_id()

        # Create template first
        self.client.email_templates.create(
            project_slug=self.project_slug,
            template_id=template_id,
            name="Test Default Template",
            sender_information={
                "from_local_part": "noreply",
                "from_name": "No Reply",
            },
            prebuilt_customization={
                "button_border_radius": 5.0,
                "button_color": "#007BFF",
                "button_text_color": "#FFFFFF",
                "font_family": "ARIAL",
                "text_alignment": "CENTER",
            },
        )

        # Set as default
        self.client.email_templates.set_default(
            project_slug=self.project_slug,
            email_template_type="PREBUILT",
            template_id=template_id,
        )

        # Get default
        response = self.client.email_templates.get_default(
            project_slug=self.project_slug, email_template_type="PREBUILT"
        )

        self.assertEqual(response.template_id, template_id)

    def test_get_default_for_type_with_no_default_set(self):
        """Test that getting default for type with no default set raises an error."""
        with self.assertRaises(Exception):
            self.client.email_templates.get_default(
                project_slug=self.project_slug, email_template_type="SIGNUP"
            )

    def test_unset_default_prebuilt_template(self):
        """Test that unsetting prebuilt template raises an error."""
        template_id = random_id()

        # Create template first
        self.client.email_templates.create(
            project_slug=self.project_slug,
            template_id=template_id,
            name="Test Default Template",
            sender_information={
                "from_local_part": "noreply",
                "from_name": "No Reply",
            },
            prebuilt_customization={
                "button_border_radius": 5.0,
                "button_color": "#007BFF",
                "button_text_color": "#FFFFFF",
                "font_family": "ARIAL",
                "text_alignment": "CENTER",
            },
        )

        # Unset default should fail
        with self.assertRaises(Exception):
            self.client.email_templates.unset_default(
                project_slug=self.project_slug, email_template_type="PREBUILT"
            )

    def test_unset_default_for_type_with_no_default_set(self):
        """Test unsetting default for type with no default set succeeds."""
        response = self.client.email_templates.unset_default(
            project_slug=self.project_slug, email_template_type="SIGNUP"
        )

        self.assertIsNotNone(response)


if __name__ == "__main__":
    unittest.main()
