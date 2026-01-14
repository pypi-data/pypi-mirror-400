# Copyright (c) 2024, qBraid Development Team
# All rights reserved.

"""
Module defining commands in the 'qbraid envs' namespace.

"""

import subprocess
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Optional

import typer
from qbraid_core.services.environments.schema import EnvironmentConfig
from qbraid_core.services.environments.exceptions import EnvironmentValidationError
from rich.console import Console
from rich.progress import (
    BarColumn,
    DownloadColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
    TransferSpeedColumn,
)

from qbraid_cli.envs.create import create_qbraid_env_assets, create_venv
from qbraid_cli.envs.data_handling import get_envs_data as installed_envs_data
from qbraid_cli.envs.data_handling import validate_env_name
from qbraid_cli.handlers import QbraidException, handle_error, run_progress_task

if TYPE_CHECKING:
    from qbraid_core.services.environments.client import EnvironmentManagerClient as EMC

envs_app = typer.Typer(help="Manage qBraid environments.", no_args_is_help=True)


@envs_app.command(name="create")
def envs_create(  # pylint: disable=too-many-statements
    name: str = typer.Option(None, "--name", "-n", help="Name of the environment to create"),
    description: Optional[str] = typer.Option(
        None, "--description", "-d", help="Short description of the environment"
    ),
    file_path: str = typer.Option(
        None, "--file", "-f", help="Path to a .yml file containing the environment details"
    ),
    auto_confirm: bool = typer.Option(
        False, "--yes", "-y", help="Automatically answer 'yes' to all prompts"
    ),
) -> None:
    """Create a new qBraid environment."""
    env_description = description or ""
    if name:
        if not validate_env_name(name):
            handle_error(
                error_type="ValueError",
                include_traceback=False,
                message=f"Invalid environment name '{name}'. ",
            )

    env_details_in_cli = name is not None and env_description != ""
    env_config = None
    if env_details_in_cli and file_path:
        handle_error(
            error_type="ArgumentConflictError",
            include_traceback=False,
            message="Cannot use --file with --name or --description while creating an environment",
        )
    elif not env_details_in_cli and not file_path:
        handle_error(
            error_type="MalformedCommandError",
            include_traceback=False,
            message="Must provide either --name and --description or --file "
            "while creating an environment",
        )
    else:
        try:
            if file_path:
                env_config: EnvironmentConfig = EnvironmentConfig.from_yaml(file_path)
        except ValueError as err:
            handle_error(error_type="YamlValidationError", message=str(err))

    if not name:
        name = env_config.name

    def gather_local_data() -> tuple[Path, str]:
        """Gather local environment data for creation."""
        from qbraid_core.services.environments import get_default_envs_paths

        env_path = get_default_envs_paths()[0]

        result = subprocess.run(
            [sys.executable, "--version"],
            capture_output=True,
            text=True,
            check=True,
        )

        python_version = result.stdout or result.stderr

        return env_path, python_version

    if not env_config:
        env_config = EnvironmentConfig(
            name=name,
            description=env_description,
        )

    # NOTE: create_environment API call will be removed from CLI
    # For now, we generate env_id locally and create environment without API
    from qbraid_core.services.environments.registry import generate_env_id
    
    local_data_out: tuple[Path, str] = run_progress_task(
        gather_local_data,
        description="Solving environment...",
        error_message="Failed to create qBraid environment",
    )

    env_path, python_version = local_data_out

    env_config.python_version = python_version

    # Generate env_id for local environment (slug will be set when published)
    env_id = generate_env_id()
    env_id_path = env_path / env_id
    description = "None" if description == "" else description

    typer.echo("## qBraid Metadata ##\n")
    typer.echo(f"  name: {env_config.name}")
    typer.echo(f"  description: {env_config.description}")
    typer.echo(f"  tags: {env_config.tags}")
    typer.echo(f"  env_id: {env_id}")
    typer.echo(f"  shellPrompt: {env_config.shell_prompt}")
    typer.echo(f"  kernelName: {env_config.kernel_name}")

    typer.echo("\n\n## Environment Plan ##\n")
    typer.echo(f"  location: {env_id_path}")
    typer.echo(f"  version: {python_version}\n")

    user_confirmation = auto_confirm or typer.confirm("Proceed", default=True)
    typer.echo("")
    if not user_confirmation:
        typer.echo("qBraidSystemExit: Exiting.")
        raise typer.Exit()

    run_progress_task(
        create_qbraid_env_assets,
        env_id,
        env_id_path,
        env_config,
        description="Generating qBraid assets...",
        error_message="Failed to create qBraid environment",
    )

    run_progress_task(
        create_venv,
        env_id_path,
        env_config.shell_prompt,
        None,  # python_exe (use default)
        env_id,  # env_id for registry package tracking
        description="Creating virtual environment...",
        error_message="Failed to create qBraid environment",
    )

    console = Console()
    console.print(
        f"[bold green]Successfully created qBraid environment: "
        f"[/bold green][bold magenta]{name}[/bold magenta]\n"
    )
    typer.echo("# To activate this environment, use")
    typer.echo("#")
    typer.echo(f"#     $ qbraid envs activate {name}")
    typer.echo("#")
    typer.echo("# To deactivate an active environment, use")
    typer.echo("#")
    typer.echo("#     $ deactivate")


@envs_app.command(name="remove")
def envs_remove(
    name: str = typer.Option(..., "-n", "--name", help="Name of the environment to remove"),
    auto_confirm: bool = typer.Option(
        False, "--yes", "-y", help="Automatically answer 'yes' to all prompts"
    ),
) -> None:
    """Delete a qBraid environment."""
    import asyncio

    def uninstall_environment(slug: str) -> dict:
        """Uninstall a qBraid environment using async method."""
        from qbraid_core.services.environments.client import EnvironmentManagerClient

        emc = EnvironmentManagerClient()

        # Run async uninstall method
        result = asyncio.run(
            emc.uninstall_environment_local(slug, delete_metadata=True, force=auto_confirm)
        )
        return result

    def gather_local_data(env_name: str) -> tuple[Path, str]:
        """Get environment path and env_id from name or env_id."""
        installed, aliases = installed_envs_data()
        # Try to find by name first, then by env_id
        if env_name in aliases:
            env_id = aliases[env_name]
            path = installed[env_id]
            return path, env_id
        elif env_name in installed:
            # Direct env_id lookup
            path = installed[env_name]
            return path, env_name

        raise QbraidException(
            f"Environment '{name}' not found. "
            "Use name (if unique) or env_id to reference the environment."
        )

    env_path, env_id = gather_local_data(name)

    confirmation_message = (
        f"⚠️  Warning: You are about to delete the environment '{name}' "
        f"located at '{env_path}'.\n"
        "This will remove all local packages and permanently delete all "
        "of its associated qBraid environment metadata.\n"
        "This operation CANNOT be undone.\n\n"
        "Are you sure you want to continue?"
    )

    if auto_confirm or typer.confirm(confirmation_message, abort=True):
        typer.echo("")
        result = run_progress_task(
            uninstall_environment,
            env_id,  # Can be name or env_id - method handles both
            description="Deleting environment...",
            error_message="Failed to delete qBraid environment",
        )

        if result.get('deleted_metadata'):
            typer.echo(f"✅ Environment '{name}' successfully removed (local files and metadata).")
        else:
            typer.echo(f"✅ Environment '{name}' successfully removed (local files only).")


@envs_app.command(name="list")
def envs_list():
    """List installed qBraid environments."""
    from qbraid_core.services.environments.registry import EnvironmentRegistryManager
    
    installed, aliases = installed_envs_data(use_registry=True)
    console = Console()

    if len(installed) == 0:
        console.print(
            "No qBraid environments installed.\n\n"
            + "Use 'qbraid envs create' to create a new environment.",
            style="yellow",
        )
        return

    # Get registry to access name and env_id
    registry_mgr = EnvironmentRegistryManager()

    # Build list of (name, env_id, path) tuples
    env_list = []
    for env_id, path in installed.items():
        try:
            entry = registry_mgr.get_environment(env_id)
            env_list.append((entry.name, env_id, path))
        except Exception:
            # Fallback if registry lookup fails
            # Try to get name from aliases
            name = None
            for alias, eid in aliases.items():
                if eid == env_id and alias != env_id:
                    name = alias
                    break
            if not name:
                name = env_id
            env_list.append((name, env_id, path))

    # Sort: default first, then by name
    sorted_env_list = sorted(
        env_list,
        key=lambda x: (x[0] != "default", str(x[2]).startswith(str(Path.home())), x[0]),
    )

    current_env_path = Path(sys.executable).parent.parent.parent

    # Calculate column widths
    max_name_length = max(len(str(name)) for name, _, _ in sorted_env_list) if sorted_env_list else 0
    max_env_id_length = max(len(str(env_id)) for _, env_id, _ in sorted_env_list) if sorted_env_list else 0
    name_width = max(max_name_length, 4)  # At least "Name"
    env_id_width = max(max_env_id_length, 6)  # At least "Env ID"

    output_lines = []
    output_lines.append("# qbraid environments:")
    output_lines.append("#")
    output_lines.append("")
    
    # Header
    header = f"{'Name'.ljust(name_width + 2)}{'Env ID'.ljust(env_id_width + 2)}Path"
    output_lines.append(header)
    output_lines.append("")

    # Data rows
    for name, env_id, path in sorted_env_list:
        mark = "*" if path == current_env_path else " "
        line = f"{name.ljust(name_width + 2)}{env_id.ljust(env_id_width + 2)}{mark} {path}"
        output_lines.append(line)

    final_output = "\n".join(output_lines)

    console.print(final_output)


@envs_app.command(name="activate")
def envs_activate(
    name: str = typer.Argument(
        ..., help="Name of the environment. Values from 'qbraid envs list'."
    ),
):
    """Activate qBraid environment.

    NOTE: Currently only works on qBraid Lab platform, and select few other OS types.
    """
    from qbraid_core.services.environments.registry import EnvironmentRegistryManager

    # Get environment details from registry by looking up alias
    installed, aliases = installed_envs_data(use_registry=True)
    # Find the env_id from the alias (name or env_id)
    env_id = aliases.get(name)

    if not env_id:
        raise typer.BadParameter(f"Environment '{name}' not found.")

    # Get the environment entry
    registry_mgr = EnvironmentRegistryManager()
    entry = registry_mgr.get_environment(env_id)
    env_path = Path(entry.path)

    # The venv is always at pyenv/ subdirectory
    # (shell_prompt is for the PS1 display name, not the directory)
    venv_path = env_path / "pyenv"

    from .activate import activate_pyvenv

    activate_pyvenv(venv_path)


@envs_app.command(name="available")
def envs_available():
    """List available pre-built environments for installation."""

    def get_available_environments():
        """Get available environments from the API."""
        from qbraid_core.services.environments.client import EnvironmentManagerClient

        emc = EnvironmentManagerClient()
        return emc.get_available_environments()

    try:
        result = run_progress_task(
            get_available_environments,
            description="Fetching available environments...",
            error_message="Failed to fetch available environments",
        )
    except QbraidException:
        # If API fails, show a helpful message
        console = Console()
        console.print(
            "[yellow]Unable to fetch available environments from qBraid service.[/yellow]"
        )
        console.print("This feature requires:")
        console.print("• qBraid Lab environment, or")
        console.print("• Valid qBraid API credentials configured")
        console.print("\nTo configure credentials, run: [bold]qbraid configure[/bold]")
        return

    console = Console()
    environments = result.get("environments", [])

    if not environments:
        console.print("No environments available for installation.")
        return

    # Check if we're on cloud or local
    is_cloud = any(env.get("available_for_installation", False) for env in environments)

    # Display header
    if is_cloud:
        status_text = "[bold green]✓ Available for installation[/bold green]"
    else:
        status_text = "[bold yellow]⚠ Not available (local environment)[/bold yellow]"

    console.print(f"\n# Available qBraid Environments ({status_text})")
    console.print(f"# Total: {len(environments)} environments")
    console.print("#")
    console.print("")

    # Calculate column widths
    max_name_len = max(len(env.get("displayName", env.get("name", ""))) for env in environments)
    max_slug_len = max(len(env.get("slug", "")) for env in environments)
    name_width = min(max_name_len + 2, 30)
    slug_width = min(max_slug_len + 2, 20)

    # Display environments
    for env in environments:
        name = env.get("displayName", env.get("name", "N/A"))
        slug = env.get("slug", "N/A")
        description = env.get("description", "No description")
        available = env.get("available_for_installation", False)

        # Truncate long names/slugs
        if len(name) > 28:
            name = name[:25] + "..."
        if len(slug) > 18:
            slug = slug[:15] + "..."
        if len(description) > 60:
            description = description[:57] + "..."

        status_icon = "✓" if available else "⚠"
        status_color = "green" if available else "yellow"

        console.print(
            f"[{status_color}]{status_icon}[/{status_color}] "
            f"{name.ljust(name_width)} "
            f"[dim]({slug.ljust(slug_width)})[/dim] "
            f"{description}"
        )

    # Show usage hint
    console.print("")
    if is_cloud:
        console.print("[dim]To install an environment, note its slug and use:[/dim]")
        console.print("[dim]  qbraid envs install <slug>[/dim]")
    else:
        console.print("[dim]Environment installation is only available on qBraid Lab.[/dim]")
        console.print("[dim]Create custom environments with: qbraid envs create[/dim]")


@envs_app.command(name="install")
def envs_install(
    env_slug: str = typer.Argument(..., help="Environment slug to install (from 'qbraid envs available')"),
    temp: bool = typer.Option(
        False, "--temp", "-t", 
        help="Install as temporary environment (faster, non-persistent)"
    ),
    target_dir: str = typer.Option(
        None, "--target", help="Custom target directory (defaults to ~/.qbraid/environments or /opt/environments)"
    ),
    yes: bool = typer.Option(
        False, "--yes", "-y",
        help="Automatically overwrite existing environment without prompting"
    ),
):
    """Install a pre-built environment from cloud storage."""
    
    async def install_environment_async():
        """Async wrapper for environment installation."""
        from qbraid_core.services.environments.client import EnvironmentManagerClient
        from pathlib import Path
        
        # Determine target directory
        if target_dir:
            install_dir = target_dir
        elif temp:
            install_dir = "/opt/environments"
        else:
            install_dir = str(Path.home() / ".qbraid" / "environments")
        
        console = Console()
        
        # Check if we're on qBraid Lab for non-temp installs
        emc = EnvironmentManagerClient()
        is_cloud = emc.running_in_lab()
        
        if not temp and not is_cloud:
            console.print("[red]❌ Environment installation requires qBraid Lab or use --temp flag[/red]")
            console.print("💡 Try: [bold]qbraid envs install {env_slug} --temp[/bold]")
            raise typer.Exit(1)
        
        if temp and not is_cloud:
            console.print("[yellow]⚠️  Local temporary install - environment won't persist after restart[/yellow]")
        
        # Install environment
        try:
            console.print(f"🚀 Installing environment: [bold]{env_slug}[/bold]")
            if temp:
                console.print(f"📂 Target: [dim]{install_dir}[/dim] (temporary)")
            else:
                console.print(f"📂 Target: [dim]{install_dir}[/dim] (persistent)")
            console.print("")

            progress_columns = (
                SpinnerColumn(),
                TextColumn("{task.description}"),
                BarColumn(),
                DownloadColumn(),
                TransferSpeedColumn(),
                TimeElapsedColumn(),
            )

            with Progress(*progress_columns, transient=True) as progress:
                tasks: dict[str, int] = {}

                def get_task(stage: str, description: str, total: Optional[int]) -> int:
                    task_id = tasks.get(stage)
                    if task_id is None:
                        task_total = total if total and total > 0 else None
                        task_id = progress.add_task(description, total=task_total)
                        tasks[stage] = task_id
                    return task_id

                def progress_callback(stage: str, completed: int, total: int) -> None:
                    total_value = total if total and total > 0 else None
                    if stage == "download":
                        task_id = get_task("download", "Downloading environment...", total_value)
                        task = progress.tasks[task_id]
                        if total_value and (task.total is None or task.total == 0):
                            progress.update(task_id, total=total_value)
                        progress.update(task_id, completed=completed)
                    elif stage == "extract":
                        task_id = get_task("extract", "Extracting files...", total_value)
                        task = progress.tasks[task_id]
                        if total_value:
                            if task.total is None or task.total == 0:
                                progress.update(task_id, total=total_value)
                            progress.update(task_id, completed=completed)
                        else:
                            progress.update(task_id, completed=task.completed + 1)

                result = await emc.install_environment_from_storage(
                    slug=env_slug,
                    target_dir=install_dir,
                    temp=temp,
                    overwrite=yes,
                    progress_callback=progress_callback,
                )

            console.print("")
            console.print(f"[green]✅ Installation completed![/green]")
            console.print(f"📍 Location: [bold]{result['target_dir']}[/bold]")
            if 'size_mb' in result:
                console.print(f"💾 Size: [dim]{result['size_mb']:.1f} MB[/dim]")
            if 'env_id' in result:
                console.print(f"🆔 Env ID: [dim]{result['env_id']}[/dim]")

            if temp:
                console.print("[yellow]⚠️  Temporary environment - will be deleted on pod restart[/yellow]")

            env_activation_id = result.get("env_id", env_slug)
            console.print("")
            console.print("🎯 Next steps:")
            console.print(f"• Activate: [bold]qbraid envs activate {env_activation_id}[/bold]")
            console.print(f"• List all: [bold]qbraid envs list[/bold]")

        except Exception as e:
            if isinstance(e, EnvironmentValidationError) and "already exists" in str(e):
                console.print("[yellow]⚠️ Installation skipped: Environment already exists.[/yellow]")
            else:
                console.print(f"[red]❌ Installation failed: {e}[/red]")
            raise typer.Exit(1)
    # Run async function
    import asyncio
    try:
        asyncio.run(install_environment_async())
    except KeyboardInterrupt:
        console = Console()
        console.print("\n[yellow]⚠️  Installation cancelled by user[/yellow]")
        raise typer.Exit(1)


@envs_app.command(name="publish")
def envs_publish(
    slug: str = typer.Argument(..., help="Environment slug identifier"),
    path: Optional[Path] = typer.Option(
        None,
        "--path",
        "-p",
        help="Path to environment directory (default: lookup from registry)"
    ),
    overwrite: bool = typer.Option(
        False,
        "--overwrite",
        "-o",
        help="Overwrite existing published environment"
    ),
):
    """
    Publish environment to qBraid cloud storage for global distribution.

    This command packages and uploads your environment to make it available
    for installation by other users via 'qbraid envs install'.

    Examples:
        $ qbraid envs publish my_custom_env
        $ qbraid envs publish my_env --path ~/my_environment
        $ qbraid envs publish my_env --overwrite
    """
    from rich.console import Console
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
    from qbraid_core.services.environments.client import EnvironmentManagerClient
    from qbraid_core.services.environments.registry import EnvironmentRegistryManager

    console = Console()

    # Determine environment path
    if path:
        env_path = path.expanduser().resolve()
        if not env_path.exists():
            console.print(f"[red]❌ Error:[/red] Path does not exist: {env_path}")
            raise typer.Exit(1)
    else:
        # Look up from registry by slug
        try:
            registry_mgr = EnvironmentRegistryManager()
            found = registry_mgr.find_by_slug(slug)
            if not found:
                console.print(f"[red]❌ Error:[/red] Environment with slug '{slug}' not found in registry")
                console.print("\n[yellow]💡 Tip:[/yellow] Use --path to specify environment directory manually.")
                raise typer.Exit(1)
            env_id, env = found
            env_path = Path(env.path)
        except Exception as err:
            console.print(f"[red]❌ Error:[/red] Failed to locate environment: {err}")
            console.print("\n[yellow]💡 Tip:[/yellow] Use --path to specify environment directory manually.")
            raise typer.Exit(1)

    console.print(f"🚀 Publishing environment: [bold]{slug}[/bold]")
    console.print(f"📂 Source: {env_path}\n")

    # Define async function
    async def publish_environment_async():
        """Async wrapper for environment publishing."""
        client = EnvironmentManagerClient()

        # Progress tracking
        stages = {"archive": False, "upload": False}

        def progress_callback(stage: str, completed: int, total: int):
            """Track progress across stages."""
            stages[stage] = True

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=console,
        ) as progress:
            # Add tasks
            archive_task = progress.add_task("📦 Creating archive...", total=100)
            upload_task = progress.add_task("☁️  Uploading to cloud...", total=100)

            try:
                # TODO: Update this when env_share_publish branch is merged
                # This will use remote_publish_environment and handle directory renaming
                raise NotImplementedError(
                    "Publish command will be updated when env_share_publish branch is merged. "
                    "It will use remote_publish_environment to get slug from API, "
                    "rename directory from env_id to slug, update paths, and upload."
                )
                # result = await client.publish_environment(
                #     slug=slug,
                #     env_path=str(env_path),
                #     overwrite=overwrite,
                #     progress_callback=progress_callback
                # )

                # Update progress bars
                if stages.get("archive"):
                    progress.update(archive_task, completed=100)
                if stages.get("upload"):
                    progress.update(upload_task, completed=100)

                return result

            except Exception as err:
                raise err

    # Run async function
    import asyncio
    try:
        result = asyncio.run(publish_environment_async())

        console.print(f"\n[green]✅ Published successfully![/green]")
        console.print(f"📍 Bucket: {result.get('bucket', 'N/A')}")
        console.print(f"📄 Path: {result.get('path', 'N/A')}")
        console.print(f"\n🎯 Users can now install with:")
        console.print(f"   [bold cyan]qbraid envs install {slug}[/bold cyan]")

    except KeyboardInterrupt:
        console.print("\n[yellow]⚠️  Publishing cancelled by user[/yellow]")
        raise typer.Exit(1)
    except Exception as err:
        console.print(f"\n[red]❌ Publishing failed:[/red] {err}")
        raise typer.Exit(1)


@envs_app.command(name="add-path")
def envs_add_path(
    path: Path = typer.Argument(..., exists=True, dir_okay=True, file_okay=False),
    alias: Optional[str] = typer.Option(None, "--alias", "-a", help="Alias for the environment"),
    name: Optional[str] = typer.Option(None, "--name", "-n", help="Name/slug for the environment"),
    auto_confirm: bool = typer.Option(False, "--yes", "-y"),
):
    """
    Register an external Python environment with qBraid.

    This allows you to use existing Python environments (conda, venv, etc.)
    with qBraid commands like kernel management and activation.

    Examples:
        $ qbraid envs add-path /path/to/my_env --alias myenv
        $ qbraid envs add-path ~/conda/envs/quantum --name quantum_abc123
    """
    from qbraid_core.services.environments.client import EnvironmentManagerClient

    def register():
        emc = EnvironmentManagerClient()
        result = emc.register_external_environment(
            path=path,
            name=alias or name or path.name,
        )
        return result

    # Get info first to show user
    try:
        emc = EnvironmentManagerClient()
        # Do a dry run to validate and get info
        from qbraid_core.system.executables import is_valid_python

        python_candidates = [
            path / "bin" / "python",
            path / "bin" / "python3",
            path / "Scripts" / "python.exe",
        ]

        python_path = None
        for candidate in python_candidates:
            if is_valid_python(candidate):
                python_path = candidate
                break

        if not python_path:
            handle_error(
                error_type="ValidationError",
                message=f"No valid Python executable found in {path}"
            )
            return

        # Confirm with user
        if not auto_confirm:
            console = Console()
            console.print("\n[bold]📦 Registering external environment:[/bold]")
            console.print(f"   Path: {path}")
            console.print(f"   Name: {alias or name or path.name}")
            console.print(f"   Python: {python_path}")

            if not typer.confirm("\nProceed with registration?"):
                typer.echo("❌ Registration cancelled.")
                return

        result = run_progress_task(
            register,
            description="Registering environment...",
            error_message="Failed to register environment"
        )

        typer.echo(f"\n✅ Environment '{result['name']}' registered successfully!")
        typer.echo(f"   Env ID: {result['env_id']}")
        typer.echo(f"\nYou can now:")
        typer.echo(f"   - Add kernel: qbraid kernels add {result['name']}")
        typer.echo(f"   - View in list: qbraid envs list")

    except Exception as e:
        handle_error(message=str(e))


@envs_app.command(name="remove-path")
def envs_remove_path(
    name: str = typer.Argument(..., help="Name or alias of environment to unregister"),
    auto_confirm: bool = typer.Option(False, "--yes", "-y"),
):
    """
    Unregister an external environment from qBraid.

    This only removes the environment from qBraid's registry.
    The actual environment files are NOT deleted.
    """
    from qbraid_core.services.environments.client import EnvironmentManagerClient

    def unregister(slug: str):
        emc = EnvironmentManagerClient()
        result = emc.unregister_external_environment(slug)
        return result

    # Find environment
    try:
        from qbraid_core.services.environments.registry import EnvironmentRegistryManager

        registry_mgr = EnvironmentRegistryManager()
        # Try to find by name first, then by env_id
        found = registry_mgr.find_by_name(name)
        if not found:
            found = registry_mgr.find_by_env_id(name)

        if not found:
            handle_error(
                error_type="NotFoundError",
                message=f"Environment '{name}' not found in registry. "
                "Use name (if unique) or env_id to reference the environment."
            )
            return

        env_id, entry = found

        if entry.type != "external":
            console = Console()
            console.print(f"[yellow]⚠️  Warning: '{name}' is a qBraid-managed environment.[/yellow]")
            console.print(f"   Use 'qbraid envs remove --name {name}' to fully remove it.")
            return

        if not auto_confirm:
            console = Console()
            console.print(f"\n[yellow]⚠️  Unregistering environment '{entry.name}'[/yellow]")
            console.print(f"   Env ID: {env_id}")
            console.print(f"   Path: {entry.path}")
            console.print(f"   Type: {entry.type}")
            console.print(f"\n   Note: Files at {entry.path} will NOT be deleted.")

            if not typer.confirm("\nProceed?"):
                typer.echo("❌ Unregistration cancelled.")
                return

        result = run_progress_task(
            unregister,
            env_id,  # Can be name or env_id - method handles both
            description="Unregistering environment...",
            error_message="Failed to unregister environment"
        )

        typer.echo(f"✅ Environment '{name}' unregistered from qBraid.")

    except Exception as e:
        handle_error(message=str(e))


@envs_app.command(name="sync")
def envs_sync():
    """
    Synchronize environment registry with filesystem.

    This will:
    - Remove registry entries for deleted environments
    - Auto-discover new environments in default paths
    - Verify all registered paths still exist
    """
    from qbraid_core.services.environments.client import EnvironmentManagerClient

    def sync():
        emc = EnvironmentManagerClient()
        stats = emc.sync_registry()
        return stats

    result = run_progress_task(
        sync,
        description="Synchronizing environment registry...",
        error_message="Failed to sync registry"
    )

    console = Console()

    if result["discovered"] > 0:
        console.print(f"[green]✅ Registry synced: {result['discovered']} new environment(s) discovered[/green]")
    elif result["removed"] > 0:
        console.print(f"[green]✅ Registry synced: {result['removed']} invalid entry(ies) removed[/green]")
    else:
        console.print("[green]✅ Registry synced: No changes detected[/green]")

    # Show summary
    console.print(f"\n[bold]Summary:[/bold]")
    console.print(f"   Verified: {result['verified']}")
    console.print(f"   Discovered: {result['discovered']}")
    console.print(f"   Removed: {result['removed']}")


if __name__ == "__main__":
    envs_app()
