"""File manager for writing ticket markdown files."""

from pathlib import Path
from typing import Optional

from janet.utils.paths import sanitize_filename, expand_path


class FileManager:
    """Manages writing ticket markdown files to filesystem."""

    def __init__(self, root_directory: str = "~/janet-tickets"):
        """
        Initialize file manager.

        Args:
            root_directory: Root directory for ticket files
        """
        self.root_directory = expand_path(root_directory)

    def write_ticket(
        self,
        org_name: str,
        project_name: str,
        ticket_key: str,
        content: str,
    ) -> Path:
        """
        Write ticket markdown to file.

        Args:
            org_name: Organization name
            project_name: Project name
            ticket_key: Ticket key (e.g., "PROJ-1")
            content: Markdown content

        Returns:
            Path to created file
        """
        # Sanitize names for filesystem
        safe_org = sanitize_filename(org_name)
        safe_project = sanitize_filename(project_name)
        safe_key = sanitize_filename(ticket_key)

        # Create directory structure: root/org/project/
        project_dir = self.root_directory / safe_org / safe_project
        project_dir.mkdir(parents=True, exist_ok=True)

        # Create file path: root/org/project/TICKET-KEY.md
        file_path = project_dir / f"{safe_key}.md"

        # Write markdown content
        file_path.write_text(content, encoding="utf-8")

        return file_path

    def get_ticket_path(
        self, org_name: str, project_name: str, ticket_key: str
    ) -> Path:
        """
        Get path for a ticket file (without writing).

        Args:
            org_name: Organization name
            project_name: Project name
            ticket_key: Ticket key

        Returns:
            Path to ticket file
        """
        safe_org = sanitize_filename(org_name)
        safe_project = sanitize_filename(project_name)
        safe_key = sanitize_filename(ticket_key)

        return self.root_directory / safe_org / safe_project / f"{safe_key}.md"

    def ticket_exists(self, org_name: str, project_name: str, ticket_key: str) -> bool:
        """
        Check if ticket file exists.

        Args:
            org_name: Organization name
            project_name: Project name
            ticket_key: Ticket key

        Returns:
            True if file exists
        """
        file_path = self.get_ticket_path(org_name, project_name, ticket_key)
        return file_path.exists()

    def list_tickets(self, org_name: Optional[str] = None, project_name: Optional[str] = None) -> list[Path]:
        """
        List all ticket markdown files.

        Args:
            org_name: Optional organization name to filter
            project_name: Optional project name to filter

        Returns:
            List of ticket file paths
        """
        if org_name and project_name:
            # List tickets in specific project
            safe_org = sanitize_filename(org_name)
            safe_project = sanitize_filename(project_name)
            search_path = self.root_directory / safe_org / safe_project
        elif org_name:
            # List tickets in organization
            safe_org = sanitize_filename(org_name)
            search_path = self.root_directory / safe_org
        else:
            # List all tickets
            search_path = self.root_directory

        if not search_path.exists():
            return []

        # Find all .md files
        return list(search_path.rglob("*.md"))

    def archive_ticket(
        self, org_name: str, project_name: str, ticket_key: str
    ) -> Optional[Path]:
        """
        Move ticket to .archived folder.

        Args:
            org_name: Organization name
            project_name: Project name
            ticket_key: Ticket key

        Returns:
            New path if archived, None if file didn't exist
        """
        file_path = self.get_ticket_path(org_name, project_name, ticket_key)

        if not file_path.exists():
            return None

        # Create .archived directory
        archived_dir = file_path.parent / ".archived"
        archived_dir.mkdir(exist_ok=True)

        # Move file
        new_path = archived_dir / file_path.name
        file_path.rename(new_path)

        return new_path

    def delete_ticket(self, org_name: str, project_name: str, ticket_key: str) -> bool:
        """
        Delete ticket file.

        Args:
            org_name: Organization name
            project_name: Project name
            ticket_key: Ticket key

        Returns:
            True if deleted, False if didn't exist
        """
        file_path = self.get_ticket_path(org_name, project_name, ticket_key)

        if not file_path.exists():
            return False

        file_path.unlink()
        return True

    def get_project_directory(self, org_name: str, project_name: str) -> Path:
        """
        Get project directory path.

        Args:
            org_name: Organization name
            project_name: Project name

        Returns:
            Path to project directory
        """
        safe_org = sanitize_filename(org_name)
        safe_project = sanitize_filename(project_name)
        return self.root_directory / safe_org / safe_project

    def ensure_project_directory(self, org_name: str, project_name: str) -> Path:
        """
        Ensure project directory exists.

        Args:
            org_name: Organization name
            project_name: Project name

        Returns:
            Path to project directory
        """
        project_dir = self.get_project_directory(org_name, project_name)
        project_dir.mkdir(parents=True, exist_ok=True)
        return project_dir
