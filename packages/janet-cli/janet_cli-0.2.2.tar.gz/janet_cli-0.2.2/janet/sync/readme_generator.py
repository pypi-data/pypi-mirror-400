"""Generate README for synced ticket directory."""

from datetime import datetime
from pathlib import Path
from typing import List, Dict


class ReadmeGenerator:
    """Generate README.md for synced ticket directory."""

    def generate(
        self,
        org_name: str,
        projects: List[Dict],
        total_tickets: int,
        sync_time: datetime,
    ) -> str:
        """
        Generate README content for ticket directory.

        Args:
            org_name: Organization name
            projects: List of synced projects
            total_tickets: Total number of tickets synced
            sync_time: Timestamp of sync

        Returns:
            README markdown content
        """
        sections = []

        # Header
        sections.append(f"# Janet AI Tickets - {org_name}\n")
        sections.append(
            "This directory contains your Janet AI tickets synced as markdown files "
            "for use with AI coding agents like Claude Code, Cursor, and GitHub Copilot.\n"
        )

        # What is this?
        sections.append("## What is this?\n")
        sections.append(
            "These markdown files are a local mirror of your tickets from "
            "[Janet AI](https://tryjanet.ai), an AI-native project management platform. "
            "Each ticket has been exported as a markdown file containing:\n"
        )
        sections.append("- **Metadata** - Status, priority, assignees, dates, labels")
        sections.append("- **Description** - Full ticket description")
        sections.append("- **Comments** - All comments with timestamps")
        sections.append("- **Attachments** - Attachment metadata and descriptions")
        sections.append("- **Child Tasks** - Sub-tasks if applicable\n")

        # Why is this here?
        sections.append("## Why is this here?\n")
        sections.append(
            "AI coding assistants work best when they have full context about your project. "
            "By having your tickets in your workspace, AI agents can:\n"
        )
        sections.append("- Reference specific tickets while writing code")
        sections.append("- Understand requirements and acceptance criteria")
        sections.append("- Answer questions about project priorities and status")
        sections.append("- Suggest implementations based on ticket descriptions")
        sections.append("- Link code changes to relevant tickets\n")

        # Directory structure
        sections.append("## Directory Structure\n")
        sections.append("```")
        sections.append(f"{org_name}/")
        for project in projects[:10]:  # Show first 10 projects
            key = project.get("project_identifier", "")
            name = project.get("project_name", "")
            count = project.get("ticket_count", 0)
            sections.append(f"├── {name}/")
            sections.append(f"│   ├── {key}-1.md")
            sections.append(f"│   ├── {key}-2.md")
            sections.append(f"│   └── ... ({count} tickets)")

        if len(projects) > 10:
            sections.append(f"└── ... ({len(projects) - 10} more projects)")
        sections.append("```\n")

        # Sync info
        sections.append("## Sync Information\n")
        sections.append(f"- **Organization:** {org_name}")
        sections.append(f"- **Projects Synced:** {len(projects)}")
        sections.append(f"- **Total Tickets:** {total_tickets}")
        sections.append(
            f"- **Last Synced:** {sync_time.strftime('%B %d, %Y at %I:%M %p')}\n"
        )

        # Projects summary
        if projects:
            sections.append("### Projects\n")
            for project in projects:
                key = project.get("project_identifier", "")
                name = project.get("project_name", "")
                count = project.get("ticket_count", 0)
                sections.append(f"- **{key}** - {name} ({count} tickets)")
            sections.append("")

        # How to use
        sections.append("## How to Use with AI Coding Agents\n")
        sections.append(
            "When working with AI assistants (Claude Code, Cursor, etc.), "
            "you can reference these tickets:\n"
        )
        sections.append('```bash')
        sections.append('# Example prompts:')
        sections.append('"Look at ticket CS-42 and implement the authentication flow"')
        sections.append('"What are the high priority tickets in the Software project?"')
        sections.append('"Which tickets are assigned to me?"')
        sections.append('"Implement the feature described in HL-15"')
        sections.append('```\n')

        # Keeping in sync
        sections.append("## Keeping Tickets in Sync\n")
        sections.append("To update tickets with latest changes from Janet AI:\n")
        sections.append("```bash")
        sections.append("janet sync")
        sections.append("```\n")
        sections.append(
            "This will update all changed tickets and add new ones. "
            "Run this regularly to keep your local tickets up to date.\n"
        )

        # About Janet AI
        sections.append("## About Janet AI\n")
        sections.append(
            "[Janet AI](https://tryjanet.ai) is an AI-native project management platform "
            "designed for modern software teams. It provides:\n"
        )
        sections.append("- AI-powered ticket creation and updates")
        sections.append("- Intelligent ticket prioritization")
        sections.append("- Automated ticket summaries and evaluations")
        sections.append("- Real-time collaboration")
        sections.append("- GitHub integration")
        sections.append("- Discord/Slack integration")
        sections.append("- Meeting and document context linking\n")

        # Footer
        sections.append("---\n")
        sections.append(
            f"*Generated by [Janet CLI](https://github.com/janet-ai/janet-cli) v0.2.0 "
            f"on {sync_time.strftime('%B %d, %Y at %I:%M %p')}*\n"
        )

        return "\n".join(sections)

    def write_readme(
        self,
        sync_dir: Path,
        org_name: str,
        projects: List[Dict],
        total_tickets: int,
    ) -> Path:
        """
        Write README.md to sync directory.

        Args:
            sync_dir: Root sync directory
            org_name: Organization name
            projects: List of synced projects
            total_tickets: Total number of tickets synced

        Returns:
            Path to created README
        """
        sync_time = datetime.utcnow()
        readme_content = self.generate(org_name, projects, total_tickets, sync_time)

        # Write to root of sync directory
        readme_path = sync_dir / "README.md"
        readme_path.write_text(readme_content, encoding="utf-8")

        return readme_path
