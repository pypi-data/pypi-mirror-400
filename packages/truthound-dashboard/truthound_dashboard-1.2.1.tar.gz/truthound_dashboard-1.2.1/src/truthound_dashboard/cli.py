"""CLI entry point for truthound-dashboard.

This module provides the command-line interface using Typer.
It supports both standalone usage and integration with the
truthound CLI plugin system.

Example:
    # Standalone usage
    truthound-dashboard serve --port 8765

    # Via truthound CLI plugin
    truthound serve --port 8765

    # Translate UI to additional languages
    truthound translate -l ja,zh,de -p openai
"""

from __future__ import annotations

import asyncio
import webbrowser
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from truthound_dashboard import __version__

app = typer.Typer(
    name="truthound-dashboard",
    help="Open-source data quality dashboard - GX Cloud alternative",
    no_args_is_help=True,
    rich_markup_mode="rich",
)
console = Console()


def version_callback(value: bool) -> None:
    """Print version and exit."""
    if value:
        console.print(f"truthound-dashboard version {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Annotated[
        bool | None,
        typer.Option(
            "--version",
            "-v",
            help="Show version and exit",
            callback=version_callback,
            is_eager=True,
        ),
    ] = None,
) -> None:
    """Truthound Dashboard - Open-source data quality monitoring."""
    pass


@app.command()
def serve(
    port: Annotated[
        int,
        typer.Option("--port", "-p", help="Port to run server on", min=1, max=65535),
    ] = 8765,
    host: Annotated[
        str,
        typer.Option("--host", "-h", help="Host to bind server to"),
    ] = "127.0.0.1",
    data_dir: Annotated[
        Path | None,
        typer.Option(
            "--data-dir",
            "-d",
            help="Data directory for database and cache",
            exists=False,
            file_okay=False,
            resolve_path=True,
        ),
    ] = None,
    no_browser: Annotated[
        bool,
        typer.Option("--no-browser", help="Don't open browser automatically"),
    ] = False,
    reload: Annotated[
        bool,
        typer.Option("--reload", help="Enable hot reload for development"),
    ] = False,
    log_level: Annotated[
        str,
        typer.Option(
            "--log-level",
            "-l",
            help="Logging level",
            case_sensitive=False,
        ),
    ] = "warning",
) -> None:
    """Start the truthound dashboard server.

    This command starts the FastAPI server and optionally opens
    the dashboard in your default browser.

    Examples:
        truthound serve
        truthound serve --port 9000
        truthound serve --reload --log-level debug
    """
    import uvicorn

    from truthound_dashboard.config import get_settings, reset_settings

    # Reset settings cache to pick up any CLI overrides
    reset_settings()
    settings = get_settings()

    # Override settings from CLI arguments
    if data_dir:
        settings.data_dir = data_dir

    # Ensure directories exist
    settings.ensure_directories()

    # Display startup info
    url = f"http://{host}:{port}"
    console.print(
        Panel(
            f"[bold]Truthound Dashboard v{__version__}[/bold]\n\n"
            f"[green]✓[/green] Database: {settings.database_path}\n"
            f"[green]✓[/green] Server: {url}\n"
            f"[green]✓[/green] API Docs: {url}/docs",
            title="Starting Dashboard",
            border_style="bright_blue",
        )
    )

    # Open browser
    if not no_browser:
        webbrowser.open(url)
        console.print("[dim]Opening browser...[/dim]")

    # Configure and run server
    uvicorn.run(
        "truthound_dashboard.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level=log_level.lower(),
        access_log=log_level.lower() == "debug",
    )


@app.command()
def info() -> None:
    """Show dashboard configuration and status."""
    from truthound_dashboard.config import get_settings

    settings = get_settings()
    settings.ensure_directories()

    console.print(
        Panel(
            f"[bold]Configuration[/bold]\n\n"
            f"Data Directory: {settings.data_dir}\n"
            f"Database: {settings.database_path}\n"
            f"Cache: {settings.cache_dir}\n"
            f"Schemas: {settings.schema_dir}\n\n"
            f"[bold]Server Defaults[/bold]\n\n"
            f"Host: {settings.host}\n"
            f"Port: {settings.port}\n"
            f"Auth Enabled: {settings.auth_enabled}\n\n"
            f"[bold]Validation Defaults[/bold]\n\n"
            f"Sample Size: {settings.sample_size:,}\n"
            f"Max Failed Rows: {settings.max_failed_rows:,}\n"
            f"Timeout: {settings.default_timeout}s",
            title=f"Truthound Dashboard v{__version__}",
            border_style="bright_blue",
        )
    )


@app.command()
def translate(
    languages: Annotated[
        str | None,
        typer.Option(
            "--languages",
            "-l",
            help="Target languages (comma-separated, e.g., ja,zh,de)",
        ),
    ] = None,
    provider: Annotated[
        str | None,
        typer.Option(
            "--provider",
            "-p",
            help="AI provider (openai, anthropic, ollama, mistral). Auto-detected if not specified.",
        ),
    ] = None,
    model: Annotated[
        str | None,
        typer.Option(
            "--model",
            "-m",
            help="Model name (e.g., gpt-4o, claude-sonnet-4-20250514). Uses provider default if not specified.",
        ),
    ] = None,
    frontend_dir: Annotated[
        Path | None,
        typer.Option(
            "--frontend-dir",
            "-f",
            help="Path to frontend directory. Auto-detected if not specified.",
            exists=True,
            file_okay=False,
            resolve_path=True,
        ),
    ] = None,
    dry_run: Annotated[
        bool,
        typer.Option(
            "--dry-run",
            help="Show what would be translated without making changes",
        ),
    ] = False,
    list_providers: Annotated[
        bool,
        typer.Option(
            "--list-providers",
            help="List available AI providers and exit",
        ),
    ] = False,
    list_languages: Annotated[
        bool,
        typer.Option(
            "--list-languages",
            help="List supported languages and exit",
        ),
    ] = False,
) -> None:
    """Translate UI to additional languages using AI.

    This command uses AI providers to translate Intlayer content files
    to new languages. Supports OpenAI, Anthropic, Ollama (local), and Mistral.

    Examples:
        # Translate to Japanese, Chinese, and German using OpenAI
        truthound translate -l ja,zh,de -p openai

        # Auto-detect provider based on environment variables
        truthound translate -l ja,zh

        # Use local Ollama (no API key needed)
        truthound translate -l ja -p ollama

        # Dry run to see what would be translated
        truthound translate -l ja --dry-run

        # List available providers
        truthound translate --list-providers

        # List supported languages
        truthound translate --list-languages
    """
    # Handle list options first
    if list_providers:
        _show_providers()
        raise typer.Exit()

    if list_languages:
        _show_languages()
        raise typer.Exit()

    # Require languages for actual translation
    if not languages:
        console.print("[red]Error:[/red] --languages / -l is required for translation")
        console.print("Use --list-languages to see supported languages")
        raise typer.Exit(1)

    # Parse languages
    target_langs = [lang.strip().lower() for lang in languages.split(",")]
    if not target_langs:
        console.print("[red]Error:[/red] No languages specified")
        raise typer.Exit(1)

    # Find frontend directory
    if frontend_dir is None:
        frontend_dir = _find_frontend_dir()
        if frontend_dir is None:
            console.print(
                "[red]Error:[/red] Could not find frontend directory. "
                "Please specify with --frontend-dir"
            )
            raise typer.Exit(1)

    # Run translation
    asyncio.run(
        _run_translation(
            target_langs=target_langs,
            provider_name=provider,
            model_name=model,
            frontend_dir=frontend_dir,
            dry_run=dry_run,
        )
    )


def _show_providers() -> None:
    """Display available AI providers."""
    try:
        from truthound_dashboard.translate import list_available_providers
    except ImportError:
        console.print(
            "[yellow]Warning:[/yellow] Translation module not available.\n"
            "Install with: pip install truthound-dashboard[translate]"
        )
        raise typer.Exit(1)

    providers = list_available_providers()

    table = Table(title="Available AI Providers")
    table.add_column("Provider", style="cyan")
    table.add_column("Environment Variable", style="yellow")
    table.add_column("Default Model", style="green")
    table.add_column("Status", style="bold")

    for p in providers:
        status = "[green]Ready[/green]" if p["available"] else "[red]Not configured[/red]"
        table.add_row(
            p["display_name"],
            p["env_var"],
            p["default_model"],
            status,
        )

    console.print(table)
    console.print("\n[dim]Set the environment variable to enable a provider.[/dim]")


def _show_languages() -> None:
    """Display supported languages."""
    try:
        from truthound_dashboard.translate.config_updater import get_supported_languages
    except ImportError:
        console.print(
            "[yellow]Warning:[/yellow] Translation module not available.\n"
            "Install with: pip install truthound-dashboard[translate]"
        )
        raise typer.Exit(1)

    languages = get_supported_languages()

    table = Table(title="Supported Languages")
    table.add_column("Code", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("Native Name", style="yellow")
    table.add_column("Flag")

    for lang in sorted(languages, key=lambda x: x["code"]):
        table.add_row(
            lang["code"],
            lang["name"],
            lang["native_name"],
            lang["flag"],
        )

    console.print(table)
    console.print("\n[dim]Use comma-separated codes: -l ja,zh,de[/dim]")


def _find_frontend_dir() -> Path | None:
    """Find the frontend directory relative to the package."""
    import truthound_dashboard

    # Try to find frontend relative to package
    package_dir = Path(truthound_dashboard.__file__).parent
    candidates = [
        package_dir.parent.parent / "frontend",  # Development layout
        package_dir / "frontend",  # Installed layout
        Path.cwd() / "frontend",  # Current directory
    ]

    for candidate in candidates:
        if candidate.exists() and (candidate / "src").exists():
            return candidate

    return None


async def _run_translation(
    target_langs: list[str],
    provider_name: str | None,
    model_name: str | None,
    frontend_dir: Path,
    dry_run: bool,
) -> None:
    """Run the translation process."""
    try:
        from truthound_dashboard.translate import (
            ContentTranslator,
            IntlayerConfigUpdater,
            ProviderConfig,
            detect_provider,
            get_provider,
        )
        from truthound_dashboard.translate.config_updater import LOCALE_MAPPINGS
        from truthound_dashboard.translate.exceptions import (
            APIKeyNotFoundError,
            ProviderNotFoundError,
            TranslationError,
        )
    except ImportError as e:
        console.print(
            f"[red]Error:[/red] Translation module not available: {e}\n"
            "Install with: pip install truthound-dashboard[translate]"
        )
        raise typer.Exit(1)

    # Validate languages
    invalid_langs = [lang for lang in target_langs if lang not in LOCALE_MAPPINGS]
    if invalid_langs:
        console.print(
            f"[red]Error:[/red] Unsupported language(s): {', '.join(invalid_langs)}\n"
            "Use --list-languages to see supported languages."
        )
        raise typer.Exit(1)

    # Get provider
    try:
        config = ProviderConfig(model=model_name) if model_name else None

        if provider_name:
            provider = get_provider(provider_name, config)
            console.print(f"[green]✓[/green] Using provider: {provider_name}")
        else:
            provider = detect_provider(config)
            console.print(
                f"[green]✓[/green] Auto-detected provider: {provider.name}"
            )

        console.print(f"[green]✓[/green] Model: {provider.model}")

    except ProviderNotFoundError as e:
        console.print(f"[red]Error:[/red] {e}")
        console.print("\nUse --list-providers to see available providers.")
        raise typer.Exit(1)
    except APIKeyNotFoundError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)

    # Show what will be translated
    console.print(f"[green]✓[/green] Frontend directory: {frontend_dir}")
    console.print(f"[green]✓[/green] Target languages: {', '.join(target_langs)}")

    if dry_run:
        console.print("\n[yellow]Dry run mode - no changes will be made[/yellow]")
        translator = ContentTranslator(provider, frontend_dir)
        content_files = translator.find_content_files()
        console.print(f"\nFound {len(content_files)} content files to translate:")
        for f in content_files:
            console.print(f"  - {f.relative_to(frontend_dir)}")
        raise typer.Exit()

    # Run translation
    console.print("\n[bold]Starting translation...[/bold]\n")

    translator = ContentTranslator(provider, frontend_dir)
    content_files = translator.find_content_files()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Translating...", total=len(content_files))

        def on_progress(current: int, total: int, filename: str) -> None:
            progress.update(task, completed=current, description=f"Translating {filename}")

        try:
            results = await translator.translate_all(
                target_langs=target_langs,
                on_progress=on_progress,
            )
        except TranslationError as e:
            console.print(f"\n[red]Translation failed:[/red] {e}")
            raise typer.Exit(1)

    # Update config files
    console.print("\n[bold]Updating configuration...[/bold]")
    try:
        config_updater = IntlayerConfigUpdater(frontend_dir)
        added_langs = config_updater.add_languages(target_langs)
        if added_langs:
            console.print(
                f"[green]✓[/green] Added languages to config: {', '.join(added_langs)}"
            )
        else:
            console.print("[dim]Languages already in config[/dim]")
    except Exception as e:
        console.print(f"[yellow]Warning:[/yellow] Could not update config: {e}")

    # Show results
    stats = translator.get_translation_stats(results)

    console.print(
        Panel(
            f"[bold]Translation Complete[/bold]\n\n"
            f"Files processed: {stats['files_processed']}\n"
            f"Entries translated: {stats['entries_translated']}\n"
            f"Entries skipped: {stats['entries_skipped']}\n"
            f"Errors: {stats['total_errors']}",
            title="Results",
            border_style="green" if stats["total_errors"] == 0 else "yellow",
        )
    )

    if stats["all_errors"]:
        console.print("\n[yellow]Errors encountered:[/yellow]")
        for error in stats["all_errors"][:10]:  # Show first 10 errors
            console.print(f"  [red]•[/red] {error}")
        if len(stats["all_errors"]) > 10:
            console.print(f"  ... and {len(stats['all_errors']) - 10} more errors")

    console.print("\n[bold]Next steps:[/bold]")
    console.print("  1. Review the translated content files")
    console.print("  2. Rebuild the frontend: cd frontend && npm run build")
    console.print("  3. Start the server: truthound serve")


def register_commands(typer_app: typer.Typer) -> None:
    """Register commands with truthound CLI plugin system.

    This function is called by the truthound CLI when the
    dashboard plugin is discovered via entry points.

    Args:
        typer_app: The parent typer application to register commands with.
    """

    @typer_app.command(name="serve")
    def serve_dashboard(
        port: Annotated[
            int,
            typer.Option("--port", "-p", help="Port to run on"),
        ] = 8765,
        host: Annotated[
            str,
            typer.Option("--host", help="Host to bind"),
        ] = "127.0.0.1",
        data_dir: Annotated[
            Path | None,
            typer.Option("--data-dir", "-d", help="Data directory path"),
        ] = None,
        no_browser: Annotated[
            bool,
            typer.Option("--no-browser", help="Don't open browser automatically"),
        ] = False,
        reload: Annotated[
            bool,
            typer.Option("--reload", help="Enable hot reload for development"),
        ] = False,
    ) -> None:
        """Start the truthound dashboard server."""
        serve(
            port=port,
            host=host,
            data_dir=data_dir,
            no_browser=no_browser,
            reload=reload,
        )

    @typer_app.command(name="translate")
    def translate_ui(
        languages: Annotated[
            str | None,
            typer.Option("--languages", "-l", help="Target languages (comma-separated)"),
        ] = None,
        provider: Annotated[
            str | None,
            typer.Option("--provider", "-p", help="AI provider"),
        ] = None,
        model: Annotated[
            str | None,
            typer.Option("--model", "-m", help="Model name"),
        ] = None,
        frontend_dir: Annotated[
            Path | None,
            typer.Option("--frontend-dir", "-f", help="Frontend directory path"),
        ] = None,
        dry_run: Annotated[
            bool,
            typer.Option("--dry-run", help="Show what would be translated"),
        ] = False,
        list_providers: Annotated[
            bool,
            typer.Option("--list-providers", help="List available AI providers"),
        ] = False,
        list_languages: Annotated[
            bool,
            typer.Option("--list-languages", help="List supported languages"),
        ] = False,
    ) -> None:
        """Translate UI to additional languages using AI."""
        translate(
            languages=languages,
            provider=provider,
            model=model,
            frontend_dir=frontend_dir,
            dry_run=dry_run,
            list_providers=list_providers,
            list_languages=list_languages,
        )


if __name__ == "__main__":
    app()
