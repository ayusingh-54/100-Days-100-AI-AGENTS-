"""
Lead Generation Agent - CLI Interface.
Command-line interface for running the lead generation agent.
"""

import click
import json
import logging
from typing import Optional, List
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from lead_gen_agent.graph import create_workflow
from lead_gen_agent.storage import get_storage
from lead_gen_agent.models import PriorityBucket

console = Console()
logging.basicConfig(level=logging.INFO)


@click.group()
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
def cli(verbose: bool):
    """Lead Generation Agent - Find and score B2B leads."""
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)


@cli.command()
@click.argument("query")
@click.option("--sources", "-s", multiple=True, default=["web_search"], 
              help="Data sources: linkedin, web_search")
@click.option("--max-results", "-n", default=10, help="Maximum results")
@click.option("--industries", "-i", multiple=True, help="Target industries")
@click.option("--locations", "-l", multiple=True, help="Target locations")
@click.option("--output", "-o", help="Output file (JSON)")
def search(
    query: str,
    sources: tuple,
    max_results: int,
    industries: tuple,
    locations: tuple,
    output: Optional[str],
):
    """
    Search for leads matching a query.
    
    Example: lead-gen search "AI startups" -s web_search -n 20
    """
    console.print(Panel(f"[bold blue]Searching for leads: {query}[/bold blue]"))
    
    # Build ICP config
    icp_config = {}
    if industries:
        icp_config["target_industries"] = list(industries)
    if locations:
        icp_config["target_geographies"] = list(locations)
    
    # Create workflow
    workflow = create_workflow()
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Generating leads...", total=None)
        
        result = workflow.run(
            query=query,
            sources=list(sources),
            icp_config=icp_config,
            max_results=max_results,
        )
        
        progress.update(task, completed=True)
    
    # Display results
    if result["success"]:
        leads = result["leads"]
        stats = result["statistics"]
        
        console.print(f"\n[green]✓ Found {len(leads)} leads[/green]")
        
        # Statistics
        console.print(Panel(
            f"High Priority: {stats.get('high_priority', 0)} | "
            f"Medium: {stats.get('medium_priority', 0)} | "
            f"Low: {stats.get('low_priority', 0)} | "
            f"Avg Score: {stats.get('avg_score', 0)}",
            title="Statistics"
        ))
        
        # Results table
        table = Table(title="Lead Results", show_lines=True)
        table.add_column("Company", style="cyan")
        table.add_column("Industry", style="green")
        table.add_column("Location", style="yellow")
        table.add_column("Score", style="magenta", justify="right")
        table.add_column("Priority", style="red")
        
        for lead in leads[:20]:  # Show top 20
            priority_color = {
                "HIGH": "[red]HIGH[/red]",
                "MEDIUM": "[yellow]MEDIUM[/yellow]",
                "LOW": "[green]LOW[/green]",
            }.get(lead.get("priority", "MEDIUM"), "MEDIUM")
            
            table.add_row(
                lead.get("company_name", "N/A")[:30],
                lead.get("industry", "N/A")[:20],
                lead.get("location", "N/A")[:20],
                str(round(lead.get("lead_score", 0), 1)),
                priority_color,
            )
        
        console.print(table)
        
        # Save output
        if output:
            with open(output, "w") as f:
                json.dump(result, f, indent=2, default=str)
            console.print(f"\n[green]Results saved to {output}[/green]")
    
    else:
        console.print(f"[red]✗ Search failed: {result.get('errors', [])}[/red]")


@cli.command()
@click.option("--priority", "-p", type=click.Choice(["HIGH", "MEDIUM", "LOW"]), 
              help="Filter by priority")
@click.option("--min-score", type=float, help="Minimum score filter")
@click.option("--search", "-q", help="Search query")
@click.option("--format", "-f", type=click.Choice(["table", "json"]), default="table",
              help="Output format")
def list_leads(
    priority: Optional[str],
    min_score: Optional[float],
    search: Optional[str],
    format: str,
):
    """List stored leads with optional filters."""
    storage = get_storage()
    
    # Get leads
    if priority:
        leads = storage.get_leads_by_priority(PriorityBucket(priority))
    elif min_score:
        leads = storage.get_leads_by_score(min_score)
    elif search:
        leads = storage.search_leads(search)
    else:
        leads = storage.get_all_leads()
    
    if format == "json":
        output = [lead.model_dump() for lead in leads]
        console.print_json(json.dumps(output, indent=2, default=str))
    else:
        if not leads:
            console.print("[yellow]No leads found.[/yellow]")
            return
        
        table = Table(title=f"Leads ({len(leads)} total)", show_lines=True)
        table.add_column("Company", style="cyan")
        table.add_column("Industry", style="green")
        table.add_column("Location", style="yellow")
        table.add_column("Score", style="magenta", justify="right")
        table.add_column("Priority", style="red")
        
        for lead in leads:
            table.add_row(
                (lead.company_name or "N/A")[:30],
                (lead.industry or "N/A")[:20],
                (lead.location or "N/A")[:20],
                str(round(lead.lead_score or 0, 1)),
                lead.priority.value if lead.priority else "N/A",
            )
        
        console.print(table)


@cli.command()
@click.option("--output", "-o", required=True, help="Output CSV file")
def export(output: str):
    """Export leads to CSV."""
    storage = get_storage()
    
    if storage.export_to_csv(output):
        console.print(f"[green]✓ Exported to {output}[/green]")
    else:
        console.print("[red]✗ Export failed[/red]")


@cli.command()
def stats():
    """Show lead storage statistics."""
    storage = get_storage()
    statistics = storage.get_statistics()
    
    console.print(Panel(
        f"Total Leads: {statistics['total_leads']}\n"
        f"High Priority: {statistics['by_priority']['HIGH']}\n"
        f"Medium Priority: {statistics['by_priority']['MEDIUM']}\n"
        f"Low Priority: {statistics['by_priority']['LOW']}\n"
        f"Average Score: {statistics['average_score']}\n"
        f"Storage Type: {statistics['storage_type']}",
        title="Lead Statistics"
    ))


@cli.command()
@click.confirmation_option(prompt="Are you sure you want to clear all leads?")
def clear():
    """Clear all stored leads."""
    storage = get_storage()
    storage.clear_all()
    console.print("[green]✓ All leads cleared[/green]")


def main():
    """Entry point for CLI."""
    cli()


if __name__ == "__main__":
    main()
