"""
API-ARM CLI - Command Line Interface for API-ARM.

Provides a terminal interface for analyzing and making requests to APIs.
"""

import asyncio
from typing import Optional
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax
from rich import print as rprint
import json

from apiarm import APIArm, __version__
from apiarm.core.analyzer import AnalysisDepth
from apiarm.models.endpoint import HTTPMethod, AuthMethod
from apiarm.core.config import ConfigManager

app = typer.Typer(
    name="apiarm",
    help="API-ARM: Application Programming Interface with Automated Request Manipulator",
    add_completion=False,
)

config_app = typer.Typer(help="Manage local configuration")
app.add_typer(config_app, name="config")
console = Console()


def version_callback(value: bool):
    if value:
        console.print(f"[bold blue]API-ARM[/bold blue] version [green]{__version__}[/green]")
        raise typer.Exit()


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        callback=version_callback,
        is_eager=True,
        help="Show version and exit",
    ),
):
    """API-ARM: Analyze APIs and make secure requests."""
    pass


@app.command()
def analyze(
    url: str = typer.Argument(..., help="Base URL of the API to analyze"),
    depth: str = typer.Option(
        "standard",
        "--depth",
        "-d",
        help="Analysis depth: shallow, standard, deep, or smart (AI)",
    ),
    output: Optional[str] = typer.Option(
        None,
        "--output",
        "-o",
        help="Output file for analysis results (JSON)",
    ),
):
    """
    Analyze an API to discover its structure and capabilities.
    
    Examples:
        apiarm analyze https://api.example.com
        apiarm analyze https://api.example.com --depth deep
        apiarm analyze https://api.example.com -o analysis.json
    """
    depth_map = {
        "shallow": AnalysisDepth.SHALLOW,
        "standard": AnalysisDepth.STANDARD,
        "deep": AnalysisDepth.DEEP,
        "smart": AnalysisDepth.SMART,
    }
    
    analysis_depth = depth_map.get(depth.lower(), AnalysisDepth.STANDARD)
    
    async def run_analysis():
        console.print(f"\n[bold blue]🔍 Analyzing API:[/bold blue] {url}\n")
        
        try:
            async with APIArm(url) as arm:
                with console.status("[bold green]Analyzing..."):
                    result = await arm.analyze(depth=analysis_depth)
                    
                # Display results
                display_analysis_results(result)
                
                # Save to file if requested
                if output:
                    with open(output, "w") as f:
                        json.dump(result.to_dict(), f, indent=2)
                    console.print(f"\n[green]✓ Results saved to {output}[/green]")
                    
        except Exception as e:
            console.print(f"[red]✗ Error: {e}[/red]")
            raise typer.Exit(1)
            
    asyncio.run(run_analysis())


def display_analysis_results(result):
    """Display analysis results in a formatted table."""
    # Summary panel
    summary = f"""
[bold]Base URL:[/bold] {result.base_url}
[bold]API Version:[/bold] {result.api_version or 'Unknown'}
[bold]Documentation:[/bold] {result.documentation_url or 'Not found'}
[bold]Response Formats:[/bold] {', '.join(result.response_formats)}
[bold]Auth Methods:[/bold] {', '.join(am.value for am in result.auth_methods)}
"""
    console.print(Panel(summary, title="[bold]API Analysis Summary[/bold]", border_style="blue"))
    
    # Endpoints table
    if result.endpoints:
        table = Table(title="Discovered Endpoints")
        table.add_column("Path", style="cyan")
        table.add_column("Methods", style="green")
        table.add_column("Auth Required", style="yellow")
        table.add_column("Description")
        
        for endpoint in result.endpoints:
            methods = ", ".join(m.value for m in endpoint.methods)
            auth = "Yes" if endpoint.requires_auth else "No"
            table.add_row(
                endpoint.path,
                methods,
                auth,
                endpoint.description[:50] + "..." if len(endpoint.description) > 50 else endpoint.description,
            )
            
        console.print(table)
    else:
        console.print("[yellow]No endpoints discovered. Try using --depth deep[/yellow]")
        
    # Rate limits
    if result.rate_limits:
        console.print("\n[bold]Rate Limits:[/bold]")
        for key, value in result.rate_limits.items():
            console.print(f"  {key}: {value}")


@app.command()
def request(
    url: str = typer.Argument(..., help="Full URL to request"),
    method: str = typer.Option(
        "GET",
        "--method",
        "-m",
        help="HTTP method",
    ),
    data: Optional[str] = typer.Option(
        None,
        "--data",
        "-d",
        help="JSON data for POST/PUT/PATCH requests",
    ),
    header: Optional[list[str]] = typer.Option(
        None,
        "--header",
        "-H",
        help="Headers in 'Key: Value' format (can be repeated)",
    ),
    api_key: Optional[str] = typer.Option(
        None,
        "--api-key",
        "-k",
        help="API key for authentication",
    ),
    bearer: Optional[str] = typer.Option(
        None,
        "--bearer",
        "-b",
        help="Bearer token for authentication",
    ),
):
    """
    Make a request to an API endpoint.
    
    Examples:
        apiarm request https://api.example.com/users
        apiarm request https://api.example.com/users -m POST -d '{"name": "John"}'
        apiarm request https://api.example.com/users -H "Accept: application/json"
    """
    async def run_request():
        # Parse headers
        headers = {}
        if header:
            for h in header:
                if ": " in h:
                    key, value = h.split(": ", 1)
                    headers[key] = value
                    
        # Parse JSON data
        json_data = None
        if data:
            try:
                json_data = json.loads(data)
            except json.JSONDecodeError:
                console.print("[red]✗ Invalid JSON data[/red]")
                raise typer.Exit(1)
                
        http_method = HTTPMethod(method.upper())
        
        console.print(f"\n[bold blue]📡 Making {method} request to:[/bold blue] {url}\n")
        
        try:
            async with APIArm(url, headers=headers) as arm:
                # Configure auth
                if api_key:
                    arm.set_api_key(api_key)
                elif bearer:
                    arm.set_bearer_token(bearer)
                    
                with console.status("[bold green]Requesting..."):
                    response = await arm.request(
                        "",  # Empty path since full URL is the base
                        method=http_method,
                        json_body=json_data,
                    )
                    
                # Display response
                display_response(response)
                
        except Exception as e:
            console.print(f"[red]✗ Error: {e}[/red]")
            raise typer.Exit(1)
            
    asyncio.run(run_request())


def display_response(response):
    """Display API response in a formatted way."""
    # Status
    status_color = "green" if response.success else "red"
    status_icon = "✓" if response.success else "✗"
    console.print(f"[{status_color}]{status_icon} Status: {response.status_code}[/{status_color}]")
    
    # Headers
    if response.headers:
        console.print("\n[bold]Response Headers:[/bold]")
        for key, value in list(response.headers.items())[:10]:
            console.print(f"  [dim]{key}:[/dim] {value}")
            
    # Body
    if response.data:
        console.print("\n[bold]Response Body (JSON):[/bold]")
        json_str = json.dumps(response.data, indent=2)
        syntax = Syntax(json_str, "json", theme="monokai", line_numbers=True)
        console.print(syntax)
    elif response.text:
        console.print("\n[bold]Response Body:[/bold]")
        console.print(response.text[:1000])
        if len(response.text) > 1000:
            console.print("[dim]... (truncated)[/dim]")


@app.command()
def interactive():
    """
    Start an interactive session for exploring an API.
    """
    console.print(Panel(
        "[bold]API-ARM Interactive Mode[/bold]\n\n"
        "Enter commands to analyze and interact with APIs.\n"
        "Type 'help' for available commands, 'exit' to quit.",
        title="🦾 API-ARM",
        border_style="blue",
    ))
    
    rprint("[yellow]Interactive mode coming soon![/yellow]")


@app.command()
def setup():
    """
    Initial setup for API-ARM. Prompts for API tokens and configuration.
    """
    console.print(Panel(
        "[bold green]API-ARM Setup[/bold green]\n\n"
        "Let's configure API-ARM for your machine. This information will be "
        "stored locally in your home directory.",
        title="🦾 Setup",
    ))
    
    config = ConfigManager()
    
    # GitHub Token
    token = typer.prompt(
        "Enter your GitHub Personal Access Token (for AI analysis)",
        hide_input=True,
    )
    if token:
        config.github_token = token
        console.print("[green]✔ GitHub token saved.[/green]")
        
    console.print("\n[bold green]Setup complete![/bold green] You can now use API-ARM with AI capabilities.")


@config_app.command("set-token")
def set_token(token: str = typer.Argument(..., help="GitHub Personal Access Token")):
    """
    Set the GitHub Personal Access Token for AI analysis.
    """
    config = ConfigManager()
    config.github_token = token
    console.print("[green]✔ GitHub token updated successfully.[/green]")


@config_app.command("show")
def show_config():
    """
    Show current configuration.
    """
    config = ConfigManager()
    
    table = Table(title="API-ARM Configuration")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")
    
    github_token = config.github_token
    if github_token:
        # Mask the token
        masked = f"{github_token[:8]}...{github_token[-4:]}"
        table.add_row("GitHub Token", masked)
    else:
        table.add_row("GitHub Token", "[red]Not set[/red]")
        
    table.add_row("Config Path", str(config.config_path))
    
    console.print(table)


if __name__ == "__main__":
    app()
