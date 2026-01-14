"""Main sync orchestration engine."""

import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Optional
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn

from janet.api.organizations import OrganizationAPI
from janet.api.projects import ProjectAPI
from janet.api.tickets import TicketAPI
from janet.config.manager import ConfigManager
from janet.markdown.generator import MarkdownGenerator
from janet.sync.file_manager import FileManager
from janet.utils.console import console, print_success, print_error, print_info
from janet.utils.errors import SyncError


class SyncEngine:
    """Main sync orchestration engine."""

    def __init__(self, config_manager: ConfigManager):
        """
        Initialize sync engine.

        Args:
            config_manager: Configuration manager instance
        """
        self.config_manager = config_manager
        self.config = config_manager.get()

        # Initialize APIs
        self.org_api = OrganizationAPI(config_manager)
        self.project_api = ProjectAPI(config_manager)
        self.ticket_api = TicketAPI(config_manager)

        # Initialize sync components
        self.markdown_generator = MarkdownGenerator()
        self.file_manager = FileManager(self.config.sync.root_directory)

    def sync_all_projects(self) -> Dict:
        """
        Sync all projects in the current organization.

        Returns:
            Summary dictionary with sync statistics
        """
        if not self.config.selected_organization:
            raise SyncError("No organization selected")

        org_name = self.config.selected_organization.name

        # Fetch all projects
        print_info(f"Fetching projects for {org_name}...")
        projects = self.project_api.list_projects()

        if not projects:
            print_info("No projects found")
            return {"projects_synced": 0, "tickets_synced": 0}

        console.print(f"\nFound {len(projects)} project(s)")

        # Sync projects in parallel
        total_tickets = 0
        projects_with_tickets = [p for p in projects if p.get("ticket_count", 0) > 0]

        # Show projects with no tickets
        for project in projects:
            if project.get("ticket_count", 0) == 0:
                console.print(f"  [dim]↳ {project.get('project_identifier', '')} - No tickets[/dim]")

        # Use ThreadPoolExecutor to sync projects in parallel
        max_workers = min(5, len(projects_with_tickets))  # Max 5 concurrent projects

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all sync tasks
            future_to_project = {
                executor.submit(
                    self.sync_project,
                    project["id"],
                    project.get("project_identifier", ""),
                    project.get("project_name", ""),
                ): project
                for project in projects_with_tickets
            }

            # Wait for completion
            for future in as_completed(future_to_project):
                try:
                    synced = future.result()
                    total_tickets += synced
                except Exception as e:
                    project = future_to_project[future]
                    project_key = project.get("project_identifier", "unknown")
                    console.print(f"[red]✗ Failed to sync {project_key}: {e}[/red]")

        return {
            "projects_synced": len(projects),
            "tickets_synced": total_tickets,
        }

    def sync_project(
        self, project_id: str, project_key: str, project_name: str
    ) -> int:
        """
        Sync a single project.

        Args:
            project_id: Project ID
            project_key: Project key (e.g., "PROJ")
            project_name: Project name

        Returns:
            Number of tickets synced
        """
        org_name = self.config.selected_organization.name

        # Fetch ALL tickets using unlimited CLI sync endpoint (no pagination!)
        response = self.ticket_api.sync_all_tickets(project_id)
        tickets = response.get("tickets", [])

        if not tickets:
            console.print(f"  [dim]↳ {project_key} - No tickets found[/dim]")
            return 0

        console.print(f"\n[bold]{project_key}[/bold] - Syncing {len(tickets)} ticket(s)...")

        # Fetch organization members for name resolution (once per project)
        org_members = self._fetch_org_members()

        # Batch fetch all full ticket details at once
        ticket_ids = [t.get("id") for t in tickets if t.get("id")]

        console.print(f"  Fetching full details for {len(ticket_ids)} tickets...")
        full_tickets_list = self.ticket_api.batch_fetch(ticket_ids)

        # Create lookup map by ticket ID
        full_tickets_map = {t.get("id"): t for t in full_tickets_list}

        # Sync each ticket with progress bar
        synced_count = 0
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console,
        ) as progress:
            task = progress.add_task(
                f"Syncing {project_key}...",
                total=len(tickets),
            )

            for ticket in tickets:
                try:
                    # Merge list ticket with full details
                    ticket_id = ticket.get("id")
                    full_ticket = full_tickets_map.get(ticket_id, {})
                    merged_ticket = {**full_ticket, **ticket}

                    self._sync_single_ticket_fast(
                        merged_ticket, org_name, project_name, org_members
                    )
                    synced_count += 1
                except Exception as e:
                    ticket_key = ticket.get("ticket_key") or ticket.get("ticket_identifier") or ticket.get("id", "unknown")
                    console.print(f"  [red]✗ Failed to sync {ticket_key}: {e}[/red]")

                progress.advance(task)

        print_success(f"Synced {synced_count}/{len(tickets)} tickets for {project_key}")
        return synced_count

    def _sync_single_ticket_fast(
        self,
        ticket: Dict,
        org_name: str,
        project_name: str,
        org_members: Optional[List[Dict]] = None,
    ) -> None:
        """
        Sync a single ticket (optimized - no individual API calls).

        Args:
            ticket: Merged ticket dictionary (already has full details)
            org_name: Organization name
            project_name: Project name
            org_members: Organization members for name resolution
        """
        ticket_id = ticket.get("id")

        # Get ticket_key - try multiple fields
        ticket_key = ticket.get("ticket_key")
        if not ticket_key:
            # Fallback: construct from project_identifier and ticket_identifier
            project_identifier = ticket.get("project_identifier") or project_name
            ticket_identifier = ticket.get("ticket_identifier")
            if project_identifier and ticket_identifier:
                ticket_key = f"{project_identifier}-{ticket_identifier}"
            else:
                ticket_key = ticket.get("ticket_identifier")

        # Validate required fields
        if not ticket_id:
            raise Exception("Ticket missing 'id' field")
        if not ticket_key:
            raise Exception(f"Ticket {ticket_id} missing 'ticket_key' field")

        # Ensure ticket has ticket_key for markdown generation
        if "ticket_key" not in ticket:
            ticket["ticket_key"] = ticket_key

        # Skip attachment fetching to reduce API calls
        # Attachments info is usually in the ticket data already
        attachments = None

        # Generate markdown
        markdown = self.markdown_generator.generate(
            ticket, org_members, attachments
        )

        # Write to file
        self.file_manager.write_ticket(
            org_name=org_name,
            project_name=project_name,
            ticket_key=ticket_key,
            content=markdown,
        )

    def _fetch_org_members(self) -> Optional[List[Dict]]:
        """
        Fetch organization members for name resolution.

        Returns:
            List of organization members or None if fetch fails
        """
        try:
            org_id = self.config.selected_organization.id
            response = self.org_api.get(
                f"/api/v1/organizations/{org_id}/members", include_org=False
            )
            return response.get("members", [])
        except Exception as e:
            console.print(f"[yellow]Warning: Could not fetch organization members: {e}[/yellow]")
            return None
