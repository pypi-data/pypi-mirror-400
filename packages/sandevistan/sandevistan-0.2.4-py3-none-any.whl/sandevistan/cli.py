"""Command-line interface for Sandevistan."""

import sys
from pathlib import Path

import click

from . import __version__
from .analyzer import analyze_crash_files
from .config import get_api_key, save_api_key, get_model, save_model, get_config_path, get_config


@click.group()
@click.version_option(version=__version__, prog_name="sandy")
def cli():
    """Sandevistan - AI agent to analyze Apple crash files."""
    pass


def discover_ips_files(path: Path) -> list[Path]:
    """
    Discover all .ips files in the given path.

    Args:
        path: Directory path to scan

    Returns:
        Sorted list of .ips file paths

    Raises:
        FileNotFoundError: If no .ips files found
    """
    ips_files = sorted(path.glob("*.ips"))

    if not ips_files:
        raise FileNotFoundError(f"No .ips files found in {path}")

    return ips_files


def prompt_file_selection(ips_files: list[Path], path: Path) -> list[Path]:
    """
    Prompt user to select which files to analyze.

    Args:
        ips_files: List of discovered .ips files
        path: The folder path being analyzed

    Returns:
        List of selected file paths
    """
    click.echo(f"\nFound {len(ips_files)} IPS file(s) in {path}:")
    click.echo("  [0] All files")

    for idx, file_path in enumerate(ips_files, start=1):
        click.echo(f"  [{idx}] {file_path.name}")

    click.echo()

    while True:
        selection = click.prompt(
            "Select files to analyze (comma-separated, e.g., \"1,3\" or \"0\" for all)",
            type=str
        ).strip().lower()

        # Handle "all" or "0"
        if selection in ("0", "all"):
            return ips_files

        # Parse comma-separated numbers
        try:
            indices = [int(s.strip()) for s in selection.split(",")]

            # Validate all indices are in range
            if all(1 <= idx <= len(ips_files) for idx in indices):
                return [ips_files[idx - 1] for idx in indices]
            else:
                click.echo(
                    f"Invalid selection. Enter numbers between 1-{len(ips_files)} "
                    "or '0' for all.",
                    err=True
                )
        except (ValueError, IndexError):
            click.echo(
                "Invalid selection. Enter numbers (e.g., '1,3') or '0' for all.",
                err=True
            )


@cli.command()
@click.argument("path", type=click.Path(exists=True))
@click.option("--verbose", "-v", is_flag=True, help="Show detailed output")
def analyze(path: str, verbose: bool):
    """Analyze crash files in the specified path (file or folder)."""
    # Get API key and model from config
    api_key = get_api_key()
    model = get_model()

    if not api_key:
        click.echo("Error: Google API key not configured.", err=True)
        click.echo("")
        click.echo("Run: sandy config --api-key YOUR_KEY", err=True)
        click.echo("Get your API key at: https://makersuite.google.com/app/apikey", err=True)
        sys.exit(1)

    path_obj = Path(path)

    try:
        # Step 1: Determine if path is file or directory
        if path_obj.is_file():
            # Validate .ips extension
            if path_obj.suffix != ".ips":
                click.echo(
                    f"Error: {path} is not an IPS file (.ips extension required)",
                    err=True
                )
                sys.exit(1)

            selected_files = [path_obj]
            click.echo(f"Analyzing file: {path_obj}")

        elif path_obj.is_dir():
            # Discover all .ips files in directory
            ips_files = discover_ips_files(path_obj)

            # Step 2: Handle based on file count
            if len(ips_files) == 1:
                # Single file: analyze immediately (no prompt)
                selected_files = ips_files
                click.echo(f"Analyzing file: {ips_files[0].name}")
            else:
                # Multiple files: show interactive selection
                selected_files = prompt_file_selection(ips_files, path_obj)
                click.echo(f"\nAnalyzing {len(selected_files)} file(s)...")
        else:
            click.echo(f"Error: {path} is not a valid file or directory", err=True)
            sys.exit(1)

        # Step 3: Run analysis
        click.echo(f"Using model: {model}")
        click.echo("-" * 80)

        result = analyze_crash_files(selected_files, api_key, model)

        # Step 4: Display results
        click.echo(f"\nAnalyzed {len(selected_files)} IPS file(s)")
        click.echo(result["analysis"])

    except FileNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


@cli.command()
@click.option("--api-key", help="Set the Google API key")
@click.option("--model", help="Set the Gemini model to use")
@click.option("--show", is_flag=True, help="Display current configuration")
@click.option("--path", is_flag=True, help="Show config file location")
def config(api_key: str, model: str, show: bool, path: bool):
    """Manage Sandevistan configuration."""
    if path:
        click.echo(f"Config file: {get_config_path()}")
        return

    if show:
        cfg = get_config()
        if not cfg:
            click.echo("No configuration found.")
            click.echo(f"Config file would be created at: {get_config_path()}")
        else:
            click.echo("Current configuration:")
            click.echo("")
            # Mask API key for security
            if "api" in cfg and "google_api_key" in cfg["api"]:
                masked_key = cfg["api"]["google_api_key"][:8] + "..." + cfg["api"]["google_api_key"][-4:]
                click.echo(f"  API Key: {masked_key}")
            else:
                click.echo("  API Key: Not set")

            # Show model
            model_name = get_model()
            click.echo(f"  Model: {model_name}")
        return

    if api_key:
        save_api_key(api_key)
        click.echo(f"API key saved to: {get_config_path()}")
        return

    if model:
        save_model(model)
        click.echo(f"Model set to: {model}")
        click.echo(f"Config saved to: {get_config_path()}")
        return

    # No options provided, show help
    click.echo("Error: Please provide an option.", err=True)
    click.echo("")
    click.echo("Examples:")
    click.echo("  sandy config --api-key YOUR_KEY               # Set API key")
    click.echo("  sandy config --model gemini-3-flash-preview   # Set model")
    click.echo("  sandy config --show                           # Show current config")
    click.echo("  sandy config --path                           # Show config file location")
    sys.exit(1)


def main():
    """Main entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()
