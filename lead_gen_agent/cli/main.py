"""
CLI interface for the Lead Generation Agent.
Provides command-line access to the workflow.
"""

import click
import json
import csv
from typing import Optional, List
from pathlib import Path
import logging

from ..graph import run_lead_gen_workflow
from ..models import ICPConfig, ScoringWeights
from ..config import Config
from ..utils import setup_logging

logger = logging.getLogger(__name__)


@click.group()
@click.option(
    "--debug",
    is_flag=True,
    help="Enable debug logging"
)
def cli(debug: bool):
    """
    Lead Generation Agent CLI.
    
    A powerful CLI tool for finding, enriching, and scoring B2B sales leads
    using AI, web scraping, and intelligent matching against your ICP.
    """
    setup_logging("DEBUG" if debug else "INFO")


@cli.command()
@click.option(
    "--keywords",
    required=True,
    help="Job keywords or titles to search (e.g., 'Data Engineer', 'Product Manager')"
)
@click.option(
    "--location",
    default="United States",
    help="Geographic location for search"
)
@click.option(
    "--sources",
    multiple=True,
    default=["linkedin"],
    type=click.Choice(["linkedin", "google_maps", "csv"]),
    help="Data sources to use for lead generation"
)
@click.option(
    "--max-leads",
    default=50,
    type=int,
    help="Maximum number of leads to generate"
)
@click.option(
    "--industries",
    multiple=True,
    help="Target industries (e.g., 'SaaS', 'Healthcare')"
)
@click.option(
    "--company-sizes",
    multiple=True,
    type=click.Choice(["micro", "small", "mid", "enterprise"]),
    help="Target company sizes"
)
@click.option(
    "--tech-stack",
    multiple=True,
    help="Preferred technologies in stack"
)
@click.option(
    "--output",
    type=click.Path(),
    default="leads_output.json",
    help="Output file path (json or csv)"
)
def search(
    keywords: str,
    location: str,
    sources: tuple,
    max_leads: int,
    industries: tuple,
    company_sizes: tuple,
    tech_stack: tuple,
    output: str,
):
    """
    Search for and generate leads.
    
    Example:
        leadgen search --keywords "Data Engineer" --location "Bangalore" \\
                       --sources linkedin --sources google_maps \\
                       --max-leads 100 --industries "SaaS" \\
                       --output leads.json
    """
    
    click.echo(f"🔍 Searching for leads...")
    click.echo(f"  Keywords: {keywords}")
    click.echo(f"  Location: {location}")
    click.echo(f"  Sources: {', '.join(sources)}")
    click.echo(f"  Max leads: {max_leads}")
    
    # Build ICP config
    icp_config = ICPConfig(
        target_industries=list(industries) if industries else [],
        target_company_sizes=list(company_sizes) if company_sizes else [],
        preferred_tech_stack=list(tech_stack) if tech_stack else [],
        target_geographies=[location],
    )
    
    # Run workflow
    with click.progressbar(length=100, label="Processing") as progressbar:
        try:
            result = run_lead_gen_workflow(
                search_keywords=keywords,
                search_location=location,
                search_source=list(sources),
                max_leads=max_leads,
                icp_config=icp_config,
            )
            progressbar.update(100)
        except Exception as e:
            click.echo(f"❌ Error: {e}", err=True)
            raise click.Exit(1)
    
    # Display results
    leads = result.scored_leads
    click.echo(f"\n✅ Found {len(leads)} leads")
    
    if leads:
        click.echo("\n📊 Top 10 Leads:")
        click.echo("-" * 100)
        
        for i, lead in enumerate(leads[:10], 1):
            click.echo(f"{i}. {lead.company_name}")
            click.echo(f"   Score: {lead.lead_score:.1f}/100 ({lead.priority.value})")
            if lead.name:
                click.echo(f"   Contact: {lead.name} ({lead.title or 'N/A'})")
            if lead.location:
                click.echo(f"   Location: {lead.location}")
            click.echo()
    
    # Save output
    _save_results(leads, output)
    
    # Display summary
    click.echo("\n📈 Summary:")
    click.echo(f"  Total leads: {len(leads)}")
    high_priority = len([l for l in leads if l.lead_score >= 70])
    medium_priority = len([l for l in leads if 40 <= l.lead_score < 70])
    low_priority = len([l for l in leads if l.lead_score < 40])
    click.echo(f"  HIGH priority: {high_priority}")
    click.echo(f"  MEDIUM priority: {medium_priority}")
    click.echo(f"  LOW priority: {low_priority}")
    click.echo(f"  Duration: {result.run_duration:.2f}s")


@cli.command()
@click.option(
    "--csv-file",
    type=click.Path(exists=True),
    required=True,
    help="CSV file with company data to enrich and score"
)
@click.option(
    "--industries",
    multiple=True,
    help="Target industries for ICP"
)
@click.option(
    "--company-sizes",
    multiple=True,
    type=click.Choice(["micro", "small", "mid", "enterprise"]),
    help="Target company sizes"
)
@click.option(
    "--output",
    type=click.Path(),
    default="leads_enriched.json",
    help="Output file path"
)
def enrich(
    csv_file: str,
    industries: tuple,
    company_sizes: tuple,
    output: str,
):
    """
    Enrich and score leads from a CSV file.
    
    CSV should have columns: company_name, name, title, email, company_website, location
    
    Example:
        leadgen enrich --csv-file companies.csv \\
                       --industries "SaaS" --industries "Enterprise Software" \\
                       --output leads_scored.json
    """
    
    # Load CSV
    click.echo(f"📂 Loading CSV file: {csv_file}")
    
    try:
        csv_data = _load_csv(csv_file)
        click.echo(f"✓ Loaded {len(csv_data)} rows")
    except Exception as e:
        click.echo(f"❌ Error loading CSV: {e}", err=True)
        raise click.Exit(1)
    
    # Build ICP config
    icp_config = ICPConfig(
        target_industries=list(industries) if industries else [],
        target_company_sizes=list(company_sizes) if company_sizes else [],
    )
    
    # Run workflow
    click.echo("🔄 Processing leads...")
    
    try:
        result = run_lead_gen_workflow(
            search_source=["csv"],
            csv_data=csv_data,
            max_leads=len(csv_data),
            icp_config=icp_config,
        )
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        raise click.Exit(1)
    
    # Display results
    leads = result.scored_leads
    click.echo(f"\n✅ Enriched and scored {len(leads)} leads")
    
    # Save output
    _save_results(leads, output)


@cli.command()
def config():
    """Show current configuration."""
    
    click.echo("\n⚙️  Lead Generation Agent Configuration\n")
    
    click.echo("🔑 API Keys:")
    click.echo(f"  OPENAI_API_KEY: {'✓' if Config.OPENAI_API_KEY else '✗ (not set)'}")
    click.echo(f"  APIFY_TOKEN: {'✓' if Config.APIFY_TOKEN else '✗ (not set)'}")
    click.echo(f"  GOOGLE_MAPS_API_KEY: {'✓' if Config.GOOGLE_MAPS_API_KEY else '✗ (not set)'}")
    
    click.echo("\n🤖 LLM Settings:")
    click.echo(f"  Model: {Config.OPENAI_MODEL}")
    click.echo(f"  Advanced Model: {Config.OPENAI_MODEL_ADVANCED}")
    click.echo(f"  Temperature: {Config.LLM_TEMPERATURE}")
    
    click.echo("\n⚡ Processing:")
    click.echo(f"  Max leads per run: {Config.MAX_LEADS_PER_RUN}")
    click.echo(f"  Parallel workers: {Config.PARALLEL_WORKERS}")
    click.echo(f"  Storage type: {Config.STORAGE_TYPE}")
    
    click.echo("\n📡 Scraping:")
    click.echo(f"  Respect robots.txt: {Config.RESPECT_ROBOTS_TXT}")
    click.echo(f"  Request delay: {Config.REQUEST_DELAY}s")
    click.echo(f"  Max retries: {Config.MAX_RETRIES}")
    
    click.echo("\n📦 Apify Actors:")
    for name, actor_id in Config.APIFY_ACTOR_IDS.items():
        click.echo(f"  {name}: {actor_id}")


def _load_csv(csv_file: str) -> List[dict]:
    """Load CSV file and return list of dictionaries."""
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return list(reader)


def _save_results(leads: list, output_path: str) -> None:
    """Save results to JSON or CSV file."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Convert leads to dictionaries
    leads_data = [lead.to_dict() for lead in leads]
    
    if output_path.suffix.lower() == '.csv':
        # Save as CSV
        if leads_data:
            keys = leads_data[0].keys()
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=keys)
                writer.writeheader()
                writer.writerows(leads_data)
            click.echo(f"✓ Results saved to CSV: {output_path}")
    else:
        # Save as JSON (default)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(leads_data, f, indent=2, default=str)
        click.echo(f"✓ Results saved to JSON: {output_path}")


if __name__ == "__main__":
    cli()
