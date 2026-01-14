"""Organization API methods."""

from typing import List, Dict

from janet.api.client import APIClient
from janet.config.manager import ConfigManager


class OrganizationAPI(APIClient):
    """API methods for organization management."""

    def __init__(self, config_manager: ConfigManager):
        """
        Initialize organization API.

        Args:
            config_manager: Configuration manager instance
        """
        super().__init__(config_manager)

    def list_organizations(self) -> List[Dict]:
        """
        List available organizations for the authenticated user.

        Returns:
            List of organization dictionaries

        Raises:
            NetworkError: If API request fails
            AuthenticationError: If not authenticated
        """
        response = self.get("/api/v1/organizations/list")

        if not response.get("success"):
            raise Exception(response.get("error", "Failed to fetch organizations"))

        return response.get("organizations", [])

    def get_organization(self, org_id: str) -> Dict:
        """
        Get organization details.

        Args:
            org_id: Organization ID

        Returns:
            Organization dictionary

        Raises:
            NetworkError: If API request fails
        """
        response = self.get(f"/api/v1/organizations/{org_id}")

        if not response.get("success"):
            raise Exception(response.get("error", "Failed to fetch organization"))

        return response.get("organization", {})
