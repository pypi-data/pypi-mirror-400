"""CLI interface for DevCon."""

import subprocess
import sys
from pathlib import Path

import click

from devcon import __version__
from devcon.generator import DevContainerGenerator
from devcon.validators import (
    check_vscode_installed,
    run_preflight_checks,
    validate_claude_version,
    validate_node_version,
    validate_python_version,
)


@click.group()
@click.version_option(version=__version__)
@click.option("--verbose", is_flag=True, help="Enable verbose output")
@click.option("--quiet", "-q", is_flag=True, help="Suppress non-error output")
@click.pass_context
def main(ctx: click.Context, verbose: bool, quiet: bool) -> None:
    """DevContainer configuration generator for MacOS.

    Generate pre-configured VS Code devcontainer setups for data science,
    LLM finetuning, and web development environments.

    All containers include Claude Code, Powerlevel10k, and SSH credentials.
    """
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose
    ctx.obj["quiet"] = quiet


@main.command()
@click.option(
    "--type",
    "-t",
    "container_type",
    type=click.Choice(["data-science", "llm-finetuning", "web-dev"], case_sensitive=False),
    required=True,
    help="Container type to generate",
)
@click.option("--output-dir", "-o", default=".", help="Output directory (default: current)")
@click.option("--python-version", default="3.11", help="Python version (default: 3.11)")
@click.option("--node-version", default="20", help="Node.js version (default: 20)")
@click.option("--gpu", is_flag=True, help="Enable GPU support (llm-finetuning only)")
@click.option(
    "--p10k-style",
    type=click.Choice(["lean", "rainbow", "classic", "pure"]),
    default="lean",
    help="Powerlevel10k style (default: lean)",
)
@click.option("--claude-version", default="latest", help="Claude Code version (default: latest)")
@click.option("--force", "-f", is_flag=True, help="Overwrite existing configuration")
@click.option("--dry-run", is_flag=True, help="Show what would be generated without creating files")
@click.pass_context
def generate(
    ctx: click.Context,
    container_type: str,
    output_dir: str,
    python_version: str,
    node_version: str,
    gpu: bool,
    p10k_style: str,
    claude_version: str,
    force: bool,
    dry_run: bool,
) -> None:
    """Generate a devcontainer configuration.

    Examples:

        \b
        # Generate data science devcontainer
        devcon generate -t data-science

        \b
        # Generate LLM finetuning devcontainer with GPU
        devcon generate -t llm-finetuning --gpu

        \b
        # Generate web dev devcontainer with custom Node version
        devcon generate -t web-dev --node-version 18

        \b
        # Preview what would be generated (dry run)
        devcon generate -t data-science --dry-run

        \b
        # Overwrite existing devcontainer
        devcon generate -t data-science --force
    """
    verbose = ctx.obj.get("verbose", False)
    quiet = ctx.obj.get("quiet", False)

    # Run pre-flight checks (skip for dry-run)
    if not dry_run:
        if verbose:
            click.echo("Running pre-flight checks...")

        errors = run_preflight_checks()
        if errors:
            click.echo("Pre-flight checks failed:\n", err=True)
            for error in errors:
                click.echo(f"  ✗ {error}", err=True)
            click.echo("\nPlease fix the above issues and try again.", err=True)
            sys.exit(1)

        if verbose:
            click.echo("✓ Pre-flight checks passed\n")

    # Validate version arguments
    if python_error := validate_python_version(python_version):
        click.echo(f"Error: {python_error}", err=True)
        sys.exit(1)

    if node_error := validate_node_version(node_version):
        click.echo(f"Error: {node_error}", err=True)
        sys.exit(1)

    if claude_error := validate_claude_version(claude_version):
        click.echo(f"Error: {claude_error}", err=True)
        sys.exit(1)

    # Check output directory is writable
    output_path = Path(output_dir)
    if not dry_run and not output_path.exists():
        click.echo(f"Error: Output directory does not exist: {output_dir}", err=True)
        sys.exit(1)

    if not dry_run and not output_path.is_dir():
        click.echo(f"Error: Output path is not a directory: {output_dir}", err=True)
        sys.exit(1)

    # Generate configuration
    if not quiet:
        click.echo(f"Generating {container_type} devcontainer...")

    generator = DevContainerGenerator()

    try:
        generator.generate(
            container_type=container_type,
            output_dir=output_dir,
            dry_run=dry_run,
            force=force,
            python_version=python_version,
            node_version=node_version,
            gpu=gpu,
            p10k_style=p10k_style,
            claude_version=claude_version,
        )

        if not dry_run and not quiet:
            devcontainer_path = Path(output_dir) / ".devcontainer"
            click.echo("\n✓ DevContainer generated successfully!\n")
            click.echo(f"Location: {devcontainer_path.absolute()}\n")
            click.echo("Next steps:")
            click.echo("  1. Open this directory in VS Code")
            click.echo('  2. Click "Reopen in Container" when prompted')
            click.echo("  3. Wait for container to build (may take a few minutes)")
            click.echo("  4. Start coding!\n")

    except FileExistsError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error generating devcontainer: {e}", err=True)
        if verbose:
            import traceback

            traceback.print_exc()
        sys.exit(1)


@main.command()
@click.option("--no-cache", is_flag=True, help="Rebuild without using cache")
@click.pass_context
def build(ctx: click.Context, no_cache: bool) -> None:
    """Rebuild the devcontainer in VS Code.

    This command triggers VS Code to rebuild the current devcontainer.
    Requires VS Code to be installed and a .devcontainer directory to exist.

    Examples:

        \b
        # Rebuild devcontainer
        devcon build

        \b
        # Rebuild without cache
        devcon build --no-cache
    """
    verbose = ctx.obj.get("verbose", False)
    quiet = ctx.obj.get("quiet", False)

    # Check VS Code is installed
    if not check_vscode_installed():
        click.echo("Error: VS Code is not installed or 'code' command is not in PATH.", err=True)
        click.echo("\nTo install the 'code' command:", err=True)
        click.echo("  1. Open VS Code", err=True)
        click.echo("  2. Press Cmd+Shift+P", err=True)
        click.echo('  3. Type "Shell Command: Install \'code\' command in PATH"', err=True)
        sys.exit(1)

    # Check .devcontainer directory exists
    devcontainer_path = Path(".devcontainer")
    if not devcontainer_path.exists():
        click.echo("Error: No .devcontainer directory found in current directory.", err=True)
        click.echo("\nGenerate a devcontainer first:", err=True)
        click.echo("  devcon generate -t data-science", err=True)
        sys.exit(1)

    if not quiet:
        if no_cache:
            click.echo("Triggering devcontainer rebuild without cache...")
        else:
            click.echo("Triggering devcontainer rebuild...")

    # Trigger VS Code rebuild
    try:
        if no_cache:
            # Rebuild without cache
            result = subprocess.run(
                ["code", "--command", "remote-containers.rebuildContainerWithoutCache"],
                capture_output=True,
                text=True,
                check=False,
            )
        else:
            # Normal rebuild
            result = subprocess.run(
                ["code", "--command", "remote-containers.rebuildContainer"],
                capture_output=True,
                text=True,
                check=False,
            )

        if result.returncode == 0:
            if not quiet:
                click.echo("\n✓ Rebuild command sent to VS Code successfully!")
                click.echo("\nVS Code should now rebuild your devcontainer.")
                click.echo("This may take a few minutes depending on your configuration.")
        else:
            click.echo("Warning: Rebuild command may not have executed correctly.", err=True)
            if verbose and result.stderr:
                click.echo(f"Error output: {result.stderr}", err=True)

    except FileNotFoundError:
        click.echo("Error: Could not execute 'code' command.", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error triggering rebuild: {e}", err=True)
        if verbose:
            import traceback

            traceback.print_exc()
        sys.exit(1)


@main.command()
def list() -> None:
    """List available devcontainer templates."""
    click.echo("Available devcontainer types:\n")
    click.echo("  data-science      Python-based data science and MLOps environment")
    click.echo("                    Includes: Jupyter, marimo, pandas, scikit-learn, MLflow")
    click.echo("")
    click.echo("  llm-finetuning    LLM finetuning environment with GPU support")
    click.echo("                    Includes: PyTorch, Transformers, datasets, PEFT")
    click.echo("")
    click.echo("  web-dev           JavaScript/Node.js web development environment")
    click.echo("                    Includes: TypeScript, ESLint, Prettier, Vite")


if __name__ == "__main__":
    main()
