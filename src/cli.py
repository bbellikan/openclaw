"""CLI interface using Typer with rich output."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from . import __version__
from .config import AmazonRegion, Settings, load_settings
from .openclaw import (
    OpenClawError,
    OpenClawNotInstalledError,
    RunMode,
    build_task_message,
    check_gateway_health,
    check_openclaw_installed,
    run_agent,
    setup_skill,
    update_openclaw_config,
)

app = typer.Typer(
    name="amazon-bot",
    help="AI-powered Amazon shopping bot using OpenClaw browser automation",
    no_args_is_help=True,
    rich_markup_mode="rich",
)

console = Console()


def version_callback(value: bool) -> None:
    """Show version and exit."""
    if value:
        console.print(f"[bold blue]OpenClaw Amazon Bot[/bold blue] v{__version__}")
        raise typer.Exit()


def get_project_root() -> Path:
    """Get the project root directory."""
    # Try to find pyproject.toml to locate project root
    current = Path(__file__).parent.parent
    if (current / "pyproject.toml").exists():
        return current
    return Path.cwd()


@app.callback()
def main(
    version: Annotated[
        Optional[bool],
        typer.Option(
            "--version",
            "-V",
            help="Show version and exit",
            callback=version_callback,
            is_eager=True,
        ),
    ] = None,
) -> None:
    """OpenClaw Amazon Bot - Automated shopping with AI."""


@app.command()
def run(
    dry_run: Annotated[
        bool,
        typer.Option(
            "--dry-run",
            "-d",
            help="Test without completing purchase",
        ),
    ] = False,
    product: Annotated[
        Optional[str],
        typer.Option(
            "--product",
            "-p",
            help="Product to search for",
        ),
    ] = None,
    max_price: Annotated[
        Optional[float],
        typer.Option(
            "--max-price",
            "-m",
            help="Maximum price in EUR",
        ),
    ] = None,
    region: Annotated[
        Optional[AmazonRegion],
        typer.Option(
            "--region",
            "-r",
            help="Amazon region",
        ),
    ] = None,
    headless: Annotated[
        bool,
        typer.Option(
            "--headless",
            help="Run browser in headless mode",
        ),
    ] = False,
    skip_checks: Annotated[
        bool,
        typer.Option(
            "--skip-checks",
            help="Skip pre-flight checks",
        ),
    ] = False,
    yes: Annotated[
        bool,
        typer.Option(
            "--yes",
            "-y",
            help="Skip confirmation prompt for live mode",
        ),
    ] = False,
) -> None:
    """Run the Amazon shopping bot.

    By default, searches for a pencil sharpener under €10 on Amazon.nl.
    Use --dry-run to test without making a purchase.
    """
    project_root = get_project_root()

    # Load settings
    try:
        settings = load_settings()
    except Exception as e:
        console.print(f"[red]Configuration error:[/red] {e}")
        console.print("\nMake sure .env file exists with required variables:")
        console.print("  AMAZON_NL_USERNAME=your@email.com")
        console.print("  AMAZON_NL_PASSWORD=yourpassword")
        console.print("  GOOGLE_API_KEY=your-gemini-api-key")
        raise typer.Exit(1)

    # Override settings from CLI
    if product:
        settings.product_search = product
    if max_price:
        from decimal import Decimal

        settings.max_price_eur = Decimal(str(max_price))
    if region:
        settings.region = region
    if headless:
        settings.headless = True

    mode = RunMode.DRY_RUN if dry_run else RunMode.LIVE

    # Display configuration
    _show_config(settings, mode)

    # Pre-flight checks
    if not skip_checks:
        if not _run_preflight_checks():
            raise typer.Exit(1)

    # Confirmation for live mode
    if mode == RunMode.LIVE and not yes:
        console.print()
        confirm = typer.confirm(
            "⚠️  This will make a REAL purchase. Continue?",
            default=False,
        )
        if not confirm:
            console.print("[yellow]Cancelled[/yellow]")
            raise typer.Exit(0)

    # Setup skill
    skill_source = project_root / "skills" / "amazon-shopper"
    if skill_source.exists():
        skill_target = setup_skill(skill_source)
        console.print(f"[dim]Skill linked: {skill_target}[/dim]")

    # Update OpenClaw config
    config_path = project_root / "openclaw.json"
    update_openclaw_config(config_path, settings)

    # Build task and run
    console.print()
    message = build_task_message(settings, mode)

    with console.status("[bold blue]Running OpenClaw agent...[/bold blue]"):
        result = run_agent(message, config_path)

    # Show result
    console.print()
    if result.success:
        console.print(Panel("[green]✓ Task completed successfully[/green]", border_style="green"))
    else:
        console.print(
            Panel(
                f"[red]✗ Task failed[/red]\n{result.message or 'Check output above for details'}",
                border_style="red",
            )
        )
        raise typer.Exit(result.return_code)


@app.command()
def check() -> None:
    """Run pre-flight checks without starting the bot."""
    if _run_preflight_checks():
        console.print("\n[green]✓ All checks passed![/green]")
    else:
        console.print("\n[red]✗ Some checks failed[/red]")
        raise typer.Exit(1)


@app.command()
def config() -> None:
    """Show current configuration."""
    try:
        settings = load_settings()
        _show_config(settings, RunMode.DRY_RUN)
    except Exception as e:
        console.print(f"[red]Failed to load configuration:[/red] {e}")
        raise typer.Exit(1)


def _show_config(settings: Settings, mode: RunMode) -> None:
    """Display current configuration in a table."""
    table = Table(title="Configuration", show_header=False, border_style="blue")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="white")

    mode_style = "yellow" if mode == RunMode.DRY_RUN else "red bold"
    mode_text = "🧪 DRY RUN" if mode == RunMode.DRY_RUN else "🛒 LIVE"

    table.add_row("Mode", f"[{mode_style}]{mode_text}[/{mode_style}]")
    table.add_row("Product", settings.product_search)
    table.add_row("Max Price", f"€{settings.max_price_eur:.2f}")
    table.add_row("Region", f"Amazon.{settings.region.value}")
    table.add_row("Min Rating", f"{settings.min_rating}⭐")
    table.add_row("Account", settings.amazon_nl_username)
    table.add_row("Browser", "Headless" if settings.headless else "Visible")

    console.print(table)


def _run_preflight_checks() -> bool:
    """Run pre-flight checks and return True if all pass."""
    console.print("\n[bold]Pre-flight checks:[/bold]")
    all_passed = True

    # Check OpenClaw installed
    try:
        openclaw_path = check_openclaw_installed()
        console.print(f"  [green]✓[/green] OpenClaw installed: {openclaw_path}")
    except OpenClawNotInstalledError as e:
        console.print(f"  [red]✗[/red] {e}")
        all_passed = False

    # Check Gateway health
    if check_gateway_health():
        console.print("  [green]✓[/green] Gateway is healthy")
    else:
        console.print("  [yellow]![/yellow] Gateway not running (will start automatically)")

    # Check .env file
    if Path(".env").exists():
        console.print("  [green]✓[/green] .env file found")
    else:
        console.print("  [red]✗[/red] .env file not found")
        all_passed = False

    # Check skill exists
    skill_path = get_project_root() / "skills" / "amazon-shopper" / "SKILL.md"
    if skill_path.exists():
        console.print("  [green]✓[/green] Amazon shopper skill found")
    else:
        console.print("  [yellow]![/yellow] Skill not found (will use default behavior)")

    return all_passed


if __name__ == "__main__":
    app()
