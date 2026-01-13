"""Project management commands."""

import json
import zipfile
import tempfile
import click
from pathlib import Path
from rich.console import Console
from rich.table import Table
from langflow_cli.api_client import LangflowAPIClient
from langflow_cli.utils import print_json


console = Console()


@click.group()
def projects():
    """Manage Langflow projects."""
    pass


@projects.command()
@click.option("--profile", help="Profile to use (overrides default)")
def list(profile: str):
    """List all projects."""
    try:
        client = LangflowAPIClient(profile_name=profile if profile else None)
        projects_list = client.list_projects()
        
        if not projects_list:
            console.print("[yellow]No projects found.[/yellow]")
            return
        
        table = Table(title="Projects")
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="magenta")
        
        for project in projects_list:
            project_id = project.get("id", project.get("project_id", "N/A"))
            project_name = project.get("name", "Unnamed")
            table.add_row(str(project_id), project_name)
        
        console.print(table)
    except Exception as e:
        console.print(f"[red]✗[/red] Failed to list projects: {str(e)}")
        raise click.Abort()


@projects.command()
@click.argument("project_id")
@click.option("--profile", help="Profile to use (overrides default)")
def get(project_id: str, profile: str):
    """Get project details by ID."""
    try:
        client = LangflowAPIClient(profile_name=profile if profile else None)
        project = client.get_project(project_id)
        print_json(project, console)
    except Exception as e:
        console.print(f"[red]✗[/red] Failed to get project: {str(e)}")
        raise click.Abort()


@projects.command()
@click.option("--name", required=True, help="Project name")
@click.option("--data", help="Additional project data as JSON string")
@click.option("--profile", help="Profile to use (overrides default)")
def create(name: str, data: str, profile: str):
    """Create a new project."""
    try:
        client = LangflowAPIClient(profile_name=profile if profile else None)
        
        project_data = {}
        if data:
            project_data = json.loads(data)
        
        project = client.create_project(name, project_data)
        console.print(f"[green]✓[/green] Project created successfully")
        print_json(project, console)
    except json.JSONDecodeError:
        console.print(f"[red]✗[/red] Invalid JSON in --data option")
        raise click.Abort()
    except Exception as e:
        console.print(f"[red]✗[/red] Failed to create project: {str(e)}")
        raise click.Abort()


@projects.command()
@click.argument("project_id")
@click.option("--data", required=True, help="Project data as JSON string")
@click.option("--profile", help="Profile to use (overrides default)")
def update(project_id: str, data: str, profile: str):
    """Update an existing project."""
    try:
        client = LangflowAPIClient(profile_name=profile if profile else None)
        
        project_data = json.loads(data)
        project = client.update_project(project_id, project_data)
        console.print(f"[green]✓[/green] Project updated successfully")
        print_json(project, console)
    except json.JSONDecodeError:
        console.print(f"[red]✗[/red] Invalid JSON in --data option")
        raise click.Abort()
    except Exception as e:
        console.print(f"[red]✗[/red] Failed to update project: {str(e)}")
        raise click.Abort()


@projects.command()
@click.argument("project_id")
@click.option("--profile", help="Profile to use (overrides default)")
@click.confirmation_option(prompt="Are you sure you want to delete this project?")
def delete(project_id: str, profile: str):
    """Delete a project."""
    try:
        client = LangflowAPIClient(profile_name=profile if profile else None)
        client.delete_project(project_id)
        console.print(f"[green]✓[/green] Project '{project_id}' deleted successfully")
    except Exception as e:
        console.print(f"[red]✗[/red] Failed to delete project: {str(e)}")
        raise click.Abort()


@projects.command()
@click.argument("project_id")
@click.option("--profile", help="Profile to use (overrides default)")
def list_flows(project_id: str, profile: str):
    """List all flows for a specific project."""
    try:
        client = LangflowAPIClient(profile_name=profile if profile else None)
        flows_list = client.list_flows(project_id=project_id)
        
        if not flows_list:
            console.print(f"[yellow]No flows found for project '{project_id}'.[/yellow]")
            return
        
        table = Table(title=f"Flows for Project {project_id}")
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="magenta")
        table.add_column("Description", style="green")
        
        for flow in flows_list:
            flow_id = flow.get("id", flow.get("flow_id", "N/A"))
            flow_name = flow.get("name", "Unnamed")
            flow_description = flow.get("description", "N/A")
            table.add_row(str(flow_id), flow_name, flow_description or "N/A")
        
        console.print(table)
    except Exception as e:
        console.print(f"[red]✗[/red] Failed to list flows: {str(e)}")
        raise click.Abort()


@projects.command()
@click.argument("project_id")
@click.option("--file", type=click.Path(path_type=Path), required=True, help="Output file path for the zip file")
@click.option("--profile", help="Profile to use (overrides default)")
def export(project_id: str, file: Path, profile: str):
    """Export a project as a zip file containing all flows as JSON files."""
    try:
        client = LangflowAPIClient(profile_name=profile if profile else None)
        
        console.print(f"[cyan]Fetching project '{project_id}'...[/cyan]")
        
        # Get project details
        project = client.get_project(project_id)
        project_name = project.get("name", project_id)
        
        # Get all flows for this project
        console.print(f"[cyan]Fetching flows for project...[/cyan]")
        flows_list = client.list_flows(project_id=project_id)
        
        if not flows_list:
            console.print(f"[yellow]No flows found for project '{project_id}'.[/yellow]")
            # Still create a zip with just the project info
            flows_list = []
        
        # Create a temporary directory to store JSON files
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Save project info as JSON
            project_file = temp_path / "project.json"
            with open(project_file, 'w', encoding='utf-8') as f:
                json.dump(project, f, indent=2, ensure_ascii=False)
            
            # Save each flow as a JSON file
            flows_dir = temp_path / "flows"
            flows_dir.mkdir(exist_ok=True)
            
            for flow in flows_list:
                flow_id = flow.get("id", flow.get("flow_id", "unknown"))
                flow_name = flow.get("name", "unnamed_flow")
                # Sanitize filename
                safe_name = "".join(c for c in flow_name if c.isalnum() or c in (' ', '-', '_')).strip()
                safe_name = safe_name.replace(' ', '_')[:50]  # Limit length
                flow_filename = f"{safe_name}_{flow_id}.json"
                flow_file = flows_dir / flow_filename
                
                with open(flow_file, 'w', encoding='utf-8') as f:
                    json.dump(flow, f, indent=2, ensure_ascii=False)
            
            # Create zip file
            console.print(f"[cyan]Creating zip file...[/cyan]")
            
            # Ensure the output directory exists
            file.parent.mkdir(parents=True, exist_ok=True)
            
            with zipfile.ZipFile(file, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Add project file
                zipf.write(project_file, "project.json")
                
                # Add all flow files
                for flow_file in flows_dir.glob("*.json"):
                    zipf.write(flow_file, f"flows/{flow_file.name}")
            
            file_size = file.stat().st_size / 1024  # Size in KB
            console.print(f"[green]✓[/green] Project exported successfully to: {file}")
            console.print(f"[dim]Project: {project_name}[/dim]")
            console.print(f"[dim]Flows exported: {len(flows_list)}[/dim]")
            console.print(f"[dim]File size: {file_size:.2f} KB[/dim]")
            
    except Exception as e:
        console.print(f"[red]✗[/red] Failed to export project: {str(e)}")
        raise click.Abort()

