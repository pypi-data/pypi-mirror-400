"""Generate markdown from ticket data."""

from datetime import datetime
from typing import Dict, List, Optional

from janet.markdown.yjs_converter import YjsConverter


class MarkdownGenerator:
    """
    Generate markdown documents from ticket data.

    Based on TypeScript implementation in copyTicketAsMarkdown.ts
    """

    def __init__(self):
        """Initialize markdown generator."""
        self.yjs_converter = YjsConverter()

    def generate(
        self,
        ticket: Dict,
        organization_members: Optional[List[Dict]] = None,
        attachments: Optional[Dict] = None,
    ) -> str:
        """
        Generate complete markdown document from ticket data.

        Args:
            ticket: Ticket dictionary
            organization_members: List of organization members (for name resolution)
            attachments: Dictionary with direct_attachments and indirect_attachments

        Returns:
            Complete markdown string
        """
        sections = []

        # 1. Title
        ticket_key = ticket.get("ticket_key", "UNKNOWN")
        title = ticket.get("title", "Untitled")
        sections.append(f"# {ticket_key}: {title}\n")

        # 2. Metadata
        sections.append(self._generate_metadata(ticket, organization_members))

        # 3. Description
        sections.append(self._generate_description(ticket))

        # 4. Comments
        if ticket.get("comments"):
            sections.append(
                self._generate_comments(ticket["comments"], organization_members)
            )

        # 5. Attachments
        if attachments:
            sections.append(self._generate_attachments(attachments, organization_members))

        # 6. Child Tasks
        if ticket.get("child_tasks"):
            sections.append(self._generate_child_tasks(ticket["child_tasks"]))

        # 7. Footer
        sections.append(self._generate_footer(ticket_key))

        return "\n".join(sections)

    def _generate_metadata(
        self, ticket: Dict, organization_members: Optional[List[Dict]] = None
    ) -> str:
        """Generate metadata section."""
        lines = ["## Metadata\n"]

        # Status
        lines.append(f"- **Status:** {ticket.get('status', 'Unknown')}")

        # Priority
        lines.append(f"- **Priority:** {ticket.get('priority', 'Unknown')}")

        # Type
        lines.append(f"- **Type:** {ticket.get('issue_type', 'Unknown')}")

        # Assignees
        assignees = ticket.get("assignees", [])
        if assignees:
            assignee_names = [
                self._resolve_user_name(email, organization_members) for email in assignees
            ]
            lines.append(f"- **Assignees:** {', '.join(assignee_names)}")
        else:
            lines.append("- **Assignees:** Unassigned")

        # Creator
        creator = ticket.get("creator", "Unknown")
        creator_name = self._resolve_user_name(creator, organization_members)
        lines.append(f"- **Creator:** {creator_name}")

        # Dates
        created_at = ticket.get("created_at", "")
        updated_at = ticket.get("updated_at", "")
        lines.append(f"- **Created:** {self._format_date(created_at)}")
        lines.append(f"- **Updated:** {self._format_date(updated_at)}")

        # Optional fields
        if ticket.get("story_points"):
            lines.append(f"- **Story Points:** {ticket['story_points']}")

        if ticket.get("due_date"):
            lines.append(f"- **Due Date:** {self._format_date(ticket['due_date'])}")

        if ticket.get("sprint"):
            lines.append(f"- **Sprint:** {ticket['sprint']}")

        if ticket.get("labels"):
            labels = ticket["labels"]
            if labels:
                lines.append(f"- **Labels:** {', '.join(labels)}")

        lines.append("")  # Empty line after metadata
        return "\n".join(lines)

    def _generate_description(self, ticket: Dict) -> str:
        """Generate description section."""
        lines = ["## Description\n"]

        yjs_binary = ticket.get("description_yjs_binary")
        plain_text = ticket.get("description")

        # Convert Yjs binary to markdown
        markdown = self.yjs_converter.convert(yjs_binary, plain_text)
        lines.append(markdown)

        lines.append("")  # Empty line after description
        return "\n".join(lines)

    def _generate_comments(
        self, comments: List[Dict], organization_members: Optional[List[Dict]] = None
    ) -> str:
        """Generate comments section."""
        lines = [f"## Comments ({len(comments)})\n"]

        for comment in comments:
            author = comment.get("created_by", "Unknown")
            author_name = self._resolve_user_name(author, organization_members)
            timestamp = self._format_date(comment.get("created_at", ""))

            lines.append(f"### {author_name} - {timestamp}\n")
            lines.append(comment.get("content", ""))
            lines.append("")  # Empty line between comments

        return "\n".join(lines)

    def _generate_attachments(
        self, attachments: Dict, organization_members: Optional[List[Dict]] = None
    ) -> str:
        """Generate attachments section."""
        direct = attachments.get("direct_attachments", [])
        indirect = attachments.get("indirect_attachments", [])
        all_attachments = direct + indirect

        if not all_attachments:
            return ""

        lines = [f"## Attachments ({len(all_attachments)})\n"]

        for attachment in all_attachments:
            filename = attachment.get("original_filename", "Unknown")
            lines.append(f"### {filename}")

            lines.append(f"- **Type:** {attachment.get('mime_type', 'Unknown')}")

            uploader = attachment.get("uploaded_by", "Unknown")
            uploader_name = self._resolve_user_name(uploader, organization_members)
            lines.append(f"- **Uploaded by:** {uploader_name}")

            created_at = attachment.get("created_at", "")
            lines.append(f"- **Uploaded:** {self._format_date(created_at)}")

            if attachment.get("ai_description"):
                lines.append(f"- **AI Description:** {attachment['ai_description']}")

            lines.append("")  # Empty line between attachments

        return "\n".join(lines)

    def _generate_child_tasks(self, child_tasks: List[Dict]) -> str:
        """Generate child tasks section."""
        if not child_tasks:
            return ""

        lines = [f"## Child Tasks ({len(child_tasks)})\n"]

        for task in child_tasks:
            identifier = task.get("fullIdentifier", task.get("childIdentifier", ""))
            title = task.get("title", "Untitled")
            status = task.get("status", "")
            priority = task.get("priority", "")

            # Format: - [STATUS] IDENTIFIER: Title (Priority)
            status_badge = f"[{status}]" if status else ""
            priority_info = f"({priority})" if priority else ""

            line = f"- {status_badge} **{identifier}**: {title}"
            if priority_info:
                line += f" {priority_info}"

            lines.append(line)

        lines.append("")  # Empty line after child tasks
        return "\n".join(lines)

    def _generate_footer(self, ticket_key: str) -> str:
        """Generate footer section."""
        export_date = self._format_date(datetime.utcnow().isoformat())
        return f"---\n*Exported from {ticket_key} on {export_date}*"

    def _resolve_user_name(
        self, email: str, organization_members: Optional[List[Dict]] = None
    ) -> str:
        """
        Resolve user email to display name.

        Args:
            email: User email
            organization_members: List of organization members

        Returns:
            Display name or email if not found
        """
        if not organization_members:
            return email

        for member in organization_members:
            if member.get("email") == email:
                first_name = member.get("firstName", "")
                last_name = member.get("lastName", "")
                if first_name and last_name:
                    return f"{first_name} {last_name}"
                elif first_name:
                    return first_name
                break

        return email

    def _format_date(self, iso_string: str) -> str:
        """
        Format ISO timestamp to human-readable date.

        Args:
            iso_string: ISO 8601 timestamp

        Returns:
            Formatted date string
        """
        if not iso_string:
            return "Unknown"

        try:
            # Parse ISO string (handle both with and without microseconds)
            if "." in iso_string:
                # Has microseconds
                dt = datetime.fromisoformat(iso_string.replace("Z", "+00:00"))
            else:
                # No microseconds
                dt = datetime.fromisoformat(iso_string.replace("Z", "+00:00"))

            # Format: Jan 15, 2024 10:30 AM
            return dt.strftime("%b %d, %Y %I:%M %p")
        except Exception:
            # Fallback: return as-is
            return iso_string
