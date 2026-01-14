"""Project API methods."""

from typing import List, Dict

from janet.api.client import APIClient
from janet.config.manager import ConfigManager


class ProjectAPI(APIClient):
    """API methods for project management."""

    def __init__(self, config_manager: ConfigManager):
        """
        Initialize project API.

        Args:
            config_manager: Configuration manager instance
        """
        super().__init__(config_manager)

    def list_projects(self) -> List[Dict]:
        """
        List projects in the current organization.

        Returns:
            List of project dictionaries

        Raises:
            NetworkError: If API request fails
            AuthenticationError: If not authenticated
        """
        response = self.get("/api/v1/projects", include_org=True)

        if not response.get("success"):
            raise Exception(response.get("error", "Failed to fetch projects"))

        return response.get("projects", [])

    def get_project(self, project_id: str) -> Dict:
        """
        Get project details.

        Args:
            project_id: Project ID

        Returns:
            Project dictionary

        Raises:
            NetworkError: If API request fails
        """
        response = self.get(f"/api/v1/projects/{project_id}", include_org=True)

        if not response.get("success"):
            raise Exception(response.get("error", "Failed to fetch project"))

        return response.get("project", {})
