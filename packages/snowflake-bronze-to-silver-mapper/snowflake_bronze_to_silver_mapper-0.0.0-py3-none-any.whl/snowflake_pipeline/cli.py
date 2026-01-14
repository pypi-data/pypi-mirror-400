import click
import os
import sys
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from .docker_manager import DockerManager
from .config import Config

console = Console()

SUPPORTED_DOMAINS = {
    'cpg': {
        'name': 'Consumer Packaged Goods',
        'description': 'Retail and consumer products data',
        'tables': ['vendor_master', 'product_master', 'sales_data', 'customer_data']
    },
    'bfsi': {
        'name': 'Banking & Financial Services',
        'description': 'Financial transactions and banking data',
        'tables': ['raw_global_incoterms', 'raw_document_tracking']
    },
    'hospital': {
        'name': 'Healthcare Management',
        'description': 'Medical and healthcare data systems',
        'tables': ['patient_master']
    }
}

@click.group()
@click.version_option(version="0.1.0")
def main():
    """Snowflake Bronze to Silver Mapper - Simplify your data layer transformations."""
    pass

@main.command()
@click.option('--path', default='.', help='Installation directory')
@click.option('--domain', 
              type=click.Choice(list(SUPPORTED_DOMAINS.keys()) + ['custom'], case_sensitive=False),
              default='cpg',
              help='Domain type for pipeline templates')
def init(path, domain):
    """Initialize a new Bronze to Silver mapping project."""
    
    # Show welcome banner
    console.print(Panel.fit(
        "[bold blue]Snowflake Bronze to Silver Mapper[/bold blue]\n"
        "Setting up your data transformation environment...",
        border_style="blue"
    ))
    
    # Show domain info
    if domain != 'custom':
        domain_info = SUPPORTED_DOMAINS[domain]
        console.print(f"\n[cyan]Domain:[/cyan] {domain_info['name']}")
        console.print(f"[cyan]Description:[/cyan] {domain_info['description']}")
        console.print(f"[cyan]Example Tables:[/cyan] {', '.join(domain_info['tables'])}")
    else:
        console.print(f"\n[cyan]Domain:[/cyan] Custom (you'll configure manually)")
    
    install_path = Path(path).resolve()
    install_path.mkdir(parents=True, exist_ok=True)
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task1 = progress.add_task("Creating project structure...", total=None)
        Config.create_project_structure(install_path)
        progress.update(task1, completed=True)
        
        task2 = progress.add_task("Copying templates...", total=None)
        Config.copy_templates(install_path)
        progress.update(task2, completed=True)
        
        task3 = progress.add_task("Creating configuration files...", total=None)
        Config.create_env_file(install_path)
        Config.create_domain_config(install_path, domain)
        progress.update(task3, completed=True)
        
        if domain != 'custom':
            task4 = progress.add_task(f"Setting up {domain.upper()} domain templates...", total=None)
            Config.setup_domain_templates(install_path, domain)
            progress.update(task4, completed=True)
    
    console.print(f"\n[green]✓[/green] Project initialized in: {install_path}")
    console.print(f"[green]✓[/green] Domain: {domain.upper()}")
    
    console.print("\n[yellow]Next steps:[/yellow]")
    console.print("1. Edit .env file with your Snowflake credentials")
    console.print(f"2. Review domain-config.json for {domain.upper()} settings")
    console.print("3. Run: bronze-to-silver start")
    console.print("4. Open: http://localhost:3000")

@main.command()
def domains():
    """List all supported domains."""
    console.print("\n[bold]Supported Domains for Bronze to Silver Mapping:[/bold]\n")
    
    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Domain", style="cyan", width=15)
    table.add_column("Name", style="white", width=30)
    table.add_column("Description", style="dim")
    
    for domain_key, domain_info in SUPPORTED_DOMAINS.items():
        table.add_row(
            domain_key.upper(),
            domain_info['name'],
            domain_info['description']
        )
    
    table.add_row(
        "CUSTOM",
        "Custom Domain",
        "Configure your own domain-specific transformations"
    )
    
    console.print(table)
    console.print("\n[dim]Use: bronze-to-silver init --domain <domain>[/dim]")

@main.command()
@click.option('--path', default='.', help='Project directory')
@click.option('--detached', '-d', is_flag=True, help='Run in detached mode')
def start(path, detached):
    """Start the Bronze to Silver Mapper services."""
    project_path = Path(path).resolve()
    
    if not (project_path / 'docker-compose.yml').exists():
        console.print("[red]Error:[/red] docker-compose.yml not found.")
        console.print("Run 'bronze-to-silver init' first.")
        sys.exit(1)
    
    # Check if domain config exists
    domain_config = project_path / 'domain-config.json'
    if domain_config.exists():
        import json
        with open(domain_config) as f:
            config = json.load(f)
            console.print(f"[cyan]Starting with domain:[/cyan] {config.get('domain', 'unknown').upper()}")
    
    manager = DockerManager(project_path)
    
    console.print("[blue]Starting services...[/blue]")
    success = manager.start(detached=detached)
    
    if success:
        console.print("\n[green]✓[/green] Services started successfully!")
        console.print("\n[bold]Access your Bronze to Silver Mapper:[/bold]")
        console.print("  • Frontend UI: http://localhost:3000")
        console.print("  • Backend API: http://localhost:8000")
        console.print("  • API Docs:    http://localhost:8000/docs")
        
        if not detached:
            console.print("\n[yellow]Press Ctrl+C to stop[/yellow]")
    else:
        console.print("[red]Failed to start services. Check logs with: bronze-to-silver logs[/red]")
        sys.exit(1)

@main.command()
@click.option('--path', default='.', help='Project directory')
def stop(path):
    """Stop the Bronze to Silver Mapper services."""
    project_path = Path(path).resolve()
    manager = DockerManager(project_path)
    
    console.print("[blue]Stopping services...[/blue]")
    success = manager.stop()
    
    if success:
        console.print("[green]✓[/green] Services stopped successfully!")
    else:
        console.print("[red]Failed to stop services[/red]")
        sys.exit(1)

@main.command()
@click.option('--path', default='.', help='Project directory')
@click.option('--follow', '-f', is_flag=True, help='Follow log output')
@click.option('--tail', default=100, help='Number of lines to show')
def logs(path, follow, tail):
    """View service logs."""
    project_path = Path(path).resolve()
    manager = DockerManager(project_path)
    
    manager.logs(follow=follow, tail=tail)

@main.command()
@click.option('--path', default='.', help='Project directory')
def status(path):
    """Check service status."""
    project_path = Path(path).resolve()
    manager = DockerManager(project_path)
    
    status = manager.status()
    
    if status:
        console.print("\n[bold]Service Status:[/bold]")
        for service, info in status.items():
            state = info.get('state', 'unknown')
            color = 'green' if state == 'running' else 'red'
            console.print(f"  • {service}: [{color}]{state}[/{color}]")
    else:
        console.print("[yellow]No services running[/yellow]")

@main.command()
@click.option('--path', default='.', help='Project directory')
def restart(path):
    """Restart all services."""
    project_path = Path(path).resolve()
    manager = DockerManager(project_path)
    
    console.print("[blue]Restarting services...[/blue]")
    success = manager.restart()
    
    if success:
        console.print("[green]✓[/green] Services restarted successfully!")
    else:
        console.print("[red]Failed to restart services[/red]")
        sys.exit(1)

@main.command()
@click.option('--path', default='.', help='Project directory')
@click.option('--volumes', is_flag=True, help='Remove volumes as well')
def down(path, volumes):
    """Stop and remove all containers."""
    project_path = Path(path).resolve()
    manager = DockerManager(project_path)
    
    console.print("[blue]Removing containers...[/blue]")
    success = manager.down(remove_volumes=volumes)
    
    if success:
        console.print("[green]✓[/green] Containers removed successfully!")
    else:
        console.print("[red]Failed to remove containers[/red]")
        sys.exit(1)

@main.command()
@click.option('--path', default='.', help='Project directory')
def health(path):
    """Check application health."""
    import requests
    
    try:
        response = requests.get('http://localhost:8000/health', timeout=5)
        if response.status_code == 200:
            data = response.json()
            console.print("\n[green]✓[/green] Backend is healthy!")
            console.print(f"  • Database: {data.get('database')}")
            console.print(f"  • Snowflake: {'configured' if data.get('snowflake_configured') else 'not configured'}")
        else:
            console.print("[red]Backend is not responding correctly[/red]")
    except requests.exceptions.RequestException:
        console.print("[red]Cannot connect to backend. Is it running?[/red]")
        console.print("Run: bronze-to-silver start")

@main.command()
@click.option('--path', default='.', help='Project directory')
def info(path):
    """Show project information and configuration."""
    project_path = Path(path).resolve()
    
    # Check if initialized
    if not (project_path / 'docker-compose.yml').exists():
        console.print("[red]Error:[/red] Project not initialized.")
        console.print("Run 'bronze-to-silver init' first.")
        sys.exit(1)
    
    console.print(f"\n[bold]Project Information:[/bold]")
    console.print(f"  • Location: {project_path}")
    
    # Read domain config
    domain_config_path = project_path / 'domain-config.json'
    if domain_config_path.exists():
        import json
        with open(domain_config_path) as f:
            config = json.load(f)
            console.print(f"  • Domain: {config.get('domain', 'unknown').upper()}")
            console.print(f"  • Description: {config.get('description', 'N/A')}")
    
    # Check .env file
    env_file = project_path / '.env'
    if env_file.exists():
        console.print(f"  • Environment: Configured (.env exists)")
    else:
        console.print(f"  • Environment: [yellow]Not configured (missing .env)[/yellow]")
    
    # Check if services are running
    manager = DockerManager(project_path)
    status = manager.status()
    if status:
        running_count = sum(1 for s in status.values() if s.get('state') == 'running')
        console.print(f"  • Services: {running_count}/{len(status)} running")
    else:
        console.print(f"  • Services: Not running")

if __name__ == '__main__':
    main()
