"""Ticket API methods."""

from typing import List, Dict, Optional

from janet.api.client import APIClient
from janet.config.manager import ConfigManager


class TicketAPI(APIClient):
    """API methods for ticket management."""

    def __init__(self, config_manager: ConfigManager):
        """
        Initialize ticket API.

        Args:
            config_manager: Configuration manager instance
        """
        super().__init__(config_manager)

    def list_tickets(
        self,
        project_id: str,
        limit: int = 1000,
        offset: int = 0,
        show_resolved: bool = True,
    ) -> Dict:
        """
        List tickets for a project.

        Args:
            project_id: Project ID
            limit: Maximum tickets to return
            offset: Pagination offset
            show_resolved: Include resolved tickets older than 7 days

        Returns:
            Dictionary with tickets and metadata

        Raises:
            NetworkError: If API request fails
        """
        endpoint = f"/api/v1/projects/{project_id}/tickets/list"

        data = {
            "limit": limit,
            "offset": offset,
            "show_resolved_over_7_days": show_resolved,
        }

        response = self.post(endpoint, data=data, include_org=True)

        if not response.get("success"):
            raise Exception(response.get("error", "Failed to list tickets"))

        return response

    def get_ticket(self, ticket_id: str) -> Dict:
        """
        Get full ticket details.

        Args:
            ticket_id: Ticket ID

        Returns:
            Ticket dictionary with all fields

        Raises:
            NetworkError: If API request fails
        """
        response = self.get(f"/api/v1/tickets/{ticket_id}", include_org=True)

        if not response.get("success"):
            raise Exception(response.get("error", "Failed to fetch ticket"))

        return response.get("ticket", {})

    def batch_fetch(self, ticket_ids: List[str]) -> List[Dict]:
        """
        Fetch multiple tickets in one request.

        Args:
            ticket_ids: List of ticket IDs

        Returns:
            List of ticket dictionaries

        Raises:
            NetworkError: If API request fails
        """
        if not ticket_ids:
            return []

        data = {"ticket_ids": ticket_ids}
        response = self.post("/api/v1/tickets/batch", data=data, include_org=True)

        if not response.get("success"):
            raise Exception(response.get("error", "Failed to batch fetch tickets"))

        return response.get("tickets", [])

    def sync_all_tickets(self, project_id: str) -> Dict:
        """
        Get ALL tickets for a project using the CLI sync endpoint - NO LIMIT.

        Uses dedicated CLI endpoint that returns all tickets in one call.

        Args:
            project_id: Project ID

        Returns:
            Dictionary with ALL tickets (no pagination)

        Raises:
            NetworkError: If API request fails
        """
        endpoint = f"/api/v1/cli/projects/{project_id}/tickets/sync"

        data = {
            "show_resolved_over_7_days": True,
        }

        response = self.post(endpoint, data=data, include_org=True)

        if not response.get("success"):
            raise Exception(response.get("error", "Failed to sync tickets"))

        return response

    def get_ticket_attachments(self, ticket_id: str) -> Dict:
        """
        Get attachments for a ticket.

        Args:
            ticket_id: Ticket ID

        Returns:
            Dictionary with direct and indirect attachments

        Raises:
            NetworkError: If API request fails
        """
        response = self.get(
            f"/api/v1/tickets/{ticket_id}/attachments", include_org=True
        )

        if not response.get("success"):
            raise Exception(response.get("error", "Failed to fetch attachments"))

        return {
            "direct_attachments": response.get("direct_attachments", []),
            "indirect_attachments": response.get("indirect_attachments", []),
        }
