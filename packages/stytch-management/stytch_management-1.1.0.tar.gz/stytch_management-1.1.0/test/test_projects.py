"""Integration tests for Projects resource.

These tests require real API credentials and are skipped by default.
Set STYTCH_WORKSPACE_KEY_ID and STYTCH_WORKSPACE_KEY_SECRET to run them.
"""

import os
import time
import unittest

from stytch_management import Client
from stytch_management.errors import StytchError

# Get credentials from environment
WORKSPACE_KEY_ID = os.environ.get("STYTCH_WORKSPACE_KEY_ID")
WORKSPACE_KEY_SECRET = os.environ.get("STYTCH_WORKSPACE_KEY_SECRET")


@unittest.skipIf(
    not (WORKSPACE_KEY_ID and WORKSPACE_KEY_SECRET),
    "Integration tests require STYTCH_WORKSPACE_KEY_ID and STYTCH_WORKSPACE_KEY_SECRET",
)
class TestProjectsIntegration(unittest.TestCase):
    """Integration tests for Projects resource."""

    @classmethod
    def setUpClass(cls):
        """Create a client with real credentials."""
        cls.client = Client(
            workspace_key_id=WORKSPACE_KEY_ID,
            workspace_key_secret=WORKSPACE_KEY_SECRET,
        )

    def test_list_all_projects(self):
        """Test that we can list all projects."""
        response = self.client.projects.get_all()

        self.assertTrue(hasattr(response, "request_id"))
        self.assertTrue(hasattr(response, "projects"))
        self.assertIsInstance(response.projects, list)

    def test_create_get_update_delete_project(self):
        """Test the full CRUD lifecycle for a project."""
        # Create
        project_name = f"Test Project {int(time.time())}"
        create_response = self.client.projects.create(name=project_name, vertical="B2B")

        self.assertIsNotNone(create_response.project)
        project_slug = create_response.project.project_slug
        self.assertIsNotNone(project_slug)

        try:
            # Get
            get_response = self.client.projects.get(project_slug=project_slug)
            self.assertEqual(get_response.project.project_slug, project_slug)
            self.assertEqual(get_response.project.name, project_name)

            # Update
            updated_name = f"Updated Test Project {int(time.time())}"
            update_response = self.client.projects.update(
                project_slug=project_slug, name=updated_name
            )
            self.assertEqual(update_response.project.name, updated_name)

        finally:
            # Delete (cleanup)
            delete_response = self.client.projects.delete(project_slug=project_slug)
            self.assertIsNotNone(delete_response.request_id)

            # Verify deletion - should raise an error
            with self.assertRaises(StytchError):
                self.client.projects.get(project_slug=project_slug)


if __name__ == "__main__":
    unittest.main()
