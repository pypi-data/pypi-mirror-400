"""Main CLI application using Typer."""

import typer
from typing_extensions import Annotated

from janet import __version__
from janet.config.manager import ConfigManager
from janet.utils.console import console, print_success, print_error, print_info
from janet.utils.errors import JanetCLIError

# Initialize Typer app
app = typer.Typer(
    name="janet",
    help="Janet AI CLI - Sync tickets to local markdown files",
    add_completion=False,
)

# Sub-commands
auth_app = typer.Typer(help="Authentication commands")
org_app = typer.Typer(help="Organization management")
project_app = typer.Typer(help="Project management")
config_app = typer.Typer(help="Configuration management")

app.add_typer(auth_app, name="auth")
app.add_typer(org_app, name="org")
app.add_typer(project_app, name="project")
app.add_typer(config_app, name="config")

# Initialize config manager
config_manager = ConfigManager()


def version_callback(value: bool) -> None:
    """Show version and exit."""
    if value:
        console.print(f"Janet CLI v{__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Annotated[
        bool, typer.Option("--version", "-v", callback=version_callback, is_eager=True)
    ] = False,
) -> None:
    """Janet AI CLI - Sync tickets to local markdown files."""
    pass


# =============================================================================
# Authentication Commands
# =============================================================================


@app.command(name="login")
def login() -> None:
    """Authenticate with Janet AI and select organization."""
    try:
        from janet.auth.oauth_flow import OAuthFlow
        from janet.api.organizations import OrganizationAPI
        from InquirerPy import inquirer

        print_info("Starting authentication flow...")

        # Start OAuth flow
        oauth_flow = OAuthFlow(config_manager)
        oauth_flow.start_login()

        # Fetch available organizations
        print_info("Fetching your organizations...")
        org_api = OrganizationAPI(config_manager)
        organizations = org_api.list_organizations()

        if not organizations:
            print_error("No organizations found for your account")
            raise typer.Exit(1)

        # Select organization
        if len(organizations) == 1:
            # Auto-select if only one org
            selected_org = organizations[0]
            print_success(f"Auto-selected organization: {selected_org['name']}")
        else:
            # Show interactive selection
            console.print("\n[bold]Select an organization:[/bold]\n")

            org_choices = []
            for org in organizations:
                role = org.get("userRole", "member")
                label = f"{org['name']} ({role})"
                org_choices.append({"name": label, "value": org})

            selected_org = inquirer.select(
                message="Select organization:",
                choices=org_choices,
            ).execute()

        # Save selected organization
        from janet.config.models import OrganizationInfo

        config = config_manager.get()
        config.selected_organization = OrganizationInfo(
            id=selected_org["id"], name=selected_org["name"], uuid=selected_org["uuid"]
        )
        config_manager.update(config)

        print_success(f"Selected organization: {selected_org['name']}")
        console.print("\n[green]✓ Authentication complete![/green]")
        console.print("Run 'janet sync' to start syncing tickets.")

    except JanetCLIError as e:
        print_error(str(e))
        raise typer.Exit(1)


@app.command(name="logout")
def logout() -> None:
    """Clear stored credentials."""
    try:
        config = config_manager.get()
        if not config_manager.is_authenticated():
            print_info("Not currently logged in")
            return

        # Clear authentication data
        config.auth.access_token = None
        config.auth.refresh_token = None
        config.auth.expires_at = None
        config.auth.user_id = None
        config.auth.user_email = None
        config.selected_organization = None

        config_manager.update(config)
        print_success("Logged out successfully")
    except JanetCLIError as e:
        print_error(str(e))
        raise typer.Exit(1)


@auth_app.command(name="status")
def auth_status() -> None:
    """Show current authentication status."""
    try:
        config = config_manager.get()

        if not config_manager.is_authenticated():
            console.print("[yellow]Not authenticated[/yellow]")
            console.print("Run 'janet login' to authenticate")
            return

        console.print("[bold green]Authenticated[/bold green]")
        if config.auth.user_email:
            console.print(f"User: [cyan]{config.auth.user_email}[/cyan]")
        if config.selected_organization:
            console.print(f"Organization: [cyan]{config.selected_organization.name}[/cyan]")
            console.print(f"Organization ID: [dim]{config.selected_organization.id}[/dim]")

        if config.auth.expires_at:
            console.print(f"Token expires: [dim]{config.auth.expires_at}[/dim]")
    except JanetCLIError as e:
        print_error(str(e))
        raise typer.Exit(1)


# =============================================================================
# Organization Commands
# =============================================================================


@org_app.command(name="list")
def org_list() -> None:
    """List available organizations."""
    try:
        from janet.api.organizations import OrganizationAPI
        from rich.table import Table

        if not config_manager.is_authenticated():
            print_error("Not authenticated. Run 'janet login' first.")
            raise typer.Exit(1)

        print_info("Fetching organizations...")
        org_api = OrganizationAPI(config_manager)
        organizations = org_api.list_organizations()

        if not organizations:
            print_info("No organizations found")
            return

        # Display as table
        table = Table(title="Organizations", show_header=True, header_style="bold cyan")
        table.add_column("ID", style="dim")
        table.add_column("Name", style="bold")
        table.add_column("Role")

        for org in organizations:
            table.add_row(
                org.get("id", ""), org.get("name", ""), org.get("userRole", "member")
            )

        console.print(table)
    except JanetCLIError as e:
        print_error(str(e))
        raise typer.Exit(1)


@org_app.command(name="select")
def org_select(org_id: str) -> None:
    """
    Switch active organization.

    Args:
        org_id: Organization ID to select
    """
    try:
        from janet.api.organizations import OrganizationAPI
        from janet.config.models import OrganizationInfo

        if not config_manager.is_authenticated():
            print_error("Not authenticated. Run 'janet login' first.")
            raise typer.Exit(1)

        print_info(f"Selecting organization: {org_id}")
        org_api = OrganizationAPI(config_manager)

        # Fetch organization details
        org_data = org_api.get_organization(org_id)

        # Update config
        config = config_manager.get()
        config.selected_organization = OrganizationInfo(
            id=org_data["id"], name=org_data["name"], uuid=org_data.get("uuid", org_id)
        )
        config_manager.update(config)

        print_success(f"Selected organization: {org_data['name']}")
    except JanetCLIError as e:
        print_error(str(e))
        raise typer.Exit(1)


@org_app.command(name="current")
def org_current() -> None:
    """Show current organization."""
    try:
        config = config_manager.get()

        if not config_manager.has_organization():
            print_info("No organization selected")
            console.print("Run 'janet org list' to see available organizations")
            return

        org = config.selected_organization
        console.print(f"[bold]Current Organization:[/bold]")
        console.print(f"  Name: [cyan]{org.name}[/cyan]")
        console.print(f"  ID: [dim]{org.id}[/dim]")
        console.print(f"  UUID: [dim]{org.uuid}[/dim]")
    except JanetCLIError as e:
        print_error(str(e))
        raise typer.Exit(1)


# =============================================================================
# Project Commands
# =============================================================================


@project_app.command(name="list")
def project_list() -> None:
    """List projects in current organization."""
    try:
        from janet.api.projects import ProjectAPI
        from rich.table import Table

        if not config_manager.is_authenticated():
            print_error("Not authenticated. Run 'janet login' first.")
            raise typer.Exit(1)

        if not config_manager.has_organization():
            print_error("No organization selected. Run 'janet org select' first.")
            raise typer.Exit(1)

        print_info("Fetching projects...")
        project_api = ProjectAPI(config_manager)
        projects = project_api.list_projects()

        if not projects:
            print_info("No projects found")
            return

        # Display as table
        table = Table(title="Projects", show_header=True, header_style="bold cyan")
        table.add_column("Key", style="bold")
        table.add_column("Name")
        table.add_column("Tickets", justify="right")
        table.add_column("Role")

        for project in projects:
            table.add_row(
                project.get("project_identifier", ""),
                project.get("project_name", ""),
                str(project.get("ticket_count", 0)),
                project.get("user_role", ""),
            )

        console.print(table)
    except JanetCLIError as e:
        print_error(str(e))
        raise typer.Exit(1)


# =============================================================================
# Sync Commands
# =============================================================================


@app.command(name="sync")
def sync(
    directory: Annotated[str, typer.Option("--dir", "-d", help="Sync directory")] = None,
    all_projects: Annotated[bool, typer.Option("--all", help="Sync all projects")] = False,
) -> None:
    """
    Sync tickets to local markdown files.

    Interactive mode: prompts for project selection and directory.
    """
    try:
        from janet.sync.sync_engine import SyncEngine
        from janet.api.projects import ProjectAPI
        import os

        if not config_manager.is_authenticated():
            print_error("Not authenticated. Run 'janet login' first.")
            raise typer.Exit(1)

        if not config_manager.has_organization():
            print_error("No organization selected. Run 'janet org select' first.")
            raise typer.Exit(1)

        org_name = config_manager.get().selected_organization.name

        # Step 1: Select projects to sync
        console.print(f"\n[bold]Sync tickets for {org_name}[/bold]\n")

        # Fetch projects
        print_info("Fetching projects...")
        project_api = ProjectAPI(config_manager)
        all_project_list = project_api.list_projects()

        if not all_project_list:
            print_error("No projects found")
            raise typer.Exit(1)

        # Filter out projects with no tickets
        available_projects = [p for p in all_project_list if p.get("ticket_count", 0) > 0]

        if not available_projects:
            print_info("No projects with tickets found")
            return

        # Show project selection
        selected_projects = []

        if all_projects:
            # Skip selection, use all projects
            selected_projects = available_projects
            console.print(f"Syncing all {len(selected_projects)} projects")
        else:
            # Interactive project selection with checkboxes
            from InquirerPy import inquirer

            console.print("\n[bold]Select projects to sync:[/bold]")
            console.print("[dim]Use ↑/↓ to move, SPACE to toggle selection, ENTER to confirm[/dim]\n")

            # Build choices with formatted display
            choices = []
            for project in available_projects:
                key = project.get("project_identifier", "")
                name = project.get("project_name", "")
                count = project.get("ticket_count", 0)
                label = f"{key:8s} - {name:30s} ({count} tickets)"
                choices.append({"name": label, "value": project, "enabled": True})

            # Show checkbox multi-select
            import sys
            import os as os_module

            # Temporarily suppress InquirerPy's result output
            selected = inquirer.checkbox(
                message="Select projects:",
                choices=choices,
                validate=lambda result: len(result) > 0 or "Please select at least one project",
                instruction="(SPACE to toggle, ENTER to confirm)",
                amark="✓",
                transformer=lambda result: "",  # Suppress the result display
            ).execute()

            if not selected:
                print_info("No projects selected")
                return

            selected_projects = selected

        # Show selected projects cleanly
        console.print(f"\n[green]✓ Selected {len(selected_projects)} project(s):[/green]")
        for proj in selected_projects:
            key = proj.get("project_identifier", "")
            name = proj.get("project_name", "")
            count = proj.get("ticket_count", 0)
            console.print(f"  • {key} - {name} ({count} tickets)")

        # Step 2: Select sync directory
        if directory:
            sync_dir = directory
        else:
            # Get current directory
            current_dir = os.getcwd()
            from InquirerPy import inquirer

            console.print(f"\n[bold]Where should tickets be synced?[/bold]")
            console.print(f"[dim]Current directory: {current_dir}[/dim]\n")

            # Build directory choices
            dir_choices = [
                {
                    "name": f"Current directory ({current_dir}/janet-tickets)",
                    "value": os.path.join(current_dir, "janet-tickets"),
                },
                {
                    "name": "Home directory (~/janet-tickets)",
                    "value": "~/janet-tickets",
                },
                {
                    "name": "Custom path...",
                    "value": "__custom__",
                },
            ]

            choice = inquirer.select(
                message="Select sync location:",
                choices=dir_choices,
            ).execute()

            if choice == "__custom__":
                sync_dir = inquirer.filepath(
                    message="Enter custom path:",
                    default=current_dir,
                    validate=lambda x: len(x) > 0 or "Path cannot be empty",
                ).execute()
                if not sync_dir:
                    print_info("Sync cancelled")
                    return
            else:
                sync_dir = choice

        # Expand path
        from janet.utils.paths import expand_path
        expanded_dir = expand_path(sync_dir)

        console.print(f"\n[green]✓ Sync directory: {expanded_dir}[/green]")

        # Confirm
        from InquirerPy import inquirer
        confirmed = inquirer.confirm(
            message=f"Sync {len(selected_projects)} project(s) to {expanded_dir}?",
            default=True,
        ).execute()

        if not confirmed:
            print_info("Sync cancelled")
            return

        # Step 3: Start sync
        console.print(f"\n[bold]Starting sync...[/bold]\n")

        # Update config with new directory
        config = config_manager.get()
        config.sync.root_directory = str(expanded_dir)
        config_manager.update(config)

        # Initialize sync engine with new directory
        sync_engine = SyncEngine(config_manager)

        # Sync selected projects
        total_tickets = 0
        for project in selected_projects:
            project_key = project.get("project_identifier", "")
            project_name = project.get("project_name", "")

            synced = sync_engine.sync_project(project["id"], project_key, project_name)
            total_tickets += synced

        # Generate README for AI agents
        from janet.sync.readme_generator import ReadmeGenerator
        readme_gen = ReadmeGenerator()
        readme_path = readme_gen.write_readme(
            sync_dir=expanded_dir,
            org_name=org_name,
            projects=selected_projects,
            total_tickets=total_tickets,
        )

        # Show summary
        console.print(f"\n[bold green]✓ Sync complete![/bold green]")
        console.print(f"  Projects: {len(selected_projects)}")
        console.print(f"  Tickets: {total_tickets}")
        console.print(f"\n[cyan]Tickets saved to: {expanded_dir}[/cyan]")
        console.print(f"[dim]README for AI agents: {readme_path}[/dim]")

    except JanetCLIError as e:
        print_error(str(e))
        raise typer.Exit(1)
    except Exception as e:
        print_error(f"Sync failed: {e}")
        raise typer.Exit(1)


# =============================================================================
# Status Command
# =============================================================================


@app.command(name="status")
def status() -> None:
    """Show overall status (auth, org, last sync)."""
    try:
        config = config_manager.get()

        console.print("[bold]Janet CLI Status[/bold]\n")

        # Authentication status
        if config_manager.is_authenticated():
            console.print("✓ [green]Authenticated[/green]")
            if config.auth.user_email:
                console.print(f"  User: {config.auth.user_email}")
        else:
            console.print("✗ [yellow]Not authenticated[/yellow]")
            console.print("  Run 'janet login' to authenticate\n")
            return

        # Organization status
        if config_manager.has_organization():
            console.print(f"✓ [green]Organization selected: {config.selected_organization.name}[/green]")
        else:
            console.print("✗ [yellow]No organization selected[/yellow]")
            console.print("  Run 'janet org list' to select an organization\n")
            return

        # Sync status
        console.print(f"\n[bold]Sync Directory:[/bold] {config.sync.root_directory}")
        if config.sync.last_sync_times:
            console.print(f"[bold]Last Synced Projects:[/bold] {len(config.sync.last_sync_times)}")
        else:
            console.print("[dim]No projects synced yet[/dim]")
    except JanetCLIError as e:
        print_error(str(e))
        raise typer.Exit(1)


# =============================================================================
# Config Commands
# =============================================================================


@config_app.command(name="show")
def config_show() -> None:
    """Display current configuration."""
    try:
        config = config_manager.get()
        console.print_json(config.model_dump_json(indent=2))
    except JanetCLIError as e:
        print_error(str(e))
        raise typer.Exit(1)


@config_app.command(name="path")
def config_path() -> None:
    """Show config file location."""
    console.print(f"Config file: [cyan]{config_manager.config_path}[/cyan]")


@config_app.command(name="reset")
def config_reset(
    confirm: Annotated[bool, typer.Option("--yes", "-y", help="Skip confirmation")] = False,
) -> None:
    """Reset configuration to defaults."""
    try:
        if not confirm:
            console.print("[yellow]This will reset all configuration to defaults.[/yellow]")
            confirmed = typer.confirm("Are you sure?")
            if not confirmed:
                print_info("Reset cancelled")
                return

        config_manager.reset()
        print_success("Configuration reset to defaults")
    except JanetCLIError as e:
        print_error(str(e))
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
